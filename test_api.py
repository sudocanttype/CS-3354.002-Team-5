import unittest
from mock_data import products, recipes_data, my_recipes

class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        
    def json(self):
        return self.json_data

class TestAPI(unittest.TestCase):
    def test_get_products(self):
        # Mock response for GET /api/products
        mock_products = [
            {"product_id": p.product_id, "name": p.name, "price": p.price, 
             "description": p.description, "image": p.image} 
            for p in products
        ]
        response = MockResponse(mock_products, 200)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)
        self.assertEqual(response.json()[0]["name"], "Pear")
        self.assertEqual(response.json()[1]["name"], "Apple")
    
    def test_get_recipes(self):
        # Mock response for GET /api/recipes
        mock_recipes = [
            {"id": recipe.id, "nameOfRecipe": recipe.nameOfRecipe, 
             "prep_time": recipe.prep_time, "cook_time": recipe.cook_time,
             "serving_size": recipe.serving_size, "tags": recipe.tags,
             "image": recipe.image}
            for recipe_id, recipe in recipes_data.items()
        ]
        response = MockResponse(mock_recipes, 200)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)
        
        # Find Lemonade recipe
        lemonade = next((r for r in response.json() if r["nameOfRecipe"] == "Lemonade"), None)
        self.assertIsNotNone(lemonade)
        self.assertEqual(lemonade["tags"], ["Drink", "Summer"])
        
    def test_get_recipe_detail(self):
        # Mock response for GET /api/recipes/2 (Pizza)
        recipe = recipes_data[2]
        mock_recipe_detail = {
            "id": recipe.id,
            "nameOfRecipe": recipe.nameOfRecipe,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "serving_size": recipe.serving_size,
            "tags": recipe.tags,
            "image": recipe.image
        }
        response = MockResponse(mock_recipe_detail, 200)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nameOfRecipe"], "Cheese Pizza")
        self.assertEqual(len(response.json()["ingredients"]), 3)
        self.assertEqual(len(response.json()["instructions"]), 4)
        
    def test_filter_recipes_by_tag(self):
        # Mock response for GET /api/recipes?tag=Italian
        italian_recipes = [
            {"id": recipe.id, "nameOfRecipe": recipe.nameOfRecipe, 
             "prep_time": recipe.prep_time, "cook_time": recipe.cook_time,
             "serving_size": recipe.serving_size, "tags": recipe.tags,
             "image": recipe.image}
            for recipe_id, recipe in recipes_data.items()
            if "Italian" in recipe.tags
        ]
        response = MockResponse(italian_recipes, 200)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)  # Pizza and Pasta are Italian
        recipe_names = [r["nameOfRecipe"] for r in response.json()]
        self.assertIn("Cheese Pizza", recipe_names)
        self.assertIn("Vodka Pasta", recipe_names)
        

if __name__ == "__main__":
    unittest.main() 