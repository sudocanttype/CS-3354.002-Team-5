from flask import Flask, render_template, request, redirect, url_for
from models import Product, Recipe, User, MyRecipes

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

@app.route('/createrecipe')
def create_recipe():
    return render_template('createrecipe.html')

recipes_data = {
    1: {
        'id': 1,
        'title': 'Lemonade',
        'image': '/static/images/recipes/lemonade.png',
        'ingredients': [
            {'name': 'Lemons', 'image': '/static/images/ingredients/lemon.png'},
            {'name': 'Sugar', 'image': '/static/images/ingredients/sugar.png'},
            {'name': 'Water', 'image': '/static/images/ingredients/water.png'}
        ],
        'instructions': ['Squeeze lemons', 'Mix with sugar and water'],
        'prep_time': 10,
        'cook_time': 0,
        'serving_size': 4,
        'tags': ['Drink', 'Summer']
    },
    2: {
        'id': 2,
        'title': 'Cheese Pizza',
        'image': '/static/images/recipes/pizza.png',
        'ingredients': [
            {'name': 'Dough', 'image': '/static/images/ingredients/dough.png'},
            {'name': 'Cheese', 'image': '/static/images/ingredients/cheese.png'},
            {'name': 'Tomato Sauce', 'image': '/static/images/ingredients/tomato-sauce.png'}
        ],
        'instructions': ['Prepare dough', 'Add sauce', 'Add cheese', 'Bake'],
        'prep_time': 15,
        'cook_time': 15,
        'serving_size': 4,
        'tags': ['Dairy', 'Italian']
    },
    3: {
        'id': 3,
        'title': 'Vodka Pasta',
        'image': '/static/images/recipes/pasta.png',
        'ingredients': [
            {'name': 'Pasta', 'image': '/static/images/ingredients/pasta.png'},
            {'name': 'Vodka', 'image': '/static/images/ingredients/vodka.png'},
            {'name': 'Tomato Sauce', 'image': '/static/images/ingredients/tomato-sauce.png'},
            {'name': 'Heavy Cream', 'image': '/static/images/ingredients/cream.png'}
        ],
        'instructions': ['Cook pasta', 'Make sauce with vodka', 'Mix pasta and sauce', 'Serve hot'],
        'prep_time': 10,
        'cook_time': 25,
        'serving_size': 4,
        'tags': ['Italian', 'Dinner']
    },
    4: {
        'id': 4,
        'title': 'Chocolate Chip Cookies',
        'image': '/static/images/recipes/cookies.png',
        'ingredients': [
            {'name': 'Flour', 'image': '/static/images/ingredients/flour.png'},
            {'name': 'Sugar', 'image': '/static/images/ingredients/sugar.png'},
            {'name': 'Chocolate Chips', 'image': '/static/images/ingredients/chocolate-chips.png'},
            {'name': 'Butter', 'image': '/static/images/ingredients/butter.png'}
        ],
        'instructions': ['Mix ingredients', 'Form dough balls', 'Bake at 350°F', 'Cool before serving'],
        'prep_time': 15,
        'cook_time': 15,
        'serving_size': 12,
        'tags': ['Dessert', 'Dairy']
    },
    5: {
        'id': 5,
        'title': 'BAD RECIPE',
        'image': '/static/images/recipes/bad-recipe.png',
        'ingredients': [
            {'name': 'Bad Ingredient 1', 'image': '/static/images/ingredients/bad1.png'},
            {'name': 'Bad Ingredient 2', 'image': '/static/images/ingredients/bad2.png'}
        ],
        'instructions': ['Do bad thing 1', 'Do bad thing 2'],
        'prep_time': 15,
        'cook_time': 15,
        'serving_size': 1,
        'tags': ['Bad']
    }
}


@app.route('/editingpage/<int:recipe_id>')
def edit_recipe(recipe_id):
    recipe_data = recipes_data.get(recipe_id)
    
    if recipe_data is None:
        return redirect(url_for('create_recipe'))
        
    return render_template('editingpage.html', recipe=recipe_data)

@app.route('/createaccount') #when you click "dont have an account? create one!" in login page
def createaccount():
    return render_template('createaccount.html')


if __name__ == '__main__':
    app.run(debug=True)
