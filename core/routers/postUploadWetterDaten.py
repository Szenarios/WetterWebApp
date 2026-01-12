from main import app


@app.route('/upload', methods=['POST'])
def upload_file():
    print("awd")
    """ 
    if 'file' not in request.files:
        print("err1")
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        print("err2")
        return 'No selected file', 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    # Hier kannst du die Datei analysieren und Daten in DB schreiben
    return 'File uploaded successfully', 200
    """
