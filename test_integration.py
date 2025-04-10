import unittest
from models import User, Product, Recipe, GroceryList
from mock_data import products, recipes_data, my_recipes

class TestUserWorkflow(unittest.TestCase):
    def setUp(self):
        self.user = User("Test", "User", "testuser", "password")
        self.lemonade = recipes_data[1]
        self.pizza = recipes_data[2]
        self.pear = products[0]
        self.apple = products[1]
    
    def test_add_recipes_to_favorites(self):
        # Test adding multiple recipes to favorites
        self.user.addToFavorites(self.lemonade)
        self.user.addToFavorites(self.pizza)
        
        favorites = self.user.getFavorites()
        self.assertEqual(len(favorites), 2)
        
        favorite_names = [recipe.nameOfRecipe for recipe in favorites]
        self.assertIn("Lemonade", favorite_names)
        self.assertIn("Cheese Pizza", favorite_names)
    
    def test_add_products_to_grocery_list(self):
        self.user.groceryList.cart.append(self.pear)
        self.user.groceryList.cart.append(self.apple)
        
        grocery_items = [product.name for product in self.user.groceryList.cart]
        self.assertEqual(len(grocery_items), 2)
        self.assertIn("Pear", grocery_items)
        self.assertIn("Apple", grocery_items)
    
    def test_end_to_end_shopping_flow(self):
        # add products to grocery list
        self.user.groceryList.cart.append(self.pear)
        self.user.groceryList.cart.append(self.apple)
        
        # add recipes to favorites
        self.user.addToFavorites(self.lemonade)
        
        # check grocery list and favorites
        grocery_items = [product.name for product in self.user.groceryList.cart]
        favorites = self.user.getFavorites()
        
        self.assertEqual(len(grocery_items), 2)
        self.assertEqual(len(favorites), 1)
        
        # complete checkout (would clear cart)
        self.user.groceryList.checkout()
        
        # check cart is empty after checkout
        self.assertEqual(len(self.user.groceryList.cart), 0)
        
        # check favorites are still there
        self.assertEqual(len(self.user.getFavorites()), 1)

class TestRecipeManagement(unittest.TestCase):
    def setUp(self):
        self.user = User("Recipe", "Tester", "recipeuser", "password")
        self.pizza = recipes_data[2]
        
        self.user.myRecipes.addRecipe(self.pizza)
    
    def test_recipe_search_by_tag(self):
        for _, recipe in recipes_data.items():
            self.user.myRecipes.addRecipe(recipe)
        
        # Get all recipes
        all_recipes = self.user.getRecipes()
        
        # Filter recipes with "Italian" tag
        italian_recipes = [r for r in all_recipes if "Italian" in getattr(r, "tags", [])]
        
        italian_recipe_names = set(r.nameOfRecipe for r in italian_recipes)
        self.assertEqual(len(italian_recipe_names), 2)
        self.assertIn("Cheese Pizza", italian_recipe_names)
        self.assertIn("Vodka Pasta", italian_recipe_names)
        
        dessert_recipes = [r for r in all_recipes if "Dessert" in getattr(r, "tags", [])]
        
        dessert_recipe_names = set(r.nameOfRecipe for r in dessert_recipes)
        self.assertEqual(len(dessert_recipe_names), 1)
        self.assertIn("Chocolate Chip Cookies", dessert_recipe_names)


if __name__ == "__main__":
    unittest.main() 
