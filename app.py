from flask import Flask
from flask_dropzone import Dropzone
from dotenv import load_dotenv
from routes import pages
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pages)
    app.config['UPLOAD_DIRECTORY'] = os.getcwd()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
    app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
    app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
    app.config['DROPZONE_MAX_FILE_SIZE'] = 3
    app.config['DROPZONE_MAX_FILES'] = 30

    dropzone = Dropzone(app)

    return app

