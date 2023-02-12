from flask import Flask, render_template, redirect, request, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
import os
import subprocess
import shutil

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
app.config['ALLOWED_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']

def current_folder_files() -> list:
    files = subprocess.check_output('ls', shell=True).decode('utf-8').split('\n')
    directories = [d for d in files if os.path.isdir(d)]
    return directories
     
def get_images(files) -> list:
    images = []
    for file in files:
      if os.path.splitext(file)[1].lower() in app.config['ALLOWED_EXTENSIONS']:
        images.append(file)
    return images


@app.route('/')
def index():
  curr_folder = app.config['UPLOAD_DIRECTORY']
  files = os.listdir(curr_folder)
  # get images to display
  images = get_images(files)
  # get just the folders
  folders_list = current_folder_files()
  # pass images, current directory, and folder list to HTML page
  return render_template('index.html', images=images, current_working_directory=curr_folder, file_list=folders_list)

@app.route('/upload', methods=['POST'])
def upload():
  try:
    file = request.files['file']

    if file:
      extension = os.path.splitext(file.filename)[1].lower()

      if extension not in app.config['ALLOWED_EXTENSIONS']:
        return 'File is not an image.'
        
      file.save(os.path.join(
        app.config['UPLOAD_DIRECTORY'],
        secure_filename(file.filename)
      ))
  
  except RequestEntityTooLarge:
    return 'File is larger than the 16MB limit.'
  
  return redirect('/')

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
