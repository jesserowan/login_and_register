from flask import Flask, request, redirect, render_template, session, flash
import re, datetime
from flask_bcrypt import Bcrypt
from mysqlconnection_copy import connectToMySQL
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key="keep it secret, keep it safe"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["POST"])
def register():

    mysql = connectToMySQL('login_and_register')

    if request.form['first_name'] == "":
        flash("First name is required.")

    elif len(request.form['first_name']) < 2:
        flash("Name must be at least 2 characters.")
    
    if request.form['last_name'] == "":
        flash("Last name is required.")

    elif len(request.form['last_name']) < 2:
        flash("Name must be at least 2 characters.")

    if request.form['email'] == "":
        flash("Email is required.")

    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email format")

    other_emails = mysql.query_db("SELECT email FROM accounts WHERE email=%(email)s;", {"email": request.form['email']})
    if other_emails:
        flash("This email has already been used to create an account.")

    if request.form['password'] == "":
        flash("Password is required.")

    elif len(request.form['password']) < 8:
        flash("Password must be at least 8 characters.")

    if request.form['confirm_pass'] == "":
        flash("Password confirmation is required.")

    elif request.form['confirm_pass'] != request.form['password']:
        flash("You must enter the same password in both fields.")

    if '_flashes' in session.keys():
        return redirect('/')

    else:
        mysql = connectToMySQL('login_and_register')

        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)

        query = "INSERT INTO accounts (first_name, last_name, email, pw_hash, updated_at, created_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pwh)s, NOW(), NOW());"

        data = {
            "fn": request.form['first_name'],
            "ln": request.form['last_name'],
            "em": request.form['email'],
            "pwh": pw_hash
        }

        new_user = mysql.query_db(query, data)

        if new_user:
            session['current_user_id'] = new_user
        else:
            return redirect('/')
    
        return redirect('/success')

@app.route('/login', methods=["POST"])
def login():



    mysql = connectToMySQL('login_and_register')

    query = "SELECT id, email, pw_hash FROM accounts WHERE email=%(email)s;"

    data = {
        "email": request.form['login_email'] 
    }
    result = mysql.query_db(query, data)

    if result:
        if bcrypt.check_password_hash(result[0]['pw_hash'], request.form['login_pass']):
            session['current_user_id'] = result[0]['id']
            return redirect('/success')
        
    flash("Your information is incorrect.")
    return redirect('/')

@app.route('/success')
def success():
    mysql = connectToMySQL('login_and_register')

    query = "SELECT first_name FROM accounts WHERE id=%(id)s;"

    data = {
        "id": session['current_user_id']
    }
    welcome = mysql.query_db(query, data)

    return render_template('success.html', name=welcome)

if __name__ == '__main__':
    app.run(debug=True)