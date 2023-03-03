from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash


class Product:
    db = "project"
    def __init__(self, data):
        self.id = data['id']
        self.category = data['category']
        self.dessert = data['dessert']
        self.price = data['price']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.image = data['image']
        self.posted_by = None

    @classmethod
    def save(cls, data):
        query = "INSERT INTO products (category, dessert, price, created_at, updated_at, image) VALUES (%(category)s, %(dessert)s, %(price)s, NOW(), NOW(), %(image)s);"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_all_by_category(cls):
        query = "SELECT * FROM products WHERE category IN ('cakes', 'cupcakes', 'cookies');"
        results = connectToMySQL(cls.db).query_db(query)
        products = []
        for r in results:
            product = cls(r)
            products.append(product)
        return products

    @classmethod
    def get_one_product(cls, id):
        query = "SELECT * FROM products WHERE id = %(id)s;"
        data = {'id': id}
        result = connectToMySQL(cls.db).query_db(query, data)
        return cls(result[0]) if result else None



    @classmethod
    def update(cls, data):
        query = "UPDATE products SET dessert = %(dessert)s, price = %(price)s, category = %(category)s WHERE id = %(id)s;"
        connectToMySQL(cls.db).query_db(query, data)
        if data['image']:
            query = "UPDATE products SET image = %(image)s WHERE id = %(id)s;"
            connectToMySQL(cls.db).query_db(query, data)

