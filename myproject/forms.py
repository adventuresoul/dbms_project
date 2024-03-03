from flask_wtf import FlaskForm
from myproject import *
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    IntegerField,
    RadioField,
    SubmitField,
    EmailField,
    PasswordField,
)
from wtforms.validators import DataRequired, ValidationError, EqualTo


class ProductRegisterForm(FlaskForm):
    name = StringField("Product-name", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    availibility = IntegerField("Availibility", validators=[DataRequired()])
    description = TextAreaField("Product-Description", validators=[DataRequired()])
    image = TextAreaField("Image-link", validators=[DataRequired()])
    submit = SubmitField("Submit")


class deleteProduct(FlaskForm):
    id = IntegerField("Product-Id", validators=[DataRequired()])
    submit = SubmitField("submit")


class CustomerRegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    contact = StringField("Contact", validators=[DataRequired()])
    address = TextAreaField("Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Signup")

    def check_email(self, field):
        with app.app_context:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError("Your email has been already regsitered")


class CustomerLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
