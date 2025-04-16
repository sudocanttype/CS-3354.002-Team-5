from flask import Flask, jsonify, session, render_template, request, redirect, url_for
from mock_data import products, recipes_data, my_recipes
import boto3
import hashlib
from datetime import timedelta
from boto3.dynamodb.conditions import Attr, Key

app = Flask(__name__)
app.secret_key = 'PKkqBBiNrVDTQtUc5oxd0zMUD3/qpvINvefbmlTt'
app.permanent_session_lifetime = timedelta(days=1)

# AWS DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # or your region
user_table = dynamodb.Table('Users')
recipes_table = dynamodb.Table('RecipeActual')
# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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
            session['user'] = username
            session['name'] = name
            session['last_name'] = last_name
            return redirect(url_for('landingpage'))

        except Exception as e:
            return render_template('createaccount.html', error=f"Error creating account: {e}")

    return render_template('createaccount.html')

# ----------------------
# LOGOUT
# ----------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landingpage'))


@app.route('/shop')
def shop():
    return render_template('grocerystorepage.html', products=products)

@app.route('/checkout')
def checkout():
    cart_items = []
    return render_template('checkout.html', cart_items=cart_items)

@app.route('/myrecipes') # when "My Recipes" button is clicked redirected to recipes page
def myrecipes():
    if 'user' not in session:
        return redirect(url_for('loginpage'))
    
    username = session['user']

    response = recipes_table.query(
        KeyConditionExpression=Key('username').eq(username)
    )

    recipes = response.get('Items', [])

    # Pass recipes to the template
    return render_template('recipes.html', recipes=recipes, username=username)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/createrecipe') # displays the create recipe form
def create_recipe():
    return render_template('createrecipe.html')

@app.route('/save_recipe', methods=['POST']) # handles submission of new recipe form
def save_recipe():
    # todo: save the recipe data from the form to the database
    return redirect(url_for('myrecipes'))

@app.route('/edit_recipe/<int:recipe_id>') # displays form to edit an existing recipe
def edit_recipe(recipe_id):
    recipe = recipes_data.get(recipe_id)
    if not recipe:
        return redirect(url_for('myrecipes'))
        
    # format the recipe data for the template
    recipe_data = {
        'id': recipe.id,
        'title': recipe.nameOfRecipe,
        'image': recipe.image,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'prep_time': recipe.prep_time,
        'cook_time': recipe.cook_time,
        'serving_size': recipe.serving_size,
        'tags': recipe.tags
    }
    
    return render_template('editingpage.html', recipe=recipe_data)

@app.route('/update_recipe/<int:recipe_id>', methods=['POST']) # handles submission of edited recipe
def update_recipe(recipe_id):
    # todo: save the updated recipe data from the form to the database
    return redirect(url_for('myrecipes'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
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
        query = request.form.get('query', '').strip().lower()
        result = None
        
        if action == 'search':
            if(query == 'lemonade'):
                result = {
                    'title': 'Lemonade', 
                    'description': 'Refreshing drink' 
                }
            return render_template('generaterecipe.html', result=result)
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
def favorite_recipe():
    print("/favorite route was triggered")
    data = request.json
    username = data.get('username')
    recipeId = data.get('recipeId')

    print("Incoming data:", data)

    if not username or not recipeId:
        print("Missing username or recipeId")
        return jsonify({'error': 'Missing username or recipeId'}), 400

    try:
        response = user_table.get_item(Key={'username': username})
        user = response.get('Item')
        print("Retrieved user:", user)

        if not user:
            print("User not found")
            return jsonify({'error': 'User not found'}), 404

        favorites = user.get('favorites', [])
        if recipeId not in favorites:
            favorites.append(recipeId)
            print("New favorites list:", favorites)

            user_table.update_item(
                Key={'username': username},
                UpdateExpression='SET favorites = :favs',
                ExpressionAttributeValues={':favs': favorites}
            )
            print("DynamoDB update sent")
        else:
            print("Recipe already in favorites")

        return jsonify({'message': 'Recipe favorited!', 'favorites': favorites})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500
print("THIS FILE IS RUNNING")
if __name__ == '__main__':
    app.run(debug=True)
