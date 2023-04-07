from flask import Blueprint

download_bp = Blueprint('download', __name__)

@download_bp.route('/topics')
def download_topics():
    return 'Blog Topics'

@download_bp.route('/editor')
def download_editor():
    return 'Blog Editor'

@download_bp.route('/date')
def download_date():
    return 'Blog Date'