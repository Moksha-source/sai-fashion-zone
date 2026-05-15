from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fashion.db"

db = SQLAlchemy(app)

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- Model ---

class Product(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    price    = db.Column(db.Integer, nullable=False)
    image    = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    
# --- Seed Data ---

def seed_data():

    if Product.query.first():
        return  # already seeded, skip

    products = [
        # Shirts
        Product(name="Formal Shirt",       price=799,  image="formal_shirt.jpeg",  category="shirts"),
        Product(name="Printed Shirt",      price=699,  image="printed_shirt.jpeg", category="shirts"),
        Product(name="Check Shirt",        price=899,  image="check_shirt.jpeg",   category="shirts"),

        # Pants
        Product(name="Formal Pant",        price=1199, image="pant1.jpeg",         category="pants"),
        Product(name="Cotton Pant",        price=899,  image="pant2.jpeg",         category="pants"),
        Product(name="Slim Fit Pant",      price=999,  image="pant3.jpeg",         category="pants"),

        # T-Shirts
        Product(name="Round Neck T-Shirt", price=499,  image="Tshirts.jpeg",       category="tshirts"),

        # Night Pants
        Product(name="Night Pant",         price=599,  image="nightpant.jpeg",     category="nightpants"),
        Product(name="Joggers",            price=649,  image="nightpant2.jpeg",    category="nightpants"),
        Product(name="Shorts",             price=299,  image="shorts.jpeg",        category="nightpants"),
    ]

    db.session.add_all(products)
    db.session.commit()
    print("Database seeded!")

# --- Routes ---

@app.route("/")
def home():
    products = Product.query.limit(4).all()
    return render_template("index.html",products=products)

@app.route("/shirts")
def shirts():

    page = request.args.get("page", 1, type=int)

    pagination = Product.query.filter_by(
        category="shirts"
    ).paginate(
        page=page,
        per_page=6
    )

    shirts = pagination.items

    return render_template(
        "shirts.html",
        shirts=shirts,
        pagination=pagination
    )

@app.route("/pants")
def pants():
    items = Product.query.filter_by(category="pants").all()
    return render_template("pants.html", pants=items)

@app.route("/tshirts")
def tshirts():
    items = Product.query.filter_by(category="tshirts").all()
    return render_template("tshirts.html", tshirts=items)

@app.route("/nightpants")
def nightpants():
    items = Product.query.filter_by(category="nightpants").all()
    return render_template("nightpants.html", nightpants=items)

@app.route("/product/<int:id>")
def product_details(id):
    product = Product.query.get_or_404(id)

    return render_template(
        "product_details.html",
        product=product
    )

@app.route("/search")
def search():

    query = request.args.get("query")
    category = request.args.get("category")

    products = Product.query

    if query:
        products = products.filter(
            Product.name.ilike(f"%{query}%")
        )

    if category and category != "All":
        products = products.filter(
            Product.category == category
        )


    products = products.all()

    return render_template(
        "index.html",
        products=products
    )

@app.route("/delete/<int:id>")
def delete_product(id):
    product = Product.query.get_or_404(id)

    db.session.delete(product)
    db.session.commit()

    return redirect("/admin")


# -----Admin Routes -----

@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")
    
    products = Product.query.all()
    return render_template("admin.html", products=products)

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():

    if request.method == "POST":

        name = request.form["name"]
        price = int(request.form["price"])
        category = request.form["category"]

        file = request.files["image"]

        filename = ""

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        product = Product(
            name     = name,
            price    = price,
            image    = filename,
            category = category
        )
        db.session.add(product)
        db.session.commit()

        return redirect(url_for("admin"))
    
    return render_template("admin_add.html")


@app.route("/admin/edit/<int:id>", methods=["GET", "POST"])
def admin_edit(id):
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        product.name     = request.form["name"]
        product.price    = int(request.form["price"])
        product.image    = request.form["image"]
        product.category = request.form["category"]
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("admin_edit.html", product=product)


@app.route("/admin/delete/<int:id>")
def admin_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("admin"))


# ----Login of Admin ------

@app.route("/login", methods=["GET", "POST"])
def login():

    # if already logged in --> go to admin
    if "user" in session:
        return redirect("/admin")

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # simple check (we'll improve later)
        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect("/admin")

    return render_template("login.html")

# ----logout of admin -----

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# Initialize database
with app.app_context():
    db.create_all()   # creates fashion.db if it doesn't exist
    seed_data()       # fills it with your products

if __name__ == "__main__":
    app.run(debug=True)