from flask import Flask, render_template, redirect, url_for, request, flash
import os
import string
import uuid
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from utils import load_json, save_json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    users_dict = load_json("data", "users_dict.json")
    if user_id in users_dict:
        user_data = users_dict[user_id]
        return User(user_data['username'], user_id, user_data['password_hash'])
    return None

class User(UserMixin):
    def __init__(self, username, id, password):
        self.username = username
        self.id = id
        self.password = password

class LoginForm(FlaskForm):
    username = StringField("Введите логин", validators=[DataRequired()])
    password = PasswordField("Введите пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")

class RegistrationForm(FlaskForm):
    def validate_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError("Пароль должен быть длиной не менее 8 символов.")
        if not len(set(string.digits) & set(password)):
            raise ValidationError("Пароль должен содержать цифры.")
        if not len(set(string.ascii_lowercase) & set(password)):
            raise ValidationError("Пароль должен содержать маленькие латинские буквы.")
    def validate_username(self, field):
        username = field.data
        user_dct = load_json("data", "user_dict.json")
        if username in user_dct:
            raise ValidationError("Такой пользоваетель уже зарегистрирован.")
        if username in ["admin", "root", "superuser", "director", "chief", "boss"]:
            raise ValidationError("Такое имя пользоваетеля запрещено.")
         

    username = StringField("Имя пользователя", 
        validators=[
            DataRequired(), 
            Length(min=4, max=25, message="Имя пользователя должно быть длиной от 4 до 25 символов."), 
            validate_username
            ])
    password = PasswordField("Пароль", 
        validators=[
            DataRequired(), 
            validate_password
            ])
    confirm = PasswordField("Повтор пароля",
        validators=[
            DataRequired(), 
            EqualTo("password", message="Пароли должны совпадать.")
            ])
    submit = SubmitField("Регистрация")
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        users_dict = load_json("data", "users_dict.json")
        user_found = False
        for user_id, user_data in users_dict.items():
            if user_data['username'] == username:
                user_found = True
                if check_password_hash(user_data['password_hash'], password):
                    user_data['last_login'] = datetime.now().isoformat() 
                    save_json("data", "users_dict.json", users_dict)  
                    user = User(username, user_id, user_data['password_hash'])
                    login_user(user)
                    flash('Вход выполнен')
                    return redirect(url_for('create_user_page'))
                else:
                    flash('Неверный пароль', 'error')
                   
        if not user_found:
            flash('Кто ты? Зарегистрируйся!', 'error')
            return redirect(url_for('register'))
      
    
    return render_template('login.html', form=form)#может зря сделала

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
     
    if form.validate_on_submit():
        username = form.username.data   
        password = form.password.data
        users_dict = load_json("data", "users_dict.json")
        id = str(uuid.uuid4())
        hash = generate_password_hash(password)
        user = User(username, id, hash)
       
        for id, user_data in users_dict.items():
            if user_data['username'] == username:
                flash('Пользователь с таким именем уже есть!', 'error')
                return redirect(url_for('register'))
        
        users_dict[id] = {
            "username": user.username,
            "password_hash": hash,
            "date_registered": datetime.now().isoformat(),   
            "last_login": None
        }
        save_json("data", "users_dict.json", users_dict)
        flash('Пользователь создан')
        return redirect(url_for('login'))  # очень спорно

    return render_template('register.html', form=form)

@app.route('/create-user')
@login_required
def create_user_page():
    return redirect(url_for('register'))
 
@app.route("/")
def index():
    return redirect(url_for('login'))
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
    