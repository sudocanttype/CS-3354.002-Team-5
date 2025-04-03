class Product:
    def __init__(self, product_id, name, description, price, image):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.image = image

        def get_product_info(self):
            return f"{self.name} - ${self.price}"