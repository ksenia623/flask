from flask import Flask, request, flash, redirect, url_for, render_template
import uuid
import json, os, pathlib, hashlib

app = Flask(__name__)
app.secret_key = os.urandom(256)


upload_folder = "uploads"
app.config["UPLOAD_FOLDER"] = upload_folder
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.mkdir(app.config["UPLOAD_FOLDER"])
black_list = [".exe", ".sh", ".php", ".js"]


def hash_find(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@app.route("/", methods=["GET", "POST"])
def upload_file():
    data = []
    if os.path.exists("files.json"):
        with open("files.json", "r") as f:
            data = json.load(f)

    if request.method == "POST":
        if "file" not in request.files:
            flash("Файл не найден", "error")
            return redirect(url_for("upload_file"))

        file = request.files["file"]
        filename = file.filename

        file_extension = pathlib.Path(filename).suffix
        if file_extension in black_list:
            flash("Недопустимое расширение файла", "error")
            return redirect(url_for("upload_file"))

        new_filename = f"{uuid.uuid4()}.{file_extension}"
        uuid_path = os.path.join(
            app.config["UPLOAD_FOLDER"], new_filename[:2], new_filename[2:4]
        )
        if not os.path.exists(uuid_path):
            os.makedirs(uuid_path)

        file.save(os.path.join(uuid_path, new_filename))
        md5 = hash_find(os.path.join(uuid_path, new_filename))
        for d in data:
            if d["hesh"] != md5:
                continue
            os.remove(os.path.join(uuid_path, new_filename))
            flash("Файл уже существует", "error")
            return redirect(url_for("upload_file"))

        data.append({"filename": str(filename), "uuid": new_filename, "hesh": md5})
        with open("files.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        flash("Файл успешно загружен", "success")
        return redirect(url_for("upload_file"))

    return render_template("form.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
