from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2


app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.INTEGER, primary_key=True)
    title = db.Column(db.VARCHAR(30), unique=True)
    body = db.Column(db.VARCHAR(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


def get_posts():
    return Blog.query.all()


# displays home page and all the blog posts in the database
@app.route("/blog")
def main_page():
    return render_template("blog.html")


# adds a new blog post
@app.route("/newpost", methods=['GET', 'POST'])
def new_post():
    # add new entry to database
    if request.method == 'POST':
        title = request.form['title']
        post = request.form['post']
        blog = Blog(title=title, body=post)
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
    # get blog posts from database
    all_posts = get_posts()

    return render_template("blog.html", all_posts=all_posts)


if __name__ == "__main__":
    app.run()