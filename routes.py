from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    send_from_directory,
    session,
    url_for,
    request,
)
import os
import subprocess
import shutil


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

@pages.context_processor
def get_folder_list():
    def folder_list() -> list:
        files = subprocess.check_output('ls', shell=True).decode('utf-8').split('\n')
        directories = [d for d in files if os.path.isdir(d)]
        return directories
    return {"folder_list": folder_list}

@pages.context_processor
def call_get_images():
    def get_images(curr_folder) -> list:
        images = []
        files = os.listdir(curr_folder)
        for file in files:
            if os.path.splitext(file)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                images.append(file)
        return images
    
    return {"get_images": get_images}


@pages.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        for key, f in request.files.items():
            if key.startswith('file'):
                file_name = os.path.join(current_app.config['UPLOAD_DIRECTORY'], f.filename)
                f.save(file_name)
    
    return redirect('/')


@pages.route('/')
def index():
  curr_folder = current_app.config['UPLOAD_DIRECTORY']

  # pass current directory, and folder list to HTML page
  return render_template('index.html', current_folder=curr_folder)


@pages.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
  return send_from_directory(current_app.config['UPLOAD_DIRECTORY'], filename)

# handle 'cd' command
@pages.route('/cd')
def cd():
    # change directory to path passed from request
    os.chdir(request.args.get('path'))
    # change upload folder to current directory.
    current_app.config['UPLOAD_DIRECTORY'] = os.getcwd()
    
    # redirect to file manager
    return redirect('/')

# handle 'make directory' command
@pages.route('/md')
def md():
    # create new folder

    folder = request.args.get('folder')
    if folder:
        os.mkdir(folder)
    
    # redirect to fole manager
    return redirect('/')

# handle 'remove directory' command
@pages.route('/rm')
def rm():
    # remove certain directory
    shutil.rmtree(os.getcwd() + '/' + request.args.get('dir'))
    
    # redirect to fole manager
    return redirect('/')
    
# view text files
@pages.route('/view')
def view():
    # get the file content
    with open(request.args.get('file')) as f:
        return f.read().replace('\n', '<br>')













