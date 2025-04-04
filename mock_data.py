from models import Product, Recipe, MyRecipes

# Dummy data
products = [
    Product(1, "Pear", "A sweet, juicy fruit that grows on trees", 1.99, "pear.png"),
    Product(2, "Apple", "A round fruit that grows on apple trees", 1.99, "apple.jpg"),
    Product(3, "Chicken", "A lean, white poultry meat", 7.99, "chicken.jpg"),
    Product(4, "Watermelon", "A large, juicy fruit with red flesh", 5.99, "watermelon.jpg"),
]

lemonade = Recipe('Lemonade', 
                  [{'name': 'Lemons', 'image': '/static/images/ingredients/lemon.png'},
                   {'name': 'Sugar', 'image': '/static/images/ingredients/sugar.png'},
                   {'name': 'Water', 'image': '/static/images/ingredients/water.png'}],
                  ['Squeeze lemons', 'Mix with sugar and water'])
lemonade.id = 1
lemonade.image = '/static/images/recipes/lemonade.png'
lemonade.prep_time = 10
lemonade.cook_time = 0
lemonade.serving_size = 4
lemonade.tags = ['Drink', 'Summer']

pizza = Recipe('Cheese Pizza',
               [{'name': 'Dough', 'image': '/static/images/ingredients/dough.png'},
                {'name': 'Cheese', 'image': '/static/images/ingredients/cheese.png'},
                {'name': 'Tomato Sauce', 'image': '/static/images/ingredients/tomato-sauce.png'}],
               ['Prepare dough', 'Add sauce', 'Add cheese', 'Bake'])
pizza.id = 2
pizza.image = '/static/images/recipes/pizza.png'
pizza.prep_time = 15
pizza.cook_time = 15
pizza.serving_size = 4
pizza.tags = ['Dairy', 'Italian']

pasta = Recipe('Vodka Pasta',
               [{'name': 'Pasta', 'image': '/static/images/ingredients/pasta.png'},
                {'name': 'Vodka', 'image': '/static/images/ingredients/vodka.png'},
                {'name': 'Tomato Sauce', 'image': '/static/images/ingredients/tomato-sauce.png'},
                {'name': 'Heavy Cream', 'image': '/static/images/ingredients/cream.png'}],
               ['Cook pasta', 'Make sauce with vodka', 'Mix pasta and sauce', 'Serve hot'])
pasta.id = 3
pasta.image = '/static/images/recipes/pasta.png'
pasta.prep_time = 10
pasta.cook_time = 25
pasta.serving_size = 4
pasta.tags = ['Italian', 'Dinner']

cookies = Recipe('Chocolate Chip Cookies',
                 [{'name': 'Flour', 'image': '/static/images/ingredients/flour.png'},
                  {'name': 'Sugar', 'image': '/static/images/ingredients/sugar.png'},
                  {'name': 'Chocolate Chips', 'image': '/static/images/ingredients/chocolate-chips.png'},
                  {'name': 'Butter', 'image': '/static/images/ingredients/butter.png'}],
                 ['Mix ingredients', 'Form dough balls', 'Bake at 350°F', 'Cool before serving'])
cookies.id = 4
cookies.image = '/static/images/recipes/cookies.png'
cookies.prep_time = 15
cookies.cook_time = 15
cookies.serving_size = 12
cookies.tags = ['Dessert', 'Dairy']

bad_recipe = Recipe('BAD RECIPE',
                    [{'name': 'Bad Ingredient 1', 'image': '/static/images/ingredients/bad1.png'},
                     {'name': 'Bad Ingredient 2', 'image': '/static/images/ingredients/bad2.png'}],
                    ['Do bad thing 1', 'Do bad thing 2'])
bad_recipe.id = 5
bad_recipe.image = '/static/images/recipes/bad-recipe.png'
bad_recipe.prep_time = 15
bad_recipe.cook_time = 15
bad_recipe.serving_size = 1
bad_recipe.tags = ['Bad']

my_recipes = MyRecipes()
my_recipes.addRecipe(lemonade)
my_recipes.addRecipe(pizza)
my_recipes.addRecipe(pasta)
my_recipes.addRecipe(cookies)
my_recipes.addRecipe(bad_recipe)

recipes_data = {
    1: lemonade,
    2: pizza,
    3: pasta,
    4: cookies,
    5: bad_recipe
} 