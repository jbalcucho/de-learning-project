import os
import config
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContentSettings


def get_blob_service_client_sas(sas_token: str, account_name: str) -> BlobServiceClient:
    """
    Devuelve un cliente de Blob Storage autenticado con SAS.

    Args:
        sas_token: El token SAS
        account_name: Nombre de la Storage Account en Azure.

    Returns:
        BlobServiceClient autenticado con SAS.
    """
    account_url = f"https://{account_name}.blob.core.windows.net"
    blob_service_client = BlobServiceClient(account_url, credential=sas_token)
    return blob_service_client


def upload_directory(
    local_dir: Path,
    account_name: str,
    sas_token: str,
    container_name: str,
    prefix: str = "",
) -> None:
    """
    Sube una carpeta completa a Azure Blob Storage preservando la estructura.
    """
    account_url = f"https://{account_name}.blob.core.windows.net"
    bsc = BlobServiceClient(account_url, credential=sas_token)
    container_client = bsc.get_container_client(container_name)

    for file_path in local_dir.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(local_dir).as_posix()
            blob_name = f"{prefix}/{relative_path}" if prefix else relative_path

            settings = ContentSettings(content_type="application/octet-stream")
            print(f"Subiendo {file_path} --> {blob_name}")
            with open(file_path, "rb") as f:
                container_client.upload_blob(
                    name=blob_name, data=f, overwrite=True, content_settings=settings
                )

    print("Todos los archivos subidos correctamente.")


if __name__ == "__main__":

    load_dotenv()

    ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    SAS_TOKEN = os.getenv("AZURE_STORAGE_SAS")
    CONTAINER = os.getenv("DATA_CONTAINER")

    if ACCOUNT_NAME and SAS_TOKEN and CONTAINER:
        bsc = get_blob_service_client_sas(SAS_TOKEN, ACCOUNT_NAME)
    else:
        raise ValueError("Credentials not found")

    upload_directory(config.DATA_DIR, ACCOUNT_NAME, SAS_TOKEN, CONTAINER)
