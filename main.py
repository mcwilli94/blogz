from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2


app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:mcwilli94@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

db = SQLAlchemy(app)
# the secret key for the project
app.secret_key = 'y337kGcoasdnfiewnfsjASEFV98323ERFVB'


class Blog(db.Model):

    id = db.Column(db.INTEGER, primary_key=True)
    title = db.Column(db.VARCHAR(30), unique=True)
    body = db.Column(db.VARCHAR(500))
    owner_id = db.Column(db.INTEGER, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner_id = owner


class User(db.Model):

    id = db.Column(db.INTEGER, primary_key=True)
    username = db.Column(db.VARCHAR(120), unique=True)
    password = db.Column(db.VARCHAR(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


# function used to pull all blogs from the database
def get_posts():
    return Blog.query.all()

# function used to pull all users from the database
def get_users():
    return User.query.all()

# displays home page and all the blog posts in the database
@app.route("/blog", methods=['GET', 'POST'])
def blog_page():
    # pull the info on the selected author
    author = request.args.get("user")
    
    if author == None:
        # get blog posts from database
        all_posts = get_posts()
        all_users = get_users()
        return render_template("blog.html", all_posts=all_posts, all_users=all_users)    

    else:
        # pull user id from User's table
        author_id = db.session.query(User.id).filter_by(username=author).all()

        # remove unwanted symboles and convert to proper data type
        author_id= str(author_id)
        author_id = author_id[2:len(author_id)-3]
        author_id = int(author_id)

        # pulls all posts by the author from the database
        author_posts = db.session.query(Blog).filter_by(owner_id=author_id).all()

        return render_template("singleUser.html", author_posts=author_posts, author=author)




@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=email).first()
        if user and user.password == password:
            session['username'] = email
            flash("Logged in")
            return render_template("newpost.html")
        elif not user:
            flash("This username does not exist", "error")
            return redirect("/login")
        elif user and user.password != password:
            flash("Your password is incorrect", "error")
            return redirect("/login")

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # check username to make sure it is valid
        if (len(email) < 4) or (len(email) > 120) or ((" " in email) == True):
            flash("That's not a valid email address", "error")
            return redirect("/signup")

        # check passwrd to make sure it is valid
        if (password == "") or (len(password) < 4) or (len(password) > 120) or ((" " in password) == True):
            flash("That is not a valid password", "error")
            return redirect("/signup")

        # check password verification to make sure it matches the password previously entered
        if (verify != password) or (verify == ""):
            flash("The passwords do not match", "error")
            return redirect("/signup")

        # checks to see if user is already in the system
        existing_user = User.query.filter_by(username=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = email
            return redirect("/newpost")
        else:
            # TODO - user better response messaging
            flash("Username already exists in the system")
            return redirect("/signup")
    else:
        return render_template("signup.html")



@app.route('/logout')
def logout():
    del session['username']
    return redirect('/index')



# adds a new blog post
@app.route("/newpost", methods=['GET', 'POST'])
def new_post():
    # add new entry to database
    if request.method == 'POST':
        title = request.form['title']
        post = request.form['post']
        owner_id = db.session.query(User.id).filter_by(username=session['username']).all()

        # remove unwanted symboles and convert to proper data type
        owner_id= str(owner_id)
        owner_id = owner_id[2:len(owner_id)-3]
        owner_id = int(owner_id)

        # insert new entry into the blog table
        blog = Blog(title=title, body=post, owner=owner_id)
        db.session.add(blog)
        db.session.commit()

        # get the id of the previously created blog post
        post_id = db.session.query(Blog.id).filter_by(id=blog.id).all()
        post_id= str(post_id)
        post_id = post_id[2:len(post_id)-3]
        return redirect("/individualblog?id=" + post_id)
    else:
        return render_template("newpost.html")


@app.route("/individualblog", methods=['GET', 'POST'])
def individual_post():
    # pull id number from the link selected
    post_id = request.args.get("id")
    
    blog = Blog.query.get(post_id)
    # pull data from the database matching the id number
    # title = db.session.query(Blog.title).filter_by(id=post_id).all()
    # post = db.session.query(Blog.body).filter_by(id=post_id).all()

    # # change the data to string format
    # title = str(title)
    # post = str(post)

    # remove unwanted symbols
    #title = title[3:len(title)-4]
    #post = post[3:len(post)-4]

    return render_template("individualblog.html", blog=blog)



@app.route("/")
def index():
    # pulls all the user data from the User table
    authors = User.query.all()

    return render_template("index.html", authors=authors)



endpoints_without_login = ['login', 'signup', 'index', 'blog']

@app.before_request
def require_login():
    if not ('username' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")



if __name__ == "__main__":
    app.run()