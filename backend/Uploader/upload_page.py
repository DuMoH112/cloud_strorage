import os
from time import time

from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict

from app.models import UploadForm

cloud_drive_bp = Blueprint('cloud_drive', __name__)


@cloud_drive_bp.route('/drive', methods=['GET', 'POST'])
def cloud_drive():
    """Cloud drive Page"""
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file_.data
        filename = secure_filename(file.filename)

        path = os.path.join("app/static/files/" + filename.split('.')[0])


        os.makedirs(path, exist_ok=True)

        tic = time()

        file.save(os.path.join(path, filename))
        
        del file
        path = '/app/backend/app/static/files/' + filename.split('.')[0]


        form.path = '/static/files/{}/'.format(filename.split('.')[0])
        form.time_seconds = '{:.4f}'.format(time() - tic)

    return render_template('upload_page.html', form=form)