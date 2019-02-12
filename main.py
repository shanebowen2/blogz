from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'gobble'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

posts =[]    

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    authors = User.query.all()
    return render_template('index.html', authors=authors, title='Blogz')



@app.route('/blog', methods=['POST', 'GET'])
def blog():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    

    if blog_id == None and user_id == None:
        return render_template('posts.html', posts=posts, title='Build-a-blog')
    elif blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('entry.html', post=post, title='Blog Entry')
    elif user_id:
        entries = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleuser.html', entries=entries)



@app.route('/newpost')
def new_post():
    return render_template('newpost.html')

def empty_val(x):
    if x:
        return True
    else:
        return False

@app.route('/newpost', methods=['POST', 'GET'])
def new_post_complete():

    username = request.form['username']
    password = request.form['password']
    owner = User.query.filter_by(email=session['email']).first()

    username_error = ""
    password_error = ""
 
    err_required = "Required field"
 
    if not empty_val(password):
        password_error = err_required
        password = ''
    
    if not empty_val(username):
        username_error = err_required
        username = ''
     
    if not username_error and not password_error:
        new_entry = Blog(username, password, owner)
        db.session.add(new_entry)
        db.session.commit()

        return redirect('/blog?id={}'.format(new_entry.id))

    elif not username_error and password_error:
        return render_template('newpost.html', username=username, password_error=password_error)

    else:
        return render_template('newpost.html', password=password, username_error=username_error)
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')
     
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if password != verify:
            flash('User password and verify do not match. Try again.', 'error')
            return redirect('/register')


        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            
            return "<h1>Duplicate User</h1>"

    return render_template('register.html')    

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')



@app.route("/delete-post", methods=['POST'])
def delete_post():

    post_id = int(request.form['post-id'])
    post = Blog.query.get(post_id)
    db.session.add(post)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()