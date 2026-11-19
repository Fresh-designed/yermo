"""Validación y normalización de las fotos del blog."""
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 40_000_000
MAX_SIDE = 1600
FORMATS = ("JPEG", "PNG", "WEBP")


class InvalidImage(ValueError):
    pass


def normalize_image(uploaded):
    """Devuelve `(bytes, ancho, alto)` de un JPEG nuevo hecho a partir del archivo subido.

    Volver a codificar la imagen garantiza que lo guardado es una foto de verdad,
    quita sus metadatos (incluida la ubicación) y limita su tamaño.
    """
    try:
        image = Image.open(uploaded, formats=FORMATS)
        if image.width * image.height > MAX_PIXELS:
            raise InvalidImage("La foto tiene demasiados píxeles. Redúcela e inténtalo de nuevo.")
        image = ImageOps.exif_transpose(image)
        if image.mode in ("RGBA", "LA", "PA") or "transparency" in image.info:
            image = image.convert("RGBA")
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")
        image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
        output = BytesIO()
        image.save(output, "JPEG", quality=84, optimize=True)
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as error:
        if isinstance(error, InvalidImage):
            raise
        raise InvalidImage("Ese archivo no es una foto JPG, PNG o WebP válida.") from error
    return output.getvalue(), image.width, image.height
