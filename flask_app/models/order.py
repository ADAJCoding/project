from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash


class Order:
    db = "project"
    def __init__(self,data):
        self.id = data['id']
        self.total_price = data['total_price']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id= data['user_id']


    @classmethod
    def save_order(cls,data):
        query = "INSERT INTO orders (total_price, created_at,updated_at) VALUES(%(total_price)s, NOW(), NOW());"
        return connectToMySQL(cls.db).query_db(query,data)

    @classmethod
    def get_one_order(cls, id):
        query = "SELECT * FROM orders WHERE id=%(id)s;"
        data = {'id': id}
        result = connectToMySQL(cls.db).query_db(query, data)
        return cls(result[0]) if result else None
    
    @classmethod
    def get_one_wuser(cls, order_id):
        query = "SELECT * FROM orders JOIN users ON orders.user_id = users.id WHERE orders.id = %(order_id)s;"
        data = {'order_id': order_id}
        result = connectToMySQL(cls.db).query_db(query, data)
        if result:
            order = cls(result[0])
            user_data = {
                "id": result[0]['users.id'],
                "first_name": result[0]['first_name'],
                "last_name": result[0]['last_name'],
                "email": result[0]['email'],
                "password": "",
                "created_at": result[0]['users.created_at'],
                "updated_at": result[0]['users.updated_at']
            }
            order.posted_by = user.User(user_data)
            return order
        else:
            return None

    def get_all(cls):
        query = "SELECT * FROM orders JOIN products ON orders.product_id = products.id JOIN users ON orders.user_id = users.id;"
        results = connectToMySQL(cls.db).query_db(query)
        orders = []
        for r in results:
            order = cls(r)
            user_data = {
                "id": r['users.id'],
                "first_name": r['first_name'],
                "last_name": r['last_name'],
                "email": r['email'],
                "password": "",
                "created_at": r['users.created_at'],
                "updated_at": r['users.updated_at']
            }
            order.posted_by = user.User(user_data)
            orders.append(order)
        return orders
    

    
    @classmethod
    def update(cls, data):
        query = "UPDATE orders SET total_price= %(total_price)s WHERE id =%(id)s;"
        return connectToMySQL(cls.db).query_db(query,data)

    @classmethod
    def delete(cls, data):
        query = "DELETE FROM orders WHERE id=%(id)s;"
        connectToMySQL(cls.db).query_db(query, data)