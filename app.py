
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


from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# sample recipe dta
sample_recipe = {
    'id': 1,
    'title': 'Honey Cake',
    'image': '/static/images/recipes/honey-cake.png',
    'ingredients': [
        {'name': 'Honey', 'image': '/static/images/ingredients/honey.png'},
        {'name': 'Flour', 'image': '/static/images/ingredients/flour.png'},
        {'name': 'Eggs', 'image': '/static/images/ingredients/egg.png'}
    ],
    'instructions': ['Whisk dry ingredients', 'Cream butter and honey'],
    'prep_time': 30,
    'cook_time': 45,
    'serving_size': 1,
    'tags': ['Dairy']
}


@app.route('/')
def landingpage():
    return render_template('practicelandingwebpage.html')

@app.route('/loginpage')
def loginpage():
    return render_template('loginpage.html')


@app.route('/shop')
def shop():
    return render_template('grocerystorepage.html', products=products)

@app.route('/checkout')
def checkout():
    cart_items = []
    return render_template('checkout.html', cart_items=cart_items)

@app.route('/myrecipes') # when "My Recipes" button is clicked redirected to recipes page
def myrecipes():
    return render_template('recipes.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/recipes')
def recipes_list():
    recipes = {1: sample_recipe}
    return render_template('recipes_list.html', recipes=recipes)

@app.route('/recipes/create')
def create_recipe():
    return render_template('recipe_form.html', 
                          is_edit_mode=False, 
                          recipe={}, 
                          form_action='/recipes/create')

@app.route('/recipes/<int:recipe_id>/edit')
def edit_recipe(recipe_id):
    return render_template('recipe_form.html', 
                          is_edit_mode=True, 
                          recipe=sample_recipe, 
                          form_action=f'/recipes/{recipe_id}/edit')

from flask import request

@app.route('/generate', methods=['GET', 'POST']) #generate recipe suggestions using user's input
def generate():
    substitutions = { #list of possible substitutions if user  is misiing ingredients 
        'egg': '1/4 Cup Applesauce or Mashed Banana',
        'milk': 'Almond Milk or Oat Milk',
        'butter': 'Coconut Oil or Olive Oil',
        'flour': 'Almond Flour or Oat Flour',
        'sugar': 'Honey or Maple Syrup'
    }
    
    suggested_subs= {}
    bs = {} #store substitutions
    #get or recieve ingredients with POST
    if request.method == 'POST':
        ingredients_input = request.form['ingredients']
        ingredients = [i.strip().lower() for i in ingredients_input.split(',')]  #this line converts list to all lowercase

        #Check for match

        for item in ingredients:   # Tryy for the exact match first
            if item in substitutions:
                suggested_subs[item] = substitutions[item]    # Try for the  singular form if plural
            elif item.endswith('s'):

                singular = item[:-1]
                if singular in substitutions:
                    suggested_subs[item] = substitutions[singular]

        return render_template('generaterecipe.html', suggestions=suggested_subs, ingredients=ingredients_input)

    return render_template('generaterecipe.html')



@app.route('/createaccount') #when you click "dont have an account? create one!" in login page
def createaccount():
    return render_template('createaccount.html')


if __name__ == '__main__':
    app.run(debug=True)
