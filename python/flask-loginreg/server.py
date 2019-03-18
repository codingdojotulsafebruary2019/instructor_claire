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
        mysql = connectToMySQL("login_and_regis_db")
        query = "INSERT INTO users (first_name, last_name, email, password_hash, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s, NOW(), NOW());"
        # put the pw_hash in our data dictionary, NOT the password the user provided
        data = {"first_name" : request.form['first_name'],
                "last_name" : request.form['last_name'],
                "email" : request.form['reg_email'],
                "password_hash" : pw_hash }
        mysql.query_db(query, data)
        session['greeting_name'] = request.form['first_name']
        return redirect("/success")
    else:
        return render_template("index.html")

@app.route('/login', methods=["POST"])
def login():
    mysql = connectToMySQL("login_and_regis_db")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["login_email"] }
    result = mysql.query_db(query, data)
    if result:
        # assuming we only have one user with this username, the user would be first in the list we get back
        # of course, we should have some logic to prevent duplicates of usernames when we create users
        # use bcrypt's check_password_hash method, passing the hash from our database and the password from the form
        if bcrypt.check_password_hash(result[0]['password_hash'], request.form['login_password']):
            # if we get True after checking the password, we may put the user id in session
            session['greeting_name'] = result[0]['first_name']
            # never render on a post, always redirect!
            return redirect('/success')
    # if we didn't find anything in the database by searching by username or if the passwords don't match,
    # flash an error message and redirect back to a safe route
    flash("Email and password do not match.", 'login')
    return redirect("/")

@app.route('/success')
def success():
    return render_template("success.html")

@app.route('/logout')
def logout():
    session.clear()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)