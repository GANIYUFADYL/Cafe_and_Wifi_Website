from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, FloatField, IntegerRangeField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
import os

class CafeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    map_url = StringField('Map Url', validators=[DataRequired()])
    img_url = StringField('Image Url', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()], render_kw={"placeholder": "Enter seat range (e.g., 20-30)"})
    has_toilet = BooleanField('Toilets', validators=[DataRequired()])
    has_wifi = BooleanField('Wifi', validators=[DataRequired()])
    has_sockets = BooleanField('Sockets', validators=[DataRequired()])
    can_take_calls = BooleanField('Calls', validators=[DataRequired()])
    coffee_price = FloatField('Coffee Price', validators=[DataRequired()])
    submit= SubmitField('Submit')



class Base(DeclarativeBase):
  pass

db = SQLAlchemy()
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"

db.init_app(app)
bootstrap = Bootstrap5(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(
            self):  # This is a dictionary comprehension function created inside the Cafe class definition. It will be used to turn rows into a dictionary before sending it to jsonify.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all", methods= ['GET'])
def all_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    list_of_cafes = []
    for cafes in all_cafes:
        list_of_cafes.append(cafes.to_dict())
    return render_template('all.html', all_cafes=list_of_cafes)

@app.route("/add", methods= ['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe()
        def display_price():
            price = form.coffee_price.data
            formatted_price = format(price, ".2f")
            return f'€{formatted_price}'

        new_cafe.name = form.name.data
        new_cafe.map_url = form.map_url.data
        new_cafe.img_url = form.img_url.data
        new_cafe.location = form.location.data
        new_cafe.seats = form.seats.data
        new_cafe.has_toilet = form.has_toilet.data
        new_cafe.has_wifi = form.has_wifi.data
        new_cafe.has_sockets = form.has_sockets.data
        new_cafe.can_take_calls = form.can_take_calls.data
        new_cafe.coffee_price = display_price()
        db.session.add(new_cafe)
        db.session.commit()
        return redirect('/all')
    return render_template('add.html', form=form)

@app.route("/delete/<int:id>", methods= ['GET', 'POST'])
def delete_cafe(id):
    cafe = db.get_or_404(Cafe, id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect("/all")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)