from app.config import config


def allowed_file(filename):
    """Checking the downloaded file for a valid extension"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in config['APP']['ALLOWED_FILE_TO_PREVIEW']
