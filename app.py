from flask import Flask, render_template, redirect, request, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone
import os
import subprocess
import shutil

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = os.getcwd()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_MAX_FILE_SIZE'] = 3
app.config['DROPZONE_MAX_FILES'] = 30

dropzone = Dropzone(app)

@app.context_processor
def get_folder_list():
    def folder_list() -> list:
        files = subprocess.check_output('ls', shell=True).decode('utf-8').split('\n')
        directories = [d for d in files if os.path.isdir(d)]
        return directories
    return {"folder_list": folder_list}

@app.context_processor
def call_get_images():
    def get_images(curr_folder) -> list:
        images = []
        files = os.listdir(curr_folder)
        for file in files:
            if os.path.splitext(file)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
                images.append(file)
        return images
    
    return {"get_images": get_images}


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        for key, f in request.files.items():
            if key.startswith('file'):
                file_name = os.path.join(app.config['UPLOAD_DIRECTORY'], f.filename)
                f.save(file_name)
    
    return redirect('/')


@app.route('/')
def index():
  curr_folder = app.config['UPLOAD_DIRECTORY']

  # pass current directory, and folder list to HTML page
  return render_template('index.html', current_folder=curr_folder)


@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
  return send_from_directory(app.config['UPLOAD_DIRECTORY'], filename)

# handle 'cd' command
@app.route('/cd')
def cd():
    # change directory to path passed from request
    os.chdir(request.args.get('path'))
    # change upload folder to current directory.
    app.config['UPLOAD_DIRECTORY'] = os.getcwd()
    
    # redirect to file manager
    return redirect('/')

# handle 'make directory' command
@app.route('/md')
def md():
    # create new folder
    os.mkdir(request.args.get('folder'))
    
    # redirect to fole manager
    return redirect('/')

# handle 'remove directory' command
@app.route('/rm')
def rm():
    # remove certain directory
    shutil.rmtree(os.getcwd() + '/' + request.args.get('dir'))
    
    # redirect to fole manager
    return redirect('/')
    
# view text files
@app.route('/view')
def view():
    # get the file content
    with open(request.args.get('file')) as f:
        return f.read().replace('\n', '<br>')
