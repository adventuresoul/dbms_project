from flask import render_template, redirect, url_for, flash, request, session
from myproject import db, app, stripe, public_key
from myproject.models import Product, Customer, Cart, Payment_history
from myproject.forms import (
    ProductRegisterForm,
    CustomerLoginForm,
    CustomerRegisterForm,
    deleteProduct,
)
from flask_login import login_user, login_required, logout_user
from decimal import Decimal
import os


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html')
#################################################################################################################
################################## ACCOUNT SECTION ##############################################################
#################################################################################################################
@app.route("/account")
@login_required
def account():
    user = Customer.query.get(session["user_id"])
    return render_template("account.html", customer=user)


@app.route("/home")
@login_required
def welcome_user():
    return render_template("home.html")


@app.route("/logout")
@login_required
def logout():
    session.pop('user_id', None)
    logout_user()
    flash("You logged out!")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        with app.app_context():
            user = Customer.query.filter_by(email=form.email.data).first()

            if user is None:
                return redirect("register")

            if user.check_password(form.password.data) and user is not None:
                session["user_id"] = user.id
                login_user(user)
                flash("Log in successful.")

                if (
                    user
                    == Customer.query.filter_by(
                        email="admin@admin.com"
                    ).first()
                ):
                    return redirect(url_for("admin"))

                next = request.args.get("next")
                if next == None or not next[0] == "/":
                    next = url_for("welcome_user")

                return redirect(next)
            else:
                flash("Incorrect email_id or password")

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = CustomerRegisterForm()

    if form.validate_on_submit():
        with app.app_context():
            user = Customer(
                name=form.name.data,
                email=form.email.data,
                contact=form.contact.data,
                address=form.address.data,
                password=form.password.data,
            )
            db.session.add(user)
            db.session.commit()
            flash("Thanks for registering! Now you can login!")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


#################################################################################################################
################################## PRODUCT SECTION ##############################################################
#################################################################################################################


@app.route("/all-products")
def product_list():
    products = None
    with app.app_context():
        products = Product.query.all()

    return render_template("products.html", products=products)


@app.route("/product-info/<product_id>")
def product_info(product_id):
    with app.app_context():
        product = Product.query.filter_by(id=product_id).first()
        return render_template("product_description.html", product=product)


@app.route("/add_to_cart/<product_id>")
@login_required
def add_prod_cart(product_id):
    with app.app_context():
        my_cart = Cart(session["user_id"], product_id)
        prod = Product.query.get(product_id)
        if prod and prod.quantity > 0:
            prod.quantity -= 1
            db.session.add(prod)
            db.session.commit()
        else:
            flash("No stock")
            return redirect(url_for("product_list"))

        db.session.add(my_cart)
        db.session.commit()
    return redirect(url_for("show_cart"))


@app.route("/remove_from_cart/<cart_id>/<product_id>")
@login_required
def remove_prod_cart(cart_id, product_id):
    with app.app_context():
        my_cart_item = Cart.query.get(cart_id)
        prod = Product.query.get(product_id)
        if my_cart_item:
            if prod:
                prod.quantity += 1
                db.session.add(prod)
                db.session.commit()
            else:
                return "Product not found", 404
            db.session.delete(my_cart_item)
            db.session.commit()
            return redirect(url_for("show_cart"))
        elif my_cart_item is None:
            return f"Cart not found: {cart_id}", 404


@app.route("/mycart")
@login_required
def show_cart():
    with app.app_context():
        items = Cart.query.filter_by(customer_id=session["user_id"]).all()
        products = []
        sums = 0
        for i in items:
            prod = Product.query.get(i.product_id)
            products.append([prod, i.id])
            sums += prod.price

        return render_template(
            "cart.html", products=products, price=sums, public_key=public_key
        )


@app.route("/payment/<total_price>", methods=["GET", "POST"])
@login_required
def payment(total_price):
    if "stripeEmail" not in request.form:
        return "Email address is missing", 400

    amount = int(Decimal(total_price) * 100)
    customer = stripe.Customer.create(
        email=request.form["stripeEmail"], source=request.form.get("stripeToken")
    )
    charge = stripe.Charge.create(
        customer=customer.id, amount=amount, currency="INR", description="Order"
    )
    flash("Order placed")
    items = Cart.query.filter_by(customer_id=session["user_id"])
    for i in items:
        hist = Payment_history(session["user_id"], i.product_id)
        db.session.add(hist)
        db.session.commit()
        db.session.delete(i)
        db.session.commit()

    return redirect(url_for("show_cart"))

@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment_cod():
    flash("Order placed")
    items = Cart.query.filter_by(customer_id=session["user_id"])
    for i in items:
        hist = Payment_history(session["user_id"], i.product_id)
        db.session.add(hist)
        db.session.commit()
        db.session.delete(i)
        db.session.commit()

    return redirect(url_for("show_cart"))



@app.route("/order-history", methods=["POST", "GET"])
@login_required
def show_history():
    items = Payment_history.query.filter_by(customer_id = session["user_id"])
    products = []

    for i in items:
        prod = Product.query.filter_by(id = i.product_id).first()
        products.append(prod)

    return render_template("order_history.html", products=products)


#################################################################################################################
################################## ADMIN CONTROLS ###############################################################
#################################################################################################################

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    return render_template("admin.html")


@app.route("/admin-add_product", methods=["GET", "POST"])
def add_product_stock():
    form = ProductRegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        quant = form.availibility.data
        description = form.description.data
        image = form.image.data

        # Add new product to database
        prod = Product(name, price, image, description, quant)
        with app.app_context():
            flash("item added to stock successfully!")
            db.session.add(prod)
            db.session.commit()

        return redirect(url_for("product_list"))

    return render_template("add_product.html", form=form)


@app.route("/admin-delete_product", methods=["GET", "POST"])
@login_required
def delete_product_stock():
    form = deleteProduct()
    if form.validate_on_submit():
        id = form.id.data
        try:
            with app.app_context():
                prod = Product.query.filter_by(id=id).first()
                flash("item deleted from stock successfully!")
                db.session.delete(prod)
                db.session.commit()
        except:
            return "Cannot delete the product, it has been ordered by someone"

        return redirect(url_for("product_list"))

    return render_template("delete_product.html", form=form)


@app.route("/admin-stock_anlyzer", methods=["GET", "POST"])
@login_required
def stock_analyzer():
    all_prod = Product.query.all()
    products = []
    for i in all_prod:
        if i.quantity <= 5:
            products.append(i)
    return render_template("stock_demand.html", products=products)

@app.route("/admin_shipment", methods = ['GET', 'POST'])
@login_required
def shipment():
    items = Payment_history.query.all()
    products = []
    for i in items:
        cust = Customer.query.filter_by(id = i.customer_id).first()
        prod = Product.query.filter_by(id = i.product_id).first()
        data = [prod.name, prod.id, cust.address, prod.image, i.id]
        products.append(data)

    return render_template("shipment.html", products=products)



#################################################################################################################
################################## ERROR HANDLING ###############################################################
#################################################################################################################
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("error_page"))


@app.errorhandler(500)
def internal_server_error(e):
    return redirect(url_for("error_page"))


@app.route("/error")
def error_page():
    return render_template("error.html")


if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=True)
# host="0.0.0.0", port=8080, threaded=True,
