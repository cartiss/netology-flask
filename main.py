import flask
import jsonschema
from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from validation import POST_ADVER
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Adver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    creator = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Adver: {self.title}'

def validate(req_schema):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                jsonschema.validate(
                    request.get_json(), schema=req_schema
                )
            except jsonschema.ValidationError as er:
                response = Flask.make_response(jsonify({'success': False, 'description': er.message}))
                response.set_status = 401
                return response
            result = func(*args, **kwargs)

            return result
        return wrapper
    return decorator


@app.route('/api/v1', methods=['POST', 'GET'])
def api():
    if request.method == 'POST':
        title = request.args.get('title')
        description = request.args.get('description')
        creator = request.args.get('creator')

        adver = Adver(title=title, description=description, creator=creator)
        db.session.add(adver)
        db.session.commit()

        response = flask.make_response(jsonify({'success': True, 'description': 'Success'}))
        response.set_status = 201

        return response

    advers = Adver.query.all()

    return f'<h1>{advers}</h1>'


@app.route('/api/v1/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_update_or_delete(id):
    try:
        adver = Adver.query.filter_by(id=id).one()
    except:
        response = flask.make_response(jsonify({'success': False, 'description': 'No content'}))
        response.set_status = 404
        return response

    if request.method == 'PUT':
        adver.title = request.args.get('title')
        adver.description = request.args.get('description')
        adver.creator = request.args.get('creator')

        db.session.commit()

        response = flask.make_response(jsonify({'success': True, 'description': 'Success'}))
        response.set_status = 200

        return response
    elif request.method == 'DELETE':
        db.session.delete(adver)
        db.session.commit()

        response = flask.make_response(jsonify({'success': True, 'description': 'Success'}))
        response.set_status = 202

        return response

    return f'<h1>{adver}</h1>'




if __name__ == '__main__':
    app.run(debug=True, port=5000)