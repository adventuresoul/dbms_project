from myproject import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def user_loader(user_id):
    return Customer.query.get(user_id)


class Customer(db.Model, UserMixin):
    __tablename__ = "Customer"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    contact = db.Column(db.String(10))
    email = db.Column(db.Text)
    address = db.Column(db.Text)
    password_hash = db.Column(db.Text)

    def __init__(self, name, contact, email, address, password):
        self.name = name
        self.contact = contact
        self.email = email
        self.address = address
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact": self.contact,
            "email": self.email,
            "address": self.address,
            "password": self.password,
        }


class Product(db.Model):
    __tablename__ = "Product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    price = db.Column(db.Numeric(precision=10, scale=2))
    image = db.Column(db.Text)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer)

    def __init__(self, name, price, image, description, quantity):
        self.name = name
        self.price = price
        self.image = image
        self.description = description
        self.quantity = quantity

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "description": self.description,
            "quantity": self.quantity,
        }


class Cart(db.Model, UserMixin):
    __tablename__ = "Cart"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customer.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("Product.id"))

    def __init__(self, customer_id, product_id):
        self.customer_id = customer_id
        self.product_id = product_id

    def __repr__(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
        }


class Payment_history(db.Model, UserMixin):
    __tablename__ = "Payment_history"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customer.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("Product.id"))

    def __init__(self, customer_id, product_id):
        self.customer_id = customer_id
        self.product_id = product_id
   

    def __repr__(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,

        }
