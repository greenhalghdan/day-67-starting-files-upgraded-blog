from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()

class NewPostForm(FlaskForm):
    title = StringField('Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    img_url = StringField('Image background URL', validators=[DataRequired()])
    body = CKEditorField('Body')
    submit = SubmitField('Submit')

@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    results = db.session.execute(db.select(BlogPost).limit(3)).scalars().all()
    posts = []
    for result in results:
        post = {
            "title": result.title,
            "subtitle": result.subtitle,
            "id": result.id,
            "author": result.author,
            "date": result.date
        }
        posts.append(post)
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/show_post/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    requested_post = {
        "subtitle": result.subtitle,
        "author": result.author,
        "date": result.date,
        "body": result.body,
        "id": result.id
    }
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/new-post/', methods=["GET", "POST"])
def new_post():
    blog_form = NewPostForm()

    if blog_form.validate_on_submit():
        blog_post = {
            "title": blog_form.title.data,
            "subtitle": blog_form.subtitle.data,
            "author": blog_form.author.data,
            "img_url": blog_form.img_url.data,
            "body": blog_form.body.data
        }
        new_blog_post = BlogPost(
            title=blog_post["title"],
            subtitle=blog_post["subtitle"],
            body=blog_post["body"],
            author=blog_post["author"],
            img_url=blog_post["img_url"],
            date=date.today().strftime("%B %d, %Y")

        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=blog_form, pagetitle="New Post")


# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    edit_blog_form = NewPostForm(
        title=result.title,
        subtitle = result.subtitle,
        author = result.author,
        img_url = result.img_url,
        body = result.body
    )
    if edit_blog_form.validate_on_submit():
        result.title = edit_blog_form.title.data
        result.subtitle = edit_blog_form.subtitle.data
        result.author = edit_blog_form.author.data
        result.img_url = edit_blog_form.title.data
        result.body = edit_blog_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))

    return render_template("make-post.html", form=edit_blog_form, pagetitle="Edit Post")


# TODO: delete_post() to remove a blog post from the database
@app.route('/delete-post/<int:post_id>', methods=["GET", "POST"])
def delete_post(post_id):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
