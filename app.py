from flask import Flask, render_template, redirect, request, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone
import os
import subprocess
import shutil

app = Flask(__name__)
# app.config['UPLOAD_DIRECTORY'] = 'uploads/'
app.config['UPLOAD_DIRECTORY'] = '/Users/macc/Pictures/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_MAX_FILE_SIZE'] = 3
app.config['DROPZONE_MAX_FILES'] = 30

dropzone = Dropzone(app)

def current_folder_files() -> list:
    files = subprocess.check_output('ls', shell=True).decode('utf-8').split('\n')
    directories = [d for d in files if os.path.isdir(d)]
    return directories

@app.context_processor
def call_get_images():
    def get_images(curr_folder) -> list:
        images = []
        files = os.listdir(curr_folder)
        for file in files:
            if os.path.splitext(file)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
                images.append(file)
        print(images)
        return images
    
    print("ran image maker")
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
  
  # get images to display
  # images = get_images(files)
  # get just the folders
  folders_list = current_folder_files()
  # pass images, current directory, and folder list to HTML page
  return render_template('index.html', current_folder=curr_folder, file_list=folders_list)


@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
  return send_from_directory(app.config['UPLOAD_DIRECTORY'], filename)

# handle 'cd' command
@app.route('/cd')
def cd():
    # run 'level up' command
    os.chdir(request.args.get('path'))
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

# handle 'make directory' command
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
