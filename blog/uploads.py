from django.core.files.uploadhandler import FileUploadHandler, SkipFile

from .images import MAX_UPLOAD_BYTES


class SizeLimitUploadHandler(FileUploadHandler):
    """Descarta un archivo en cuanto supera el límite, sin llegar a guardarlo entero.

    Deja `request.upload_too_large = True` para que la vista pueda explicarlo.
    """

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.received = 0

    def receive_data_chunk(self, raw_data, start):
        self.received += len(raw_data)
        if self.received > MAX_UPLOAD_BYTES:
            self.request.upload_too_large = True
            raise SkipFile
        return raw_data

    def file_complete(self, file_size):
        return None
