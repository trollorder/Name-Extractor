from flask import Flask , render_template , send_file, request
from flask_bootstrap import Bootstrap
from flask_cors import CORS , cross_origin
from models import name_extractor  #
import os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'temp'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
file_path= None
new_file_path=None

@app.route('/' , methods=['POST', 'GET']) 
@cross_origin()
def home(): 
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/downloadtemplate')
def downloadtemplate():
    try:
        template_path = "static/template.xlsx"
        return send_file(template_path, as_attachment=True)
    except Exception as e:
        return str(e), 500  # Return the error message with a 500 status code
    

@app.route('/upload', methods=['POST'])
def upload():
    global file_path, new_file_path  # Declare them as global variables

    print("upload Triggered")
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        print(f"filename is {file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        file.close()  # Close the original file
        print(f"filepath is {file_path}")
        
        # Call the processxlsx function from your_module
        new_file_path = processxlsx(file_path)  # Use the original file path
        print(f"outputfilepath is {new_file_path}")
        
        # Determine the appropriate MIME type
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        # Get the original filename for the download
        original_filename = secure_filename(file.filename)
        print(f"original filename is {original_filename}")
        
        # Close the processed file before sending the response
        response = send_file(new_file_path, as_attachment=True, mimetype=mime_type, download_name=original_filename)        
        return response

import shutil  # Import the shutil module for working with file operations

@app.after_request
def cleanup(response):
    global file_path, new_file_path  # Access the global variables
    print(f"file path is {file_path} \n new file path is {new_file_path}")
    if file_path is None or new_file_path is None:
        return response
    
    temp_folder_path = app.config['UPLOAD_FOLDER']  # Get the path to the temp folder
    
    if os.path.exists(temp_folder_path) and os.path.isdir(temp_folder_path):
        print("cleaning temp")
        for file_name in os.listdir(temp_folder_path):
            file_path_to_delete = os.path.join(temp_folder_path, file_name)
            try:
                if os.path.isfile(file_path_to_delete):
                    os.remove(file_path_to_delete)  # Delete individual files
                elif os.path.isdir(file_path_to_delete):
                    shutil.rmtree(file_path_to_delete)  # Delete subdirectories
            except Exception as e:
                print(f"Error deleting {file_path_to_delete}: {e}")
    
    file_path, new_file_path = None, None
    return response



def processxlsx(file_path):
    try:
        output_file_path = name_extractor.get_predictions(file_path=file_path)
        return output_file_path
    except Exception as e:
        return str(e), 500  # Return the error message with a 500 status code
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)