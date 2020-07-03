import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks') # make sure same name in AUth0
def drinks_get():
    alldrinks =  Drink.query.all()
 
    return jsonify({
        'success': True,
        'drinks':[drink.short() for drink in alldrinks] 
    }),200



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_detail_get(payload):

    drinks = list(map(Drink.long, Drink.query.all()))
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drinks(payload):
    data = request.get_json()
    try:
        # data = request.get_json()
        recipe = data['recipe']
        if isinstance(recipe, dict):
            recipe=[recipe]

        title = data['title']
        
        created_drink = Drink(title=title, recipe=json.dumps(recipe))
        created_drink.insert()
    except Exception:
        abort(400)

    return jsonify({'success': True, 
    'drinks': [created_drink.long()
    ]}),200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):

    drink = Drink.query.filter(Drink.id==id).one_or_none()
    data = request.get_json()
    # if the drink is not found then abort 404
    if drink is None:
        abort(404)

    try:
        title = data.get('title')
        recipe = data.get('recipe')
        if title:
            drink.title = title

        if recipe:
            drink.recipe = json.dumps(data['recipe'])

        drink.update()
    except Exception:
        abort(400)
        

    return jsonify({'success': True, 'drinks': [drink.long()]}),200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()
    
    if drink is None:
        abort(404)

    try:
        drink.delete()

    except Exception:
        abort(400)

    return jsonify({'success': True, 'delete': id}),200


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(authorization_error):
    return jsonify({
        "success": False,
        "error": authorization_error.status_code,
        "message": authorization_error.error['description']
    }), authorization_error.status_code 

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False,
                    'error': 400,
                    'message': 'Bad Request'
                    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Not Authorized'
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({'success': False,
                    'error': 405,
                    'message': 'Method Not Allowed'
                    }), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False,
                    'error': 500,
                    'message': 'Internal Server Error'
                    }), 500



