from __future__ import annotations

import os
import io
import csv
import json
import logging
import psycopg
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

from config import (
    LINKS_RAW_DIR,
    MOVIES_CLEANED_DIR,
    UNIQUE_GENRES_DIR,
    RATINGS_RAW_DIR,
    TAGS_RAW_DIR,
)


def connect() -> psycopg.Connection:
    load_dotenv()
    missing = [
        k for k in ("PG_HOST", "PG_DB", "PG_USER", "PG_PASSWORD") if not os.getenv(k)
    ]
    if missing:
        raise EnvironmentError(f"Faltan variables en .env: {missing}")
    return psycopg.connect(
        host=os.environ["PG_HOST"],
        dbname=os.environ["PG_DB"],
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        sslmode=os.environ.get("PG_REQUIRE_SSL", "require"),
    )


def copy_csv(cur: psycopg.Cursor, copy_sql: str, buf: io.StringIO) -> None:
    buf.seek(0)
    with cur.copy(copy_sql) as cp:
        cp.write(buf.getvalue())


def to_ts_utc(epoch_seconds: str) -> str:
    dt = datetime.fromtimestamp(int(float(epoch_seconds)), tz=timezone.utc)
    return dt.isoformat()


def read_unique_genres(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de géneros: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def load_genres(conn: psycopg.Connection, genres: list[str]) -> dict[str, int]:
    if not genres:
        raise ValueError("La lista de géneros está vacía.")

    buf = io.StringIO()
    writer = csv.writer(buf)
    for g in genres:
        writer.writerow([g])

    with conn.cursor() as cur:
        cur.execute("CREATE TEMP TABLE _tmp_genre(name TEXT);")
        copy_csv(cur, "COPY _tmp_genre(name) FROM STDIN WITH (FORMAT csv)", buf)
        cur.execute(
            """
            INSERT INTO public.genre(name)
            SELECT DISTINCT name FROM _tmp_genre
            ON CONFLICT (name) DO NOTHING;
        """
        )
        cur.execute("SELECT genre_id, name FROM public.genre;")
        mapping = {name: gid for gid, name in cur.fetchall()}
    return mapping


def load_movies(
    conn: psycopg.Connection, movies_json: Path, genre_map: dict[str, int]
) -> None:
    if not movies_json.exists():
        raise FileNotFoundError(f"No existe: {movies_json}")

    with open(movies_json, "r", encoding="utf-8") as fh:
        movies = json.load(fh)

    buf_movies = io.StringIO()
    w_m = csv.writer(buf_movies)
    for m in movies:
        w_m.writerow([m["movieId"], m.get("title"), m.get("year")])

    buf_bridge = io.StringIO()
    w_b = csv.writer(buf_bridge)
    for m in movies:
        mid = m["movieId"]
        for g in m.get("genres", []):
            gid = genre_map.get(g)
            if gid:
                w_b.writerow([mid, gid])

    with conn.cursor() as cur:
        cur.execute("CREATE TEMP TABLE _tmp_movie(movie_id INT, title TEXT, year INT);")
        copy_csv(
            cur,
            "COPY _tmp_movie(movie_id, title, year) FROM STDIN WITH (FORMAT csv)",
            buf_movies,
        )
        cur.execute(
            """
            INSERT INTO public.movie(movie_id, title, year)
            SELECT movie_id, title, year FROM _tmp_movie
            ON CONFLICT (movie_id) DO UPDATE
              SET title = EXCLUDED.title,
                  year  = EXCLUDED.year;
        """
        )

        cur.execute("CREATE TEMP TABLE _tmp_bridge(movie_id INT, genre_id INT);")
        copy_csv(
            cur,
            "COPY _tmp_bridge(movie_id, genre_id) FROM STDIN WITH (FORMAT csv)",
            buf_bridge,
        )
        cur.execute(
            """
            INSERT INTO public.movie_genre(movie_id, genre_id)
            SELECT DISTINCT movie_id, genre_id FROM _tmp_bridge
            ON CONFLICT DO NOTHING;
        """
        )


def load_links(conn: psycopg.Connection, links_csv: Path) -> None:
    if not links_csv.exists():
        logging.warning("No existe links.csv en: %s (se omite)", links_csv)
        return

    with open(links_csv, "r", encoding="utf-8") as fh:
        data = fh.read()
    buf = io.StringIO(data)

    with conn.cursor() as cur:
        cur.execute(
            "CREATE TEMP TABLE _tmp_link(movie_id INT, imdb_id TEXT, tmdb_id TEXT);"
        )
        copy_csv(
            cur,
            "COPY _tmp_link(movie_id, imdb_id, tmdb_id) FROM STDIN WITH (FORMAT csv, HEADER true)",
            buf,
        )
        cur.execute(
            """
            INSERT INTO public.link(movie_id, imdb_id, tmdb_id)
            SELECT movie_id, NULLIF(imdb_id,''), NULLIF(tmdb_id,'') FROM _tmp_link
            ON CONFLICT (movie_id) DO UPDATE
              SET imdb_id = COALESCE(EXCLUDED.imdb_id, link.imdb_id),
                  tmdb_id = COALESCE(EXCLUDED.tmdb_id, link.tmdb_id);
        """
        )


def load_ratings(conn: psycopg.Connection, ratings_csv: Path) -> None:
    if not ratings_csv.exists():
        logging.warning("No existe ratings.csv en: %s (se omite)", ratings_csv)
        return

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["user_id", "movie_id", "rating", "rated_at"])

    with open(ratings_csv, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            w.writerow(
                [r["userId"], r["movieId"], r["rating"], to_ts_utc(r["timestamp"])]
            )
    buf.seek(0)

    with conn.cursor() as cur:
        copy_csv(
            cur,
            "COPY public.rating(user_id, movie_id, rating, rated_at) FROM STDIN WITH (FORMAT csv, HEADER true)",
            buf,
        )


def load_tags(conn: psycopg.Connection, tags_csv: Path) -> None:
    if not tags_csv.exists():
        logging.warning("No existe tags.csv en: %s (se omite)", tags_csv)
        return

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["user_id", "movie_id", "tag", "tagged_at"])

    with open(tags_csv, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames:
            mid_key = "movieId" if "movieId" in reader.fieldnames else "MovieId"
        else:
            raise ValueError()
        for r in reader:
            w.writerow([r["userId"], r[mid_key], r["tag"], to_ts_utc(r["timestamp"])])
    buf.seek(0)

    with conn.cursor() as cur:
        copy_csv(
            cur,
            "COPY public.tag(user_id, movie_id, tag, tagged_at) FROM STDIN WITH (FORMAT csv, HEADER true)",
            buf,
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    # Validación mínima
    required = [MOVIES_CLEANED_DIR, UNIQUE_GENRES_DIR]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Faltan archivos requeridos: {missing}")

    conn = connect()
    try:
        logging.info("→ Cargando géneros (catálogo)")
        genres = read_unique_genres(UNIQUE_GENRES_DIR)
        genre_map = load_genres(conn, genres)
        conn.commit()

        logging.info("→ Cargando películas y relación con géneros")
        load_movies(conn, MOVIES_CLEANED_DIR, genre_map)
        conn.commit()

        logging.info("→ Cargando links")
        load_links(conn, LINKS_RAW_DIR)
        conn.commit()

        logging.info("→ Cargando ratings")
        load_ratings(conn, RATINGS_RAW_DIR)
        conn.commit()

        logging.info("→ Cargando tags")
        load_tags(conn, TAGS_RAW_DIR)
        conn.commit()

        logging.info("Carga completada con éxito.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
