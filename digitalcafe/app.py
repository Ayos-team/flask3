from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import session
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b'w33uwueed@!@'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html', page="Index")


@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)


@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)


@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)


@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))

    return render_template('branchdetails.html', code=code, branch=branch)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    database_username = db.get_username(username)
    database_password = db.get_pass(password)
    error = None

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    elif(database_username != username and database_password == password):
        error = 'Invalid username. Please try again.'
        return render_template('login.html', error=error)
    elif(database_username == username and database_password != password):
        error = 'Invalid password. Please try again.'
        return render_template('login.html', error=error)
    else:
        error = 'Invalid Credentials. Please try again.'
        return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("cart", None)
    return redirect('/')


@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item = dict()
    # A click to add a product translates to a
    # quantity of 1 for now
    item["code"] = code
    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"] * item["qty"]

    if(session.get("cart") is None):
        session["cart"] = {}

    cart = session["cart"]
    cart[code] = item
    session["cart"] = cart
    return redirect('/cart')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/addquantity', methods=['POST'])
def form_submission():
    #qty = request.form.getlist("qty")
    code = request.form.get('code', '')
    product = db.get_product(int(code))
    qty = int(request.form.get('qty'))

    cart = session["cart"]

    for item in cart.values():
        if item["code"] == code:
            item["qty"] = qty
            item["subtotal"] = product["price"] * item["qty"]
            cart = session["cart"]
            cart[code] = item
            session["cart"] = cart
    return render_template('cart.html', qty=qty, code=code, product=product)


@app.route('/removeproduct', methods=['POST'])
def removeproduct():
    #stype = request.form.get("stype")
    code = request.form.get('code', '')
    cart = session["cart"]
    del cart[code]
    session["cart"] = cart
    return redirect('cart')


@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')
