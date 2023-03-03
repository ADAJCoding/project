from flask import render_template,redirect,session, flash, request, url_for
from flask_app import app
from flask_app.models.product import Product
from flask_app.models.user import User
from flask_app.models.order import Order
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Define the menu items and their prices
cakes = [
    {'id': 1,'category': 'cake', 'dessert': 'Chocolate Cake', 'price': 30,'image':""},
    {'id': 2,'category': 'cake', 'dessert': 'Vanilla Cake', 'price': 25,'image':""},
    {'id': 3,'category': 'cake', 'dessert': 'Carrot Cake', 'price': 35,'image':""},
    {'id': 4,'category': 'cake', 'dessert': 'Red Velvet Cake', 'price': 35,'image':""},
    {'id': 5,'category': 'cake', 'dessert': 'Coconut Cake', 'price': 40,'image':""},
]

cupcakes = [
    {'id': 6,'category': 'cupcake', 'dessert': 'Vanilla Cupcake', 'price': 3,'image':""},
    {'id': 7,'category': 'cupcake', 'dessert': 'Chocolate Cupcake', 'price': 3,'image':""},
    {'id': 8, 'category': 'cupcake','dessert': 'Red Velvet Cupcake', 'price': 3.50,'image':""},
    {'id': 9,'category': 'cupcake', 'dessert': 'Carrot Cupcake', 'price': 3.50,'image':""},
    {'id': 10,'category': 'cupcake', 'dessert': 'Lemon Cupcake', 'price': 3,'image':""},
]

cookies = [
    {'id': 11,'category': 'cookie', 'dessert': 'Chocolate Chip Cookie', 'price': 2,'image':""},
    {'id': 12,'category': 'cookie', 'dessert': 'Oatmeal Raisin Cookie', 'price': 2,'image':""},
    {'id': 13,'category': 'cookie', 'dessert': 'Sugar Cookie', 'price': 2,'image':""},
    {'id': 14, 'category': 'cookie','dessert': 'Snickerdoodle Cookie', 'price': 2,'image':""},
    {'id': 15,'category': 'cookie', 'dessert': 'Double Chocolate Cookie', 'price': 2,'image':""},
    
]


@app.route('/home')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    data ={
        'id': session['user_id']
    }
    user= User.get_by_id(data)
    return render_template('dashboard.html',user=user)


@app.route('/order/create', methods=['GET', 'POST'])
def order():
    cakes = Product.get_all_by_category('cakes')
    cupcakes = Product.get_all_by_category('cupcakes')
    cookies = Product.get_all_by_category('cookies')
    
    if request.method == 'POST':
        # Process the form data
        order_items = []
        for cake in cakes:
            quantity = request.form.get(f'cake_{cake["id"]}', 0)
            if quantity:
                order_items.append({'dessert': cake['dessert'], 'quantity': int(quantity), 'price': cake['price']})
        for cupcake in cupcakes:
            quantity = request.form.get(f'cupcake_{cupcake["id"]}', 0)
            if quantity:
                order_items.append({'dessert': cupcake['dessert'], 'quantity': int(quantity), 'price': cupcake['price']})
        for cookie in cookies:
            quantity = request.form.get(f'cookie_{cookie["id"]}', 0)
            if quantity:
                order_items.append({'dessert': cookie['dessert'], 'quantity': int(quantity), 'price': cookie['price']})
        total_price = sum(item['quantity'] * item['price'] for item in order_items)
        data ={
            'dessert': ' '.join([item['dessert'] for item in order_items]),
            'quantity': sum(item['quantity'] for item in order_items),
            'price': sum(item['quantity'] * item['price'] for item in order_items),
            'total_price': total_price,
            'user_id': session['user_id']
        }
        id = Order.save_order(data)
        user = User.get_by_id({'id': session['user_id']})
        
        # Filter out items with quantity 0
        items = [item for item in order_items if item['quantity'] > 0]
        order = Order.get_one_order(id)
        # Render the order confirmation page
        return render_template('order.html', items=items, total_price=total_price, user=user, order=order)
    else:
        # Render the order form page
        user = User.get_by_id({'id': session['user_id']})
        return render_template('new_order.html', cakes=cakes, cupcakes=cupcakes, cookies=cookies, user=user)
    

@app.route('/order', methods=['POST'])
def order_confirmation():
    # Get the items and quantities from the form data
    items = []
    for item, price, quantity in request.form.items():
        # Convert the price and quantity to the correct data type
        price = float(price)
        quantity = int(quantity)
        # Add the item and quantity to the list of items
        items.append({'item': item, 'price': price, 'quantity': quantity})
    # Calculate the total order amount
    total = 0
    for item in items:
        price = item['price']
        quantity = item['quantity']
        total += price * quantity
    data ={
        'id': session['user_id']
    }
    user= User.get_by_id(data)
    # Render the order confirmation template with the order data
    return render_template('order.html', items=items, total=total,user=user)



@app.route('/order/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    if 'user_id' not in session:
        return redirect('/logout')
    order = Order.get_one_order(id)
    if not order:
        return redirect('/order/create')
    if request.method == 'POST':
        # Handle form submission
        return redirect('/order')
    data ={
        'id': session['user_id']
    }
    user= User.get_by_id(data)
    return render_template('edit_order.html', order=order, user=user)


@app.route('/order/update/<int:id>', methods=['POST'])
def update(id):
    if 'user_id' not in session:
        return redirect('/logout')
    order = Order.get_one_order(id)
    if not order:
        return "Order not found"
    order_items = order.order_items
    quantities = request.form.getlist('quantity')
    total_price = 0
    for i in range(len(order_items)):
        item = order_items[i]
        quantity = int(quantities[i])
        if quantity < 0:
            return "Invalid quantity"
        item.quantity = quantity
        total_price += item.price * quantity
    order.price = total_price
    order.save_order()
    return redirect('/order')


@app.route('/order/destroy/<int:id>', methods=['GET', 'POST', 'DELETE'])
def destroy(id):
    if request.method == 'GET':
        orders = Product.get_all()
        return render_template('order.html', orders=orders)
    elif request.method == 'POST':
        order = Product.get_one_order(id)
        if not order:
            return "Order not found"
        try:
            Product.delete({"id": id})
            print("Order deleted")
            return redirect('/home')
        except Exception as e:
            print(f"Error deleting order: {e}")
            return "Error deleting order"