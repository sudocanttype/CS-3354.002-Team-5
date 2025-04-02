from flask import Flask, render_template, request, redirect, url_for
from models import Product

app = Flask(__name__)

# Dummy data
products = [
    Product(1, "Pear", "A sweet, juicy fruit that grows on trees", 1.99, "pear.png"),
    Product(2, "Apple", "A round fruit that grows on apple trees", 1.99, "apple.jpg"),
    Product(3, "Chicken", "A lean, white poultry meat", 7.99, "chicken.jpg"),
    Product(4, "Watermelon", "A large, juicy fruit with red flesh", 5.99, "watermelon.jpg"),
]


@app.route('/')
def landingpage():  # homepage of application
    return render_template('practicelandingwebpage.html')



@app.route('/loginpage') # when "Get Started" button is clicked redirected to login page
def loginpage():
    return render_template('loginpage.html')

@app.route('/shop')
def shop():
    return render_template('grocerystorepage.html', products=products)

@app.route('/checkout')
def checkout():
    cart_items = []
    return render_template('checkout.html', cart_items=cart_items)

if __name__ == '__main__':
    app.run()
