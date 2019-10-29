import markdown
import os
import shelve
from flask import Flask, g
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("pricing.db")
    return db


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def index():

    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        content = markdown_file.read()
        return markdown.markdown(content)


class OrderList(Resource):

    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())
        orders = []

        for key in keys:
            orders.append(shelf[key])

        return {'message': 'Success', 'data': orders}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)
        parser.add_argument('customer', required=True)
        parser.add_argument('items', required=True)
        parser.add_argument('quantity', required=True)

        args = parser.parse_args()

        shelf = get_db()
        shelf[args['id']] = args

        return {'message': 'Order registered', 'data': args}, 201


class Order(Resource):
    def get(self, id):
        shelf = get_db()

        if not (id in shelf):
            return {'message': 'Order not found', 'data': {}}, 404

        return {'message': 'Order found', 'data': shelf[id]}, 200

    def delete(self, id):
        shelf = get_db()
        if not (id in shelf):
            return {'message': 'Order not found', 'data': {}}, 404

        del shelf[id]
        return '', 204


api.add_resource(OrderList, '/order')
api.add_resource(Order, '/order/<string:identifier>')
