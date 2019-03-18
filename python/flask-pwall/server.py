from flask import Flask, redirect, request, render_template, flash, session
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "BlahBlahBlahBLAH"


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=["POST"])
def register():
    # validate post data
    is_valid = True
    if len(request.form['first_name']) < 2:
        flash('First name must be at least 2 characters long.', 'first_name')
        is_valid = False
    elif not request.form['first_name'].isalpha():
        flash('First name must be alphabetical characters only.', 'first_name')
        is_valid = False
    if len(request.form['last_name']) < 2:
        flash('Last name must be at least 2 characters long.', 'last_name')
        is_valid = False
    elif not request.form['last_name'].isalpha():
        flash('Last name must be alphabetical characters only.', 'last_name')
        is_valid = False
    if len(request.form['reg_email']) < 1 and not EMAIL_REGEX.match(request.form['reg_email']):
        flash('Email address is not valid.', 'reg_email')
        is_valid = False
    if len(request.form['reg_password']) < 8:
        flash('Password must be at least 8 characters long.', 'reg_password')
        is_valid = False
    elif request.form['reg_password'] != request.form['confirm_password']:
        flash('Password do not match.', 'reg_password')
        is_valid = False
    
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['reg_password'])  
        mysql = connectToMySQL("private_wall")
        query = "INSERT INTO users (first_name, last_name, email, password_hash, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s, NOW(), NOW());"
        data = {"first_name" : request.form['first_name'],
                "last_name" : request.form['last_name'],
                "email" : request.form['reg_email'],
                "password_hash" : pw_hash }
        user = mysql.query_db(query, data)
        session['greeting_name'] = request.form['first_name']
        session['id'] = user
        return redirect("/wall")
    else:
        return render_template("index.html")

@app.route('/login', methods=["POST"])
def login():
    mysql = connectToMySQL("private_wall")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["login_email"] }
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password_hash'], request.form['login_password']):
            session['greeting_name'] = result[0]['first_name']
            session['id'] = result[0]['id']
            return redirect('/wall')
    flash("Email and password do not match.", 'login')
    return redirect("/")

@app.route('/wall')
def wall():
    db = connectToMySQL('private_wall')
    all_users = db.query_db('SELECT * FROM users;')
    db = connectToMySQL('private_wall')
    all_messages = db.query_db('SELECT * FROM messages WHERE messages.to_user = %(id)s;', {'id': session['id']})
    return render_template("wall.html", users = all_users, messages = all_messages)

@app.route('/create', methods=['POST'])
def create_message():
    is_valid = True
    if len(request.form['content']) < 5:
        flash('Message must be at least 5 characters long.', 'message')
        is_valid = False

    if is_valid == False:
        return redirect('/wall')
    else:
        db = connectToMySQL('private_wall')
        query = "INSERT INTO messages (content, to_user, from_user, created_at, updated_at) VALUES (%(c)s, %(to)s, %(from)s, NOW(), NOW());"
        data = {
            'c': request.form['content'],
            'to': request.form['to_user'],
            'from': session['id']
        }
        db.query_db(query,data)

        return redirect('/wall')

@app.route('/delete/<id>')
def delete_message(id):
    db = connectToMySQL('private_wall')
    query = 'DELETE FROM messages WHERE id = %(id)s;'
    data = {
        'id': int(id)
    }
    db.query_db(query,data)

    return redirect('/wall')

@app.route('/logout')
def logout():
    session.clear()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)