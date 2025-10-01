CREATE SCHEMA IF NOT EXISTS public;

-- 1) Catálogo: género
CREATE TABLE IF NOT EXISTS public.genre (
  genre_id   SERIAL PRIMARY KEY,
  name       TEXT UNIQUE NOT NULL
);

-- 2) Catálogo: película
CREATE TABLE IF NOT EXISTS public.movie (
  movie_id   INTEGER PRIMARY KEY,
  title      TEXT NOT NULL,
  year       INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3) Relación N:M película–género
CREATE TABLE IF NOT EXISTS public.movie_genre (
  movie_id INTEGER NOT NULL REFERENCES public.movie(movie_id) ON DELETE CASCADE,
  genre_id INTEGER NOT NULL REFERENCES public.genre(genre_id) ON DELETE RESTRICT,
  PRIMARY KEY (movie_id, genre_id)
);

-- 4) IDs externos
CREATE TABLE IF NOT EXISTS public.link (
  movie_id INTEGER PRIMARY KEY REFERENCES public.movie(movie_id) ON DELETE CASCADE,
  imdb_id  TEXT,
  tmdb_id  TEXT
);

-- 5) Calificaciones
CREATE TABLE IF NOT EXISTS public.rating (
  user_id    INTEGER NOT NULL,
  movie_id   INTEGER NOT NULL REFERENCES public.movie(movie_id) ON DELETE CASCADE,
  rating     NUMERIC(2,1) NOT NULL CHECK (rating >= 0 AND rating <= 5),
  rated_at   TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (user_id, movie_id, rated_at)
);

-- 6) Etiquetas
CREATE TABLE IF NOT EXISTS public.tag (
  user_id    INTEGER NOT NULL,
  movie_id   INTEGER NOT NULL REFERENCES public.movie(movie_id) ON DELETE CASCADE,
  tag        TEXT NOT NULL,
  tagged_at  TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (user_id, movie_id, tag, tagged_at)
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_rating_movie ON public.rating(movie_id);
CREATE INDEX IF NOT EXISTS idx_rating_user  ON public.rating(user_id);
CREATE INDEX IF NOT EXISTS idx_tag_movie    ON public.tag(movie_id);
CREATE INDEX IF NOT EXISTS idx_tag_user     ON public.tag(user_id);
