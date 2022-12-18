from flask import Flask, render_template, redirect, flash, url_for
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask import request

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash




#Create Flask Instance
app = Flask(__name__)


# configure the SQLite database, relative to the app instance folder
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"



# configure the MySQL database, relative to the app instance folder
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://username:password@localhost/db_name"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:somesh123@localhost/users"

# initialize the app with the extension
db = SQLAlchemy(app)
migrate = Migrate(app, db)



# SECRET_KEY
app.config['SECRET_KEY'] = 'any secret string'



#Define Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    favorite_color = db.Column(db.String(100), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #create a string
    def __repr__(self):
        return "<Name %r>" % self.name


with app.app_context():
    db.create_all()



class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])


class UserForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Password Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    favorite_color = StringField('Favorite Color')


#Create a route decorator
@app.route('/')
def index():
    return render_template("index.html")


@app.route("/users")
def user_list():
    users = User.query.order_by(User.date_added)
    return render_template("user_list.html", users=users)



@app.route("/user/create", methods=["GET", "POST"])
def user_create():
    form = UserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hash_pwd = generate_password_hash(form.password_hash.data, 'sha256')
            user = User(
                name=request.form["name"],
                email=request.form["email"],
                favorite_color = request.form["favorite_color"],
                password_hash = hash_pwd,
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user', id=user.id))

    return render_template("create.html", form=form)



@app.route('/user/<int:id>')
def user(id):
    name = User.query.get_or_404(id)
    return render_template("user.html", user_name=name)



@app.route('/user/update/<int:id>', methods=["GET", "POST"])
def user_update(id):
    form = UserForm()
    name_update = User.query.get_or_404(id)

    if request.method == "POST":
        if form.validate_on_submit():
            hash_pwd = generate_password_hash(form.password_hash.data, 'sha256')
            name_update.name = request.form["name"]
            name_update.email = request.form["email"]
            name_update.password_hash = hash_pwd
            name_update.favorite_color = request.form["favorite_color"]
            try:
                db.session.commit()
                flash(f'{name_update.name}: User updated successfully..!')
                return redirect(url_for("user_list"))
            except :
                flash('Error, looks like a some problem, try again..!')
                return render_template("user_update.html", form=form, name_update=name_update)

    return render_template("user_update.html", form=form, name_update=name_update)




@app.route("/user/delete/<int:id>")
def user_delete(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User removed successfully..!')
        return redirect(url_for("user_list"))
    except:
        flash('Error, looks like some error, try again..!')
        return redirect(url_for("user_list"))




@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = MyForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submited successfully!")
    return render_template('submit.html', name=name, form=form)


if __name__ == '__main__':
    app.run(debug=True)
