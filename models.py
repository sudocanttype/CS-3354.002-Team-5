# Product class made by Ahmed Sherwani
class Product: #class for the products the user is able to add to their cart
    def __init__(self, product_id, name, description, price, image):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.image = image

    def get_product_info(self):
        return f"{self.name} - ${self.price}"
    
    def addToCart(self):
        pass


class Recipe:  #class for recipes so that the user can view its details, edit, or create a recipe
    def __init__(self, nameOfRecipe, ingredients, instructions):
        self.nameOfRecipe = nameOfRecipe
        self.ingredients = ingredients
        self.instructions = instructions
    
    def updateRecipe(self):
        pass
    
    def deleteRecipe(self):
        pass


class Favorites:  #collection of the user's fav recipes to display when they filter for favorite recipes in the My Recipes page
    def __init__(self):
        self.favoriteRecipes = []  
    
    def addFavorite(self, recipe):
        self.favoriteRecipes.append(recipe)
    
    def getFavorites(self):
        return self.favoriteRecipes


class MyRecipes:  #collection of the user's recipes including the favorites and recipes the user created/edited
    def __init__(self):
        self.myRecipes = []  
    
    def addRecipe(self, recipe):
        self.myRecipes.append(recipe)
    
    def getMyRecipes(self):
        return self.myRecipes
    
    def deleteRecipe(self, recipe):
        if recipe in self.myRecipes:
            self.myRecipes.remove(recipe)


class User:  #user object to store user info and manage user details for login/log out and their recipes/cart
    def __init__(self, name, lastName, userName, password):
        self.name = name
        self.lastName = lastName
        self.userName = userName
        self.password = password 
        self.favorites = Favorites()
        self.myRecipes = MyRecipes()
        self.groceryList = GroceryList()
    
    def signIn(self):
        pass
    
    def signOut(self):
        pass
    
    def getRecipes(self):
        return self.myRecipes.getMyRecipes()
    
    def addToFavorites(self, recipe):
        self.favorites.addFavorite(recipe)
    
    def getFavorites(self):
        return self.favorites.getFavorites()
    
    def addToGroceryList(self, product):
        self.groceryList.cartList.append(product)
    
    def getGroceryList(self):
        return [product.name for product in self.groceryList.cartList]


class GroceryList:   #unique to a particular user and used to display all products the user added to their cart on the Checkout page
    def __init__(self):
        self.cart = [] 
        self.totalPrice = 0.0
    
    def deleteFromCart(self, product):
        if product in self.cart:
            self.cart.remove(product)
            self.totalPrice -= product.price
    
    def checkout(self):
        self.cart = []
        self.totalPrice = 0.0