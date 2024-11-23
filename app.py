from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Change to your MySQL username
app.config['MYSQL_PASSWORD'] = 'Vivek94947@'  # Change to your MySQL password
app.config['MYSQL_DB'] = 'user_database'

# Set up logging
logging.basicConfig(level=logging.DEBUG)

mysql = MySQL(app)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ensure the username and password are valid
        if not username or not password:
            flash('Both fields are required!', 'danger')
            return render_template('register.html')

        password_hash = generate_password_hash(password)

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password_hash))
            mysql.connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            logging.error(f"Error during registration: {str(e)}")
            flash('Username already exists or database error. Try another username.', 'danger')
        finally:
            cursor.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ensure the username and password are valid
        if not username or not password:
            flash('Both fields are required!', 'danger')
            return render_template('login.html')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):  # user[2] is the password hash
                session['username'] = user[1]
                flash('Welcome back!', 'success')
                return redirect(url_for('success'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')

        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            flash('An error occurred during login. Please try again later.', 'danger')
        finally:
            cursor.close()

    return render_template('login.html')

@app.route('/success')
def success():
    if 'username' in session:
        return render_template('success.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT DATABASE()')
        db = cursor.fetchone()
        return f"Connected to database: {db[0]}"
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return f"Error: {str(e)}"
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)
