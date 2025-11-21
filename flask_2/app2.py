from flask import Flask, request, flash, redirect, url_for, render_template
import uuid
import json, os, pathlib, hashlib
app =Flask(__name__)
app.secret_key = 'iamstupid'
upload_folder = 'uploads'
app.config['UPLOAD_FOLDER'] = upload_folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files: 
            flash("Файл не найден", "error")
            return redirect('/')
        
        file = request.files['file'] 
        file_uuid = uuid.uuid4()
        filename = file.filename

        file_extension = pathlib.Path(filename).suffix
        if file_extension in('.exe','.sh','.php','.js'):
            flash('Недопустимое расширение файла', 'error')
            return redirect('/')
        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'], 
            f"{file_uuid}_{filename}"
        )
        file.save(filepath)
        if check_hash(filepath) == False:
            os.remove(filepath)
            flash('Файл уже существует', 'error')
            return redirect('/')
        file_hash = hash_find(filepath)
        metadata(filename, file_uuid, file_hash)
        flash("Файл успешно загружен", 'success')
        return redirect('/')
    return render_template('form.html')
def hash_find(filename):
    hash_md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()     

def metadata(filename, file_uuid, hesh_md5):
    if os.path.exists('files.json'):
        with open('files.json', 'r') as f:
            data = json.load(f)
    else:
        data = []   
    met = {
        "filename": str(filename),
        "uuid": str(file_uuid),
        "hesh": hesh_md5
    }
    data.append(met)

    with open('files.json', 'w') as f:
        json.dump(data, f, indent=2)
     
    
def check_hash(filename):
    file_hash = hash_find(filename)
    if os.path.exists('files.json'):
        with open('files.json', 'r') as f:
            data = json.load(f)
    else:
        data = [] 

    # Ищем совпадение по хешу
    for record in data:
        if record['hesh'] == file_hash:
            return False  # Дубликат найден
    return True  # Дубликатов нет
if __name__ == '__main__':
    app.run(debug=True)