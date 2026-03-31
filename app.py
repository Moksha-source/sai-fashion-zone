from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/shirts")
def shirts():

    shirts_data = [
        {
            "name": "Formal Shirt",
            "price": 799,
            "image": "formal_shirt.jpeg"
        },
        {
            "name": "Printed Shirt",
            "price": 699,
            "image": "printed_shirt.jpeg"
        },
        {
            "name": "Check Shirt",
            "price": 899,
            "image": "check_shirt.jpeg"
        }
    ]

    return render_template(
        "shirts.html",
        shirts=shirts_data
    )

@app.route("/pants")
def pants():
    return  render_template("pants.html")

@app.route("/tshirts")
def tshirts():
    return render_template("tshirts.html")

@app.route("/nightpants")
def nightpants():
    return render_template("nightpants.html")

if __name__ == "__main__":
    app.run(debug=True)