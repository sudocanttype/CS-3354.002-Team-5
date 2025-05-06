from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from mock_data import recipes_data, my_recipes
from decimal import Decimal
from datetime import datetime
import boto3
import hashlib
import time
import random
import string
import stripe
import os
from datetime import timedelta
from boto3.dynamodb.conditions import Attr, Key
import uuid 
from urllib.parse import unquote
from dotenv import load_dotenv
load_dotenv()


#Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

app = Flask(__name__)
app.secret_key = 'PKkqBBiNrVDTQtUc5oxd0zMUD3/qpvINvefbmlTt'
app.permanent_session_lifetime = timedelta(days=1)

# AWS DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # or your region
user_table = dynamodb.Table('Users')
products_table = dynamodb.Table('Products')
cart_table = dynamodb.Table('Cart')
orders_table = dynamodb.Table('Orders')


recipes_table = dynamodb.Table('RecipeActual')
generate_recipe_table = dynamodb.Table('GenerateRecipes')


@app.route('/')
def landingpage():
    user_logged_in = 'user' in session
    first_name = session.get('name')
    last_name = session.get('last_name')

    return render_template('landingwebpage.html', logged_in=user_logged_in, first_name=first_name, last_name=last_name)

# ----------------------
# LOGIN
# ----------------------
@app.route('/loginpage', methods=['GET', 'POST'])
def loginpage():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        try:
            response = user_table.get_item(Key={'username': username})
            user = response.get('Item')

            if user and user['password_hash'] == password:
                session['user'] = username
                session['name'] = user['name']
                session['last_name'] = user['last_name']
                session.permanent = True
                return redirect(url_for('landingpage'))

            else:
                error = "Invalid username and password. Please check your credentials."

                return render_template('loginpage.html', error=error)

        except Exception as e:
            return render_template('loginpage.html', error="Error logging in")

    return render_template('loginpage.html')

# ----------------------
# CREATE ACCOUNT
# ----------------------
@app.route('/createaccount', methods=['GET', 'POST']) #when you click "don't have an account? create one!" in login page
def createaccount():

    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return render_template('createaccount.html', error="Passwords do not match")

        #  Check if username already exists
        try:
            existing_user = user_table.get_item(Key={'username': username}).get('Item')

            if existing_user:
                return render_template('createaccount.html',
                                       error="Username already exists. Please choose another one.")
        except Exception as e:
            return render_template('createaccount.html', error=f"Error checking username: {e}")

        # Check for duplicate email
        try:
            email_check = user_table.scan(
                FilterExpression=Attr('email').eq(email)
            )

            if email_check['Items']:
                return render_template('createaccount.html', error="An account with this email already exists.")
        except Exception as e:
            return render_template('createaccount.html', error=f"Error checking email: {e}")

        # Save user
        hashed = hash_password(password)

        try:
            user_table.put_item(Item={
                'username': username,
                'name': name,
                'last_name': last_name,
                'email': email,
                'password_hash': hashed
            })
            session.permanent = True
            session['user'] = username
            session['name'] = name
            session['last_name'] = last_name

            return redirect(url_for('landingpage'))

        except Exception as e:
            return render_template('createaccount.html', error=f"Error creating account: {e}")

    return render_template('createaccount.html')

# ----------------------
# EDIT ACCOUNT
# ----------------------
@app.route('/editaccount', methods=['GET', 'POST'])
def editaccount():
    if 'user' not in session:
        return redirect(url_for('loginpage'))

    username = session['user']

    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password and password != confirm:
            return render_template('editaccount.html', error="Passwords do not match", user={
                'name': name,
                'last_name': last_name,
                'email': email
            })

        update_expr = "SET name = :n, last_name = :ln, email = :e"
        expr_vals = {
            ':n': name,
            ':ln': last_name,
            ':e': email
        }

        if password:
            update_expr += ", password_hash = :p"
            expr_vals[':p'] = hash_password(password)

        try:
            user_table.update_item(
                Key={'username': username},
                UpdateExpression="SET #n = :n, last_name = :ln, email = :e" + (
                    ", password_hash = :p" if password else ""),
                ExpressionAttributeValues={
                    ':n': name,
                    ':ln': last_name,
                    ':e': email,
                    **({':p': hash_password(password)} if password else {})
                },
                ExpressionAttributeNames={
                    '#n': 'name'  # <-- This is the fix
                }
            )

            # Update names in past orders, if different
            try:
                orders = orders_table.scan(
                    FilterExpression=Attr('username').eq(username)
                ).get('Items', [])

                for order in orders:
                    if 'personal_info' in order:
                        old_first = order['personal_info'].get('first_name')
                        old_last = order['personal_info'].get('last_name')

                        # Only update if the name actually changed
                        if old_first != name or old_last != last_name:
                            orders_table.update_item(
                                Key={
                                    'username': username,
                                    'order_id': order['order_id']
                                },
                                UpdateExpression='SET personal_info.#first = :fn, personal_info.#last = :ln',
                                ExpressionAttributeNames={
                                    '#first': 'first_name',
                                    '#last': 'last_name'
                                },
                                ExpressionAttributeValues={
                                    ':fn': name,
                                    ':ln': last_name
                                }
                            )
            except Exception as e:
                print(
                    f"Warning: Failed to update personal_info in Orders: {e}")  # error log for production issues

            session['name'] = name
            session['last_name'] = last_name
            return redirect(url_for('landingpage'))

        except Exception as e:
            return render_template('editaccount.html', error=f"Error updating account: {e}", user={
                'name': name,
                'last_name': last_name,
                'email': email
            })

    # GET method: populate form with current user data
    user = user_table.get_item(Key={'username': username}).get('Item')
    return render_template('editaccount.html', user=user)


# ----------------------
# LOGOUT
# ----------------------
@app.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('landingpage'))


@app.route('/shop')
def shop():
    if 'user' not in session:
        flash("You must be logged in to access the shop")

        return redirect(url_for('loginpage'))

    username = session['user']
    response = products_table.scan()
    products = response['Items']  # Pulled from DynamoDB

    cart_response = cart_table.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    cart_items = cart_response.get('Items', [])
    total_quantity = sum(item['quantity'] for item in cart_items)


    first_name = session.get('name')
    last_name = session.get('last_name')

    return render_template('grocerystorepage.html', products=products, first_name=first_name, last_name=last_name, cart_count=total_quantity)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return jsonify({'message': 'Please log in first'}), 403

    data = request.get_json()
    username = session['user']
    product_id = int(data['product_id'])
    quantity = int(data['quantity'])
    product = products_table.get_item(Key={'product_id': product_id}).get('Item')
    name = product['name']
    price = product['price']
    image = product['image']

    try:
        cart_table.put_item(Item={
            'username': username,
            'product_id': product_id,
            'name': name,
            'quantity': quantity,
            'price': Decimal(str(price)),
            'image': image,
            'added_at': str(int(time.time()))
        })

        return jsonify({'message': f'Added {quantity} of item {product_id} to your cart!'})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
@app.route('/checkout')
def checkout():
    if 'user' not in session:
        flash("You must be logged in to access checkout")

        return redirect(url_for('loginpage'))

    username = session['user']

    # Get all items from the Cart table for this user
    response = cart_table.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    cart_items = response.get('Items', [])

    total_items = sum(int(item['quantity']) for item in cart_items)

    # Calculate subtotal
    subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
    tax = 5.00
    convenience_fee = 1.00
    total = subtotal + tax + convenience_fee

    first_name = session.get('name')
    last_name = session.get('last_name')

    return render_template('checkout.html',subtotal=subtotal, tax=tax, convenience_fee=convenience_fee, total=total, cart_items=cart_items, total_items=total_items, first_name=first_name, last_name=last_name)

@app.route('/update_quantity', methods=['PATCH'])
def update_quantity():
    if 'user' not in session:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    username = session['user']
    product_id = int(data['product_id'])
    new_qty = int(data['quantity'])

    try:
        cart_table.update_item(
            Key={'username': username, 'product_id': product_id},
            UpdateExpression="SET quantity = :q",
            ExpressionAttributeValues={':q': new_qty}
        )

        return jsonify({'message': 'Quantity updated successfully'})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/remove_from_cart', methods=['DELETE'])
def remove_from_cart():
    if 'user' not in session:
        return jsonify({'message': 'Not authorized'}), 403

    data = request.get_json()
    username = session['user']
    product_id = int(data['product_id'])

    try:
        cart_table.delete_item(
            Key={
                'username': username,
                'product_id': product_id
            }
        )

        return jsonify({'message': 'Item removed from cart'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 403

    data = request.get_json()
    personal = data.get('personal')
    payment = data.get('payment')
    username = session['user']
    order_id = generate_order_number()

    # Get current user's cart
    cart_items = cart_table.query(
        KeyConditionExpression=Key('username').eq(username)
    ).get('Items', [])

    # Calculate total
    subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
    tax = 5.00
    convenience_fee = 1.00
    total = subtotal + tax + convenience_fee

    try:
        # Verify payment with Stripe
        payment_intent_id = payment.get('payment_intent_id')
        if not payment_intent_id:
            return jsonify({"error": "Payment information is incomplete"}), 400

        # Retrieve the payment intent from Stripe to verify its status
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        # Ensure payment was successful
        if payment_intent.status != 'succeeded':
            return jsonify({"error": f"Payment not completed. Status: {payment_intent.status}"}), 400

        # Store only necessary payment information (not card details)
        safe_payment_info = {
            'payment_intent_id': payment_intent_id,
            'payment_method': payment.get('payment_method'),
            'payment_status': payment_intent.status,
            'billing_name': f"{payment.get('cc_first_name')} {payment.get('cc_last_name')}",
            'billing_address': payment.get('cc_address')
        }

        # Save order to database
        orders_table.put_item(Item={
            'order_id': order_id,
            'username': username,
            'personal_info': personal,
            'payment_info': safe_payment_info,
            'cart_items': cart_items,
            'subtotal': Decimal(str(subtotal)),
            'tax': Decimal(str(tax)),
            'convenience_fee': Decimal(str(convenience_fee)),
            'total_paid': Decimal(str(total)),
            'timestamp': int(time.time())
        })

        # Clear the cart after saving the order
        for item in cart_items:
            cart_table.delete_item(
                Key={'username': username, 'product_id': item['product_id']}
            )

        return jsonify({"orderNumber": order_id})
    except stripe.error.StripeError as se:
        return jsonify({"error": f"Payment verification failed: {str(se)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_order_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        amount = int(data['amount'])  # in cents $10 = 1000

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            automatic_payment_methods={"enabled": True}
        )

        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/myorders')
def myorders():
    if 'user' not in session:
        flash("You must be logged to view your orders")
        return redirect(url_for('loginpage'))

    username = session['user']
    response = orders_table.scan(
        FilterExpression=Attr('username').eq(username)
    )
    orders = response.get('Items', [])
    return render_template('myorders.html', orders=orders)

@app.template_filter('datetime')
def format_datetime(value):
    if isinstance(value, Decimal):
        value = float(value)
    return datetime.fromtimestamp(value).strftime('%Y-%m-%d %I:%M %p')

@app.route('/cart_total_items')
def cart_total_items():
    cart = session.get("cart", [])
    total_items = sum(item["quantity"] for item in cart)
    return jsonify(total_items=total_items)

@app.route('/cart')
def get_cart():
    if 'user' not in session:
        return jsonify({'items': []})

    username = session['user']
    response = cart_table.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    items = response.get('Items', [])

    return jsonify({'items': items})



# ----------------------
# My Recipes
# ----------------------
@app.route('/myrecipes') # when "My Recipes" button is clicked redirected to recipes page
def myrecipes():
    if 'user' not in session:
        flash("You must be logged to view recipes page")
        return redirect(url_for('loginpage'))

    username = session['user']

    response = recipes_table.query(
        KeyConditionExpression=Key('username').eq(username)
    )

    recipes = response.get('Items', [])

    # remove recipes based on recipeId
    seen = set()
    unique_recipes = []

    for r in recipes:
        rid = str(r['recipeId'])  # normalize to string

        if rid not in seen:
            # ensure each recipe has a title field
            if 'title' not in r and 'recipe_title' in r:
                r['title'] = r['recipe_title']
            elif 'recipe_title' not in r and 'title' in r:
                r['recipe_title'] = r['title']
            # set default title if no exist
            elif 'title' not in r and 'recipe_title' not in r:
                r['title'] = "Untitled Recipe"
                r['recipe_title'] = "Untitled Recipe"

            unique_recipes.append(r)
            seen.add(rid)
    recipes = unique_recipes

    # Get favorite recipe IDs from the user's record
    user_data = user_table.get_item(Key={'username': username})
    favorite_ids = (set(user_data['Item'].get('favorites', [])))

    for i in range(len(recipes)):
        if str(recipes[i]["recipeId"]) in favorite_ids:
            recipes[i]['favorite'] = True
        else:
            recipes[i]['favorite'] = False

    favorite_ids = list(favorite_ids)

    # Pass recipes to the template
    user_logged_in = 'user' in session
    first_name = session.get('name')
    last_name = session.get('last_name')
    return render_template('recipes.html', recipes=recipes, username=username, favorite_ids=favorite_ids, logged_in=user_logged_in, first_name=first_name, last_name=last_name)

@app.route('/aboutus')
def aboutus():
    user_logged_in = 'user' in session
    first_name = session.get('name')
    last_name = session.get('last_name')


    return render_template('aboutus.html', logged_in=user_logged_in, first_name=first_name, last_name=last_name)

@app.route('/createrecipe') # displays the create recipe form
def create_recipe():
    return render_template('createrecipe.html')

@app.route('/save_recipe', methods=['POST']) # handles submission of new recipe form
def save_recipe():
    if 'user' not in session:
        flash("Please log in to save recipes.")
        return redirect(url_for('loginpage'))

    username = session['user']
    # generate a unique recipe ID based on time
    recipe_id = int(time.time() * 1000)

    try:
        # get data from form
        title = request.form.get('title')
        ingredients = request.form.getlist('ingredients')
        # collect instructions it assumes inputs are named instruction-1, instruction-2..
        instructions = []
        i = 1
        while True:
            instruction = request.form.get(f'instruction-{i}')
            if instruction is None:
                # check for other instruction keys in case missing sequential ones
                all_instr_keys = [k for k in request.form if k.startswith('instruction-')]
                if not all_instr_keys and i > 1: break 
                elif not all_instr_keys: break  
                else: pass  
            if instruction is not None: 
                instructions.append(instruction)
            i += 1
            if i > 50: break  

        prep_time = request.form.get('prep_time', type=int) 
        cook_time = request.form.get('cook_time', type=int) 
        serving_size = request.form.get('serving_size', type=int) 
        tags = request.form.getlist('tags')
        # placeholder for image
        image_url = request.form.get('image_url', 'https://via.placeholder.com/150')

        if not title or not ingredients or not instructions:
             flash("Title, ingredients, and instructions are required.")
             return redirect(url_for('myrecipes'))

        #for DynamoDB
        recipe_item = {
            'username': username,
            'recipeId': recipe_id,
            'title': title,
            'recipe_title': title,  # set both title and recipe_title to the same value
            'ingredients': ingredients,
            'instructions': instructions,
            'image': image_url,
            **( {'prep_time': prep_time} if prep_time is not None else {} ),
            **( {'cook_time': cook_time} if cook_time is not None else {} ),
            **( {'serving_size': serving_size} if serving_size is not None else {} ),
            **( {'tags': tags} if tags else {} )
        }

        # save to DynamoDB
        recipes_table.put_item(Item=recipe_item)
        flash(f"Recipe '{title}' created successfully!")

    except Exception as e:
        flash(f"Error saving recipe: {str(e)}")

    return redirect(url_for('myrecipes'))

@app.route('/edit_recipe/<int:recipe_id>')
def edit_recipe(recipe_id):
    if 'user' not in session:
        flash("Please log in to edit recipes.")
        return redirect(url_for('loginpage'))

    username = session['user']

    preview_recipe = session.get('preview_recipe')
    if preview_recipe and preview_recipe.get('recipeId') == recipe_id:
        recipe_data = {
            'id': preview_recipe.get('recipeId'),
            'title': preview_recipe.get('title', ''),
            'image': preview_recipe.get('image', 'https://via.placeholder.com/150'),
            'ingredients': preview_recipe.get('ingredients', []),
            'instructions': preview_recipe.get('instructions', []),
            'prep_time': preview_recipe.get('prep_time'),
            'cook_time': preview_recipe.get('cook_time'),
            'serving_size': preview_recipe.get('serving_size'),
            'tags': preview_recipe.get('tags', []),
            'preview_mode': True
        }
        return render_template('editingpage.html', recipe=recipe_data)

    try:
        # fetch specific recipe from DynamoDB using the integer recipe_id
        response = recipes_table.get_item(
            Key={'username': username, 'recipeId': recipe_id} 
        )
        recipe = response.get('Item')

        if not recipe:
            flash("Recipe not found or you don't have permission to edit it.")
            return redirect(url_for('myrecipes'))

        # pass fetched recipe data to template
        recipe_data = {
            'id': recipe.get('recipeId'), 
            'title': recipe.get('title', ''),
            'image': recipe.get('image', 'https://via.placeholder.com/150'),
            'ingredients': recipe.get('ingredients', []),
            'instructions': recipe.get('instructions', []),
            'prep_time': recipe.get('prep_time'),
            'cook_time': recipe.get('cook_time'),
            'serving_size': recipe.get('serving_size'),
            'tags': recipe.get('tags', [])
        }



        return render_template('editingpage.html', recipe=recipe_data)

    except Exception as e:
        flash(f"Error loading recipe for editing: {str(e)}")
        # Check if the error is the schema mismatch again
        print(f"Error fetching recipe {recipe_id} for user {username}: {e}")
        if 'ValidationException' in str(e) and 'does not match the schema' in str(e):
            print("SCHEMA MISMATCH: edit_recipe received an ID that doesn't match RecipeActual's recipeId type (expected Number). Ensure the link generating this URL passes an integer.")
        return redirect(url_for('myrecipes'))


@app.route('/view_recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    if 'user' not in session:
        flash("Please log in to view recipes.")
        return redirect(url_for('loginpage'))

    username = session['user']
    
    preview_recipe = session.get('preview_recipe')
    if preview_recipe and preview_recipe.get('recipeId') == recipe_id:
        recipe_data = {
            'id': preview_recipe.get('recipeId'),
            'title': preview_recipe.get('title', ''),
            'image': preview_recipe.get('image', 'https://via.placeholder.com/150'),
            'ingredients': preview_recipe.get('ingredients', []),
            'instructions': preview_recipe.get('instructions', []),
            'prep_time': preview_recipe.get('prep_time'),
            'cook_time': preview_recipe.get('cook_time'),
            'serving_size': preview_recipe.get('serving_size'),
            'tags': preview_recipe.get('tags', []),
            'preview_mode': True
        }
        return render_template('viewingpage.html', recipe=recipe_data)

    try:
        # fetch specific recipe from DynamoDB using the integer recipe_id
        response = recipes_table.get_item(
            Key={'username': username, 'recipeId': recipe_id} 
        )
        recipe = response.get('Item')

        if not recipe:
            flash("Recipe not found or you don't have permission to view it.")
            return redirect(url_for('myrecipes'))

        # pass fetched recipe data to template
        recipe_data = {
            'id': recipe.get('recipeId'), 
            'title': recipe.get('title', ''),
            'image': recipe.get('image', 'https://via.placeholder.com/150'),
            'ingredients': recipe.get('ingredients', []),
            'instructions': recipe.get('instructions', []),
            'prep_time': recipe.get('prep_time'),
            'cook_time': recipe.get('cook_time'),
            'serving_size': recipe.get('serving_size'),
            'tags': recipe.get('tags', [])
        }

        return render_template('viewingpage.html', recipe=recipe_data)

    except Exception as e:
        flash(f"Error loading recipe for viewing: {str(e)}")
        # Check if the error is the schema mismatch again
        print(f"Error fetching recipe {recipe_id} for user {username}: {e}")
        if 'ValidationException' in str(e) and 'does not match the schema' in str(e):
            print("SCHEMA MISMATCH: view_recipe received an ID that doesn't match RecipeActual's recipeId type (expected Number). Ensure the link generating this URL passes an integer.")
        return redirect(url_for('myrecipes'))

@app.route('/update_recipe/<int:recipe_id>', methods=['POST'])
def update_recipe(recipe_id):

    if 'user' not in session:
        flash("Please log in to update recipes.")
        return redirect(url_for('loginpage'))

    username = session['user']

    title = request.form.get('title')

    ingredients = request.form.getlist('ingredients')

    instructions = []
    i = 1
    while True:
        instruction = request.form.get(f'instruction-{i}')
        if instruction is None:
            all_instr_keys = [k for k in request.form if k.startswith('instruction-')]
            if not all_instr_keys and i > 1: break 
            elif not all_instr_keys: break  
            else: pass  
        if instruction is not None: 
            instructions.append(instruction)
        i += 1
        if i > 50: break  

    prep_time = request.form.get('prep_time', type=int)

    cook_time = request.form.get('cook_time', type=int)

    serving_size = request.form.get('serving_size', type=int)

    tags = request.form.getlist('tags')

    image_url = request.form.get('image_url', 'https://via.placeholder.com/150')

    # Basic validation
    if not title:
        flash("Recipe title is required.")
        return redirect(url_for('edit_recipe', recipe_id=recipe_id))

    preview_recipe = session.get('preview_recipe')
    if preview_recipe and preview_recipe.get('recipeId') == recipe_id:

        try:
            # create a new recipe item for DynamoDB
            new_recipe_id = int(time.time() * 1000)  
            recipe_item = {
                'username': username,
                'recipeId': new_recipe_id,
                'title': title,
                'recipe_title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'image': image_url,
                **( {'prep_time': prep_time} if prep_time is not None else {} ),
                **( {'cook_time': cook_time} if cook_time is not None else {} ),
                **( {'serving_size': serving_size} if serving_size is not None else {} ),
                **( {'tags': tags} if tags else {} )
            }

            # save to DynamoDB
            recipes_table.put_item(Item=recipe_item)
            flash(f"Recipe '{title}' saved to your collection!")

            # remove preview recipe from session
            session.pop('preview_recipe', None)

            return redirect(url_for('myrecipes'))

        except Exception as e:
            flash(f"Error saving recipe: {str(e)}")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))

    try:
        # first verify the recipe exists
        check_response = recipes_table.get_item(
            Key={
                'username': username,
                'recipeId': recipe_id
            }
        )
        recipe_exists = 'Item' in check_response

        if not recipe_exists:
            flash("Recipe not found. Cannot update a recipe that doesn't exist.")
            return redirect(url_for('myrecipes'))


        if not ingredients or not instructions:
            flash("Ingredients and instructions are required.")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))

        # prepare update expression and attribute values
        update_expression = "SET title = :t, recipe_title = :t, ingredients = :ing, instructions = :ins"
        expression_attribute_values = {
            ':t': title,
            ':ing': ingredients,
            ':ins': instructions
        }

        #add image if provided
        if image_url and image_url != 'https://via.placeholder.com/150':
            update_expression += ", image = :img"
            expression_attribute_values[':img'] = image_url

        # Add optional fields to update expression only if they have values
        if prep_time is not None: 
            update_expression += ", prep_time = :pt"
            expression_attribute_values[':pt'] = prep_time
        if cook_time is not None: 
            update_expression += ", cook_time = :ct"
            expression_attribute_values[':ct'] = cook_time
        if serving_size is not None: 
            update_expression += ", serving_size = :ss"
            expression_attribute_values[':ss'] = serving_size

        #update tags, empty list is valid
        update_expression += ", tags = :tg"
        expression_attribute_values[':tg'] = tags if tags else []


        # update item in DynamoDB using the integer recipe_id
        update_response = recipes_table.update_item(
            Key={
                'username': username,
                'recipeId': recipe_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'  # Return the updated item
        )


        if 'Attributes' in update_response:
            flash(f"Recipe '{title}' updated successfully!")
        else:
            flash(f"Recipe '{title}' updated successfully!")

    except Exception as e:
        flash(f"Error updating recipe: {str(e)}")
        return redirect(url_for('edit_recipe', recipe_id=recipe_id))

    return redirect(url_for('myrecipes'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if 'user' not in session:
        flash("You must be logged in to access generate recipe page")
        return redirect(url_for('loginpage'))


    substitutions = {
        'egg': '1/4 Cup Applesauce or Mashed Banana',
        'milk': 'Almond Milk or Oat Milk',
        'butter': 'Coconut Oil or Olive Oil',
        'flour': 'Almond Flour or Oat Flour',
        'sugar': 'Honey or Maple Syrup'
    }

    suggested_subs = {}

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':  #add to my collection button
            if 'user' not in session:
                return redirect(url_for('loginpage'))

            username = session['user']
            recipe_title = request.form.get('recipe_title')

            if not recipe_title:
                return jsonify({'status': 'error', 'message': 'Missing recipe title'}), 400

            #get recipe from generate recipes table
            response = generate_recipe_table.get_item(Key={'recipe_title': recipe_title})
            recipe = response.get('Item')

            if not recipe:
                return jsonify({'status': 'error', 'message': 'Recipe not found'}), 404

            recipe['username'] = username
            
            if 'recipe_title' in recipe and ('title' not in recipe or not recipe['title']):
                recipe['title'] = recipe['recipe_title']
                
            recipes_table.put_item(Item=recipe)  #add to my recipes (recipes actual table)

            return jsonify({'status': 'success', 'message': 'Recipe added'})

        if action == 'search':  #search for recipe by name/ingredients
            if 'user' not in session:
                return redirect(url_for('loginpage'))

            search_name = request.form.get('query', '').strip()
            ingredients_given = request.form.get('ingredients_search', '').strip().lower()

            filter_exp = Attr('recipe_title').contains(search_name)
            response = generate_recipe_table.scan(FilterExpression=filter_exp)
            recipes = response.get('Items', [])

            if ingredients_given: #filter by ingredients too if given
                ingredients_list = [item.strip().lower() for item in ingredients_given.split(',') if item.strip()]
                filtered_recipes = []

                for r in recipes:
                    matched = []
                    unmatched = []

                    for db_ing in r.get('ingredients', []):
                        db_ing_lower = db_ing.lower()
                        matched_flag = False

                        for input_ing in ingredients_list:
                            if input_ing in db_ing_lower:
                                matched.append(db_ing)
                                matched_flag = True
                                break

                        if not matched_flag:
                            unmatched.append(db_ing)

                    if matched:   #keep track of matched & unmatched recipes
                        r['matched_ingredients'] = matched
                        r['unmatched_ingredients'] = unmatched
                        filtered_recipes.append(r)

                recipes = filtered_recipes 

            return render_template('generaterecipe.html', result=recipes)
        elif action == 'subs':
            ingredients_input = request.form['ingredients']
            ingredients = [i.strip().lower() for i in ingredients_input.split(',')]

            for item in ingredients:
                if item in substitutions:
                    suggested_subs[item] = substitutions[item]
                elif item.endswith('s'):
                    singular = item[:-1]

                    if singular in substitutions:
                        suggested_subs[item] = substitutions[singular]

            return render_template('generaterecipe.html', suggestions=suggested_subs, ingredients=ingredients_input)

    return render_template('generaterecipe.html')

@app.route('/favorite', methods=['POST'])
def toggle_favorite():
    data = request.json
    username = data.get('username')
    recipeId = data.get('recipeId')

    if not username or not recipeId:
        return jsonify({'error': 'Missing username or recipeId'}), 400

    try:
        # Get user
        response = user_table.get_item(Key={'username': username})
        user = response.get('Item')

        if not user:
            return jsonify({'error': 'User not found'}), 404

        favorites = user.get('favorites', [])

        if recipeId in favorites:
            favorites.remove(recipeId)
            message = "Recipe unfavorited!"
        else:
            favorites.append(recipeId)
            message = "Recipe favorited!"

        # Update the user's favorites
        user_table.update_item(
            Key={'username': username},
            UpdateExpression='SET favorites = :favs',
            ExpressionAttributeValues={':favs': favorites}
        )

        return jsonify({'message': message, 'favorites': favorites})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_and_edit_recipe/<string:recipe_title>')
def add_and_edit_recipe(recipe_title):
    if 'user' not in session:
        flash("Please log in to add and edit recipes.")
        return redirect(url_for('loginpage'))

    username = session['user']
    decoded_title = unquote(recipe_title)

    try:
        #check if recipe with this title already exists for the user in RecipeActual
        existing_response = recipes_table.query(
            KeyConditionExpression=Key('username').eq(username),
            FilterExpression=Attr('title').eq(decoded_title)
        )
        existing_items = existing_response.get('Items', [])

        if existing_items:
            #if exists redirect to edit the existing recipe
            existing_recipe_id = existing_items[0]['recipeId'] # Get ID from first match
            flash(f"Recipe '{decoded_title}' is already in your collection. Editing existing version.")
            return redirect(url_for('edit_recipe', recipe_id=existing_recipe_id))
        else:
            #if not exists fetch it but don't save it to collection yet
            response = generate_recipe_table.get_item(Key={'recipe_title': decoded_title})
            original_recipe = response.get('Item')

            if not original_recipe:
                flash(f"Recipe titled '{decoded_title}' not found in the generation database.")
                return redirect(url_for('generate'))

            #generate a temporary ID for preview
            temp_recipe_id = int(time.time() * 1000)  

            #create the preview recipe
            preview_recipe = {
                'username': username,
                'recipeId': temp_recipe_id,
                'title': original_recipe.get('recipe_title'),
                'recipe_title': original_recipe.get('recipe_title'),
                'ingredients': original_recipe.get('ingredients', []),
                'instructions': original_recipe.get('instructions', []),
                'image': original_recipe.get('image', original_recipe.get('img_url', 'https://via.placeholder.com/150')),
                'preview_mode': True  # Flag to identify this as a preview
            }

            if 'prep_time' in original_recipe and original_recipe['prep_time'] is not None:
                try:
                    preview_recipe['prep_time'] = int(original_recipe['prep_time'])
                except (ValueError, TypeError):
                    preview_recipe['prep_time'] = original_recipe['prep_time']

            if 'cook_time' in original_recipe and original_recipe['cook_time'] is not None:
                try:
                    preview_recipe['cook_time'] = int(original_recipe['cook_time'])
                except (ValueError, TypeError):
                    preview_recipe['cook_time'] = original_recipe['cook_time']

            if 'serving_size' in original_recipe and original_recipe['serving_size'] is not None:
                try:
                    preview_recipe['serving_size'] = int(original_recipe['serving_size'])
                except (ValueError, TypeError):
                    preview_recipe['serving_size'] = original_recipe['serving_size']

            if 'tags' in original_recipe:
                preview_recipe['tags'] = original_recipe['tags']

            if 'rating' in original_recipe:
                preview_recipe['rating'] = original_recipe['rating']

            session['preview_recipe'] = preview_recipe

            flash(f"Previewing '{preview_recipe.get('title', '[No Title]')}'. Click 'Save Recipe' to add to your collection.")

            return redirect(url_for('edit_recipe', recipe_id=temp_recipe_id))

    except Exception as e:
        flash(f"Error processing recipe request: {str(e)}")
        return redirect(url_for('generate')) # Redirect back to generate page on error

@app.route('/delete_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    if 'user' not in session:
        flash("Please log in to delete recipes.")
        return redirect(url_for('loginpage'))

    username = session['user']


    try:
        # first verify the recipe exists
        check_response = recipes_table.get_item(
            Key={
                'username': username,
                'recipeId': recipe_id
            }
        )
        recipe_exists = 'Item' in check_response

        if not recipe_exists:
            flash("Recipe not found. It may have been deleted already.")
            return redirect(url_for('myrecipes'))

        # recipe exists, proceed with deletion
        delete_response = recipes_table.delete_item(
            Key={
                'username': username,
                'recipeId': recipe_id
            },
            ReturnValues='ALL_OLD'
        )


        if 'Attributes' in delete_response:
            recipe_title = delete_response['Attributes'].get('title', 'Unknown')
            flash(f"Recipe '{recipe_title}' was deleted successfully!")
        else:
            flash("Recipe was deleted successfully!")

    except Exception as e:
        flash(f"Error deleting recipe: {str(e)}")
        return redirect(url_for('myrecipes'))

    return redirect(url_for('myrecipes'))

if __name__ == '__main__':
    app.run(debug=True)
