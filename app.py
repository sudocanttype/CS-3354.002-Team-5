from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'nom_nom_bites_secret_key'

# Mock database for demo purposes
recipes = {
    1: {
        'id': 1,
        'title': 'Honey Cake',
        'image': '../static/images/recipes/honey-cake.png',
        'ingredients': [
            {'name': 'Honey 5000L', 'image': '../static/images/ingredients/honey.png'},
            {'name': 'Flour', 'image': '../static/images/ingredients/flour.png'},
            {'name': '4 Eggs', 'image': '../static/images/ingredients/egg.png'}
        ],
        'instructions': [
            'Whisk dry ingredients',
            'Cream butter and honey'
        ],
        'prep_time': 30,
        'cook_time': 45,
        'serving_size': 1,
        'tags': ['Dairy']
    }
}

@app.route('/')
def home():
    return redirect(url_for('recipes_list'))

@app.route('/recipes')
def recipes_list():
    return render_template('recipes_list.html', recipes=recipes)

@app.route('/recipes/create', methods=['GET', 'POST'])
def create_recipe():
    if request.method == 'POST':
        # Process form data
        recipe_id = len(recipes) + 1
        title = request.form.get('title', '')
        prep_time = request.form.get('prep_time', 0)
        cook_time = request.form.get('cook_time', 0)
        serving_size = request.form.get('serving_size', 1)
        
        # In a real app, handle file uploads and store in database
        
        # Add to mock database
        recipes[recipe_id] = {
            'id': recipe_id,
            'title': title,
            'image': '../static/images/shared/placeholder-recipe.png',
            'ingredients': [],
            'instructions': request.form.getlist('instructions[]'),
            'prep_time': prep_time,
            'cook_time': cook_time,
            'serving_size': serving_size,
            'tags': request.form.getlist('tags[]')
        }
        
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('recipes_list'))
    
    # For GET requests, show the form
    return render_template('recipe_form.html', 
                           is_edit_mode=False, 
                           recipe={}, 
                           form_action=url_for('create_recipe'))

@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if recipe_id not in recipes:
        flash('Recipe not found!', 'error')
        return redirect(url_for('recipes_list'))
    
    if request.method == 'POST':
        # Process form data
        recipe = recipes[recipe_id]
        recipe['title'] = request.form.get('title', '')
        recipe['prep_time'] = request.form.get('prep_time', 0)
        recipe['cook_time'] = request.form.get('cook_time', 0)
        recipe['serving_size'] = request.form.get('serving_size', 1)
        recipe['instructions'] = request.form.getlist('instructions[]')
        recipe['tags'] = request.form.getlist('tags[]')
        
        # In a real app, handle file uploads
        
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipes_list'))
    
    # For GET requests, show the form with existing data
    return render_template('recipe_form.html', 
                           is_edit_mode=True, 
                           recipe=recipes[recipe_id], 
                           form_action=url_for('edit_recipe', recipe_id=recipe_id))

if __name__ == '__main__':
    app.run(debug=True)
