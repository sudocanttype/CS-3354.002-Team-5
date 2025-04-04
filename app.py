from flask import Flask, render_template, request, redirect, url_for
from mock_data import products, recipes_data, my_recipes

app = Flask(__name__)

@app.route('/')
def landingpage():
    return render_template('landingwebpage.html')

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

@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    return redirect(url_for('myrecipes'))

@app.route('/edit_recipe/<int:recipe_id>')
def edit_recipe(recipe_id):
    recipe = recipes_data.get(recipe_id)
    if not recipe:
        return redirect(url_for('myrecipes'))
        
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

@app.route('/update_recipe/<int:recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
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

@app.route('/createaccount') #when you click "dont have an account? create one!" in login page
def createaccount():
    return render_template('createaccount.html')

if __name__ == '__main__':
    app.run(debug=True)
