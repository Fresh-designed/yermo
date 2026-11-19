"""Videos de los cursos en un bucket privado de Backblaze B2, a través de su API compatible con S3.

La base de datos guarda la dirección de cada archivo: `https://<bucket>.<endpoint>/<clave>`, o
`https://<endpoint>/<bucket>/<clave>` si el nombre del bucket lleva mayúsculas o puntos, que no
caben en un nombre de dominio. Como el bucket es privado, esa dirección no se abre tal cual:
`signed_url` la convierte en un enlace temporal firmado, que solo recibe quien abre la lección.
"""
import re
from functools import lru_cache
from urllib.parse import quote, unquote, urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Lo que dura un enlace firmado: de sobra para ver una lección con pausas.
LINK_SECONDS = 6 * 60 * 60

DNS_BUCKET = re.compile(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]")


def endpoint_host():
    return settings.B2_ENDPOINT.strip().removeprefix("https://").removeprefix("http://").strip("/")


def is_configured():
    return all(
        (settings.B2_KEY_ID, settings.B2_APPLICATION_KEY, settings.B2_BUCKET, settings.B2_ENDPOINT)
    )


def _virtual_host():
    """True si el bucket puede ir en el dominio (`bucket.endpoint`); si no, va en la ruta."""
    return bool(DNS_BUCKET.fullmatch(settings.B2_BUCKET))


def public_url(key):
    """Dirección que se guarda en la base de datos para el archivo `key` del bucket."""
    if not settings.B2_BUCKET or not settings.B2_ENDPOINT:
        raise ImproperlyConfigured("Define B2_BUCKET y B2_ENDPOINT en el archivo .env.")
    if _virtual_host():
        return f"https://{settings.B2_BUCKET}.{endpoint_host()}/{quote(key)}"
    return f"https://{endpoint_host()}/{settings.B2_BUCKET}/{quote(key)}"


def key_from_url(url):
    """Clave del archivo si `url` apunta al bucket configurado; si no, None."""
    if not url or not settings.B2_BUCKET or not settings.B2_ENDPOINT:
        return None
    parsed = urlparse(url)
    host, bucket = endpoint_host().lower(), settings.B2_BUCKET
    if parsed.netloc.lower() == f"{bucket}.{host}".lower():
        key = parsed.path[1:]
    elif parsed.netloc.lower() == host and parsed.path.startswith(f"/{bucket}/"):
        key = parsed.path[len(bucket) + 2 :]
    else:
        return None
    return unquote(key) or None


def signed_url(url):
    """Enlace temporal para reproducir `url`. Las direcciones que no son del bucket no cambian."""
    key = key_from_url(url)
    if key is None or not is_configured():
        return url
    return client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.B2_BUCKET, "Key": key},
        ExpiresIn=LINK_SECONDS,
    )


def client():
    if not is_configured():
        raise ImproperlyConfigured(
            "Faltan datos de Backblaze B2. Define B2_KEY_ID, B2_APPLICATION_KEY, "
            "B2_BUCKET y B2_ENDPOINT en el archivo .env."
        )
    style = "virtual" if _virtual_host() else "path"
    return _client(settings.B2_KEY_ID, settings.B2_APPLICATION_KEY, endpoint_host(), style)


@lru_cache(maxsize=4)
def _client(key_id, application_key, host, addressing_style):
    # boto3 solo hace falta si hay videos en B2, así que se importa aquí.
    import boto3
    from botocore.config import Config

    # s3.us-east-005.backblazeb2.com → us-east-005, que entra en la firma de cada enlace.
    parts = host.split(".")
    if len(parts) < 4 or parts[0] != "s3" or not host.endswith(".backblazeb2.com"):
        raise ImproperlyConfigured(
            "B2_ENDPOINT debe ser el «Endpoint» del bucket, por ejemplo s3.us-east-005.backblazeb2.com."
        )
    return boto3.client(
        "s3",
        endpoint_url=f"https://{host}",
        region_name=parts[1],
        aws_access_key_id=key_id,
        aws_secret_access_key=application_key,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": addressing_style},
            # B2 rechaza las cabeceras de checksum que boto3 añade por defecto desde la 1.36.
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
            retries={"max_attempts": 6, "mode": "standard"},
        ),
    )
