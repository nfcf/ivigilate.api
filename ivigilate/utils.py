import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def get_file_extension(file_name, decoded_file):
    import imghdr

    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension

    return extension