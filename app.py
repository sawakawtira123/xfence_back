from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from marshmallow import Schema, fields
import json
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://LOGIN:PASS@IP:PORT/DB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

products_colors = db.Table('products_colors',
                           db.Column('product_id', db.Integer(), db.ForeignKey('products.id')),
                           db.Column('color_id', db.Integer(), db.ForeignKey('colors.id'))
                           )


def custom_response(res, status_code):
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code,
    )


class Colors(db.Model):
    __tablename__ = 'colors'
    id = db.Column(db.Integer(), primary_key=True, unique=True, index=True)
    color = db.Column(db.String(30), nullable=False)
    products = db.relationship('Product', secondary=products_colors, backref='color')

    def __repr__(self):
        return f'{self.id}: {self.color}'

    def __init__(self, color):
        self.color = color


class ColorsSchema(Schema):
    id = fields.Int()
    color = fields.Str()


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer(), primary_key=True, unique=True, index=True)
    article = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Numeric(), nullable=False)
    image = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(800), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    section = db.Column(db.String(120), nullable=False)
    colors = db.relationship('Colors', secondary=products_colors, backref='product')
    is_avialable = db.Column(db.Boolean(), nullable=False, default=True)

    def __repr__(self):
        return f'"id": {self.id},' \
               f'"article": {self.article},' \
               f'"name": {self.name}'

    def __init__(self, article, name, price, image, description, category, section, is_avialable):
        self.article = article
        self.name = name
        self.price = price
        self.image = image
        self.description = description
        self.category = category
        self.section = section
        self.is_avialable = is_avialable


class ProductSchema(Schema):
    id = fields.Int()
    article = fields.Str()
    name = fields.Str()
    price = fields.Float()
    image = fields.Str()
    description = fields.Str()
    category = fields.Str()
    section = fields.Str()
    is_avialable = fields.Bool()
    colors = fields.Nested(ColorsSchema, many=True)


class Contacts(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer(), primary_key=True, unique=True, index=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(40), default='В обработке')

    def __repr__(self):
        return f'{self.id}: {self.name}'

    def __init__(self, name, phone, date):
        self.name = name
        self.phone = phone
        self.date = date


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer(), primary_key=True, unique=True, index=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(40), default='В обработке')
    company = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(100), nullable=True)
    inn = db.Column(db.String(100), nullable=True)
    kpp = db.Column(db.String(100), nullable=True)
    bik = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    addresspost = db.Column(db.String(100), nullable=True)
    post = db.Column(db.String(100), nullable=True)
    pay = db.Column(db.String(100), nullable=True)
    scope = db.Column(db.String(200), nullable=True)
    price = db.Column(db.String(100), nullable=True)
    product = db.Column(JSONB)

    def __repr__(self):
        return f'{self.id}: {self.name}'

    def __init__(self, name, phone, date, status, company, address, inn, kpp, bik, city, country, addresspost, post, pay, scope, price, product):
        self.name = name
        self.phone = phone
        self.date = date
        self.status = status
        self.company = company
        self.address = address
        self.inn = inn
        self.kpp = kpp
        self.bik = bik
        self.city = city
        self.country = country
        self.addresspost = addresspost
        self.post = post
        self.pay = pay
        self.scope = scope
        self.price = price
        self.product = product


@app.route('/api/catalog/<category>/<section>', methods=['GET'])
def get_products(category, section):
    products = db.session.query(Product).filter(Product.category == category, Product.section == section).all()
    schema = ProductSchema()
    result = schema.dump(products, many=True)
    print(result)
    return custom_response(result, 200)


@app.route('/api/catalog/<category>/<section>/<id>', methods=['GET'])
def get_products_byid(category, section, id):
    product = db.session.query(Product).filter(Product.category == category, Product.section == section, Product.id == id).all()
    schema = ProductSchema()
    result = schema.dump(product, many=True)
    print(result)
    return custom_response(result, 200)


@app.route('/api/orders', methods=['POST'])
def add_orders():
    data = request.json
    print(data)
    datenow = datetime.now()
    try:
        order = Orders(data['name'], data['phone'], str(datenow), 'В обработке',
                       data['company'], data['address'], data['inn'], data['kpp'],
                       data['bik'], data['city'], data['country'], data['addresspost'],
                       data['post'], data['pay'], data['scope'], data['price'], data['product'])
        db.session.add(order)
        db.session.commit()
        return Response(
            response='Завяка успешно добавлена',
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return Response(
            response=f'{e}',
            status=500,
            mimetype='application/json'
        )


@app.route('/api/contacts', methods=['POST'])
def add_contact():
    data = request.json
    print(data)
    datenow = datetime.now()
    try:
        contact = Contacts(data['name'], data['phone'], str(datenow))
        db.session.add(contact)
        db.session.commit()
        return Response(
            response='Завяка успешно добавлена',
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return Response(
            response=f'{e}',
            status=500,
            mimetype='application/json'
        )


if __name__ == '__main__':
    app.run()
