from flask import Flask, render_template, request, url_for, redirect, session
import sqlite3

Flask.secret_key = 'notasecretkey'

app = Flask(__name__)

conn = sqlite3.connect('faceback.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (email TEXT, password TEXT, username TEXT);")
conn.commit()
cursor.execute("CREATE TABLE IF NOT EXISTS posts (author TEXT, title TEXT, content TEXT, date TEXT);")
conn.commit()


@app.route('/')
@app.route('/home', methods = ["GET", "POST"])
def home():
    if request.method == 'POST':
        # author = request.form['author']
        title = request.form['title']
        content = request.form['content']

        cursor.execute("INSERT INTO posts VALUES (?, ?, ?, datetime('now'));", (session.get('username', None), title, content))
        conn.commit()
        cursor.execute("SELECT * FROM posts ORDER BY 4 DESC LIMIT 15;")
        posts = cursor.fetchall()
        session['posts'] = posts
        return redirect(url_for('home'))

    return render_template('home.html', user=session.get('username', None), posts_html=session.get('posts', None))


@app.route('/login/', methods = ["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['emaili']
        password = request.form['password']

        cursor.execute("SELECT username FROM users WHERE email = ? AND password = ?", (email, password))
        username = cursor.fetchone()
        if username is not None:       
            cursor.execute("SELECT * FROM posts ORDER BY 4 DESC LIMIT 15;")     
            posts = cursor.fetchall()
            session['username'] = username[0]
            session['posts'] = posts
            print(posts)
            return redirect(url_for('home'))
        else:
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            if cursor.fetchone() is not None:
                error = "The email or the username is inccorect"
            else:
                error = "The email does not exist"
            return render_template('login.html' , error_html=error)

    return render_template('login.html', error_html=error)


@app.route('/registration', methods = ["POST", "GET"])
def registration():
    error = []
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']

        if len(password) < 5:
            error = "The password must contain at least 5 c"

        cursor.execute("SELECT username FROM users WHERE username = ?;", (username,))
        if len(cursor.fetchall()) == 0:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?);", (email, password, username))
            conn.commit() 
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = "This username already exsits"
            return render_template('registration.html', error_html=error)

    return render_template('registration.html', error_html=None)


@app.route('/logout')
def logout():
    session['username'] = None
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True)