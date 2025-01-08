#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        try:
            json = request.get_json()
            new_user = User(
                username = json['username'],
                image_url = json['image_url'],
                bio = json['bio']
            )
            new_user.password_hash = json['password']
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            response_body = new_user.to_dict(only=('id', 'username', 'image_url', 'bio'))
            return make_response(response_body, 201)
        except:
            response_body = {
                "error": "error"
            }
            return make_response(response_body, 422)

    


       
class CheckSession(Resource):
    
    def get(self):

        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            response_body = user.to_dict(only=('id', 'username', 'image_url', 'bio'))
            return make_response(response_body, 200)
        else:
            response_body = {
                "error": "Please log in!"
            }
        return make_response(response_body, 401)   

class Login(Resource):
    
    def post(self):
           json = request.get_json()
           username = json['username']
           password = json['password']

           user = User.query.filter(User.username == username).first()

           if user and user.authenticate(password):
               session['user_id'] = user.id
               response_body = user.to_dict(only=('id', 'username', 'image_url', 'bio'))
               return make_response(response_body, 200)
           else:
               response_body = {
                   "error": "Invalid username or password"
               }
               return make_response(response_body, 401)

class Logout(Resource):
    
    def delete(self):
        user_id = session['user_id']
        if user_id:
            session['user_id'] = None
            return {}, 204
        else:
            return {"error": "error"}, 401

class RecipeIndex(Resource):
    
    def get(self):
        user_id = session['user_id']
        if user_id:
            recipes = [recipe.to_dict(only=('title', 'instructions', 'minutes_to_complete', 'user_id')) for recipe in Recipe.query.all()]
            return make_response(recipes, 200)
        else:
            response_body = {
                "error": "Unauthorized access. Please log in to view recipes."
            }
            return make_response(response_body, 401)
        
    def post(self):

        user_id = session['user_id']
        try:
            if user_id:
                json = request.get_json()
                new_recipe = Recipe(
                    title = json['title'],
                    instructions = json['instructions'],
                    minutes_to_complete = json['minutes_to_complete'],
                    user_id = user_id
                )
                db.session.add(new_recipe)
                db.session.commit()
                response_body = new_recipe.to_dict(only=('title', 'instructions', 'minutes_to_complete', 'user_id'))
                return make_response(response_body, 201)
            else:
                response_body = {
                    "error", "Not Logged In"
                }
                return make_response(response_body, 401)
        except ValueError as ve:
               response_body = {
                   "error": str(ve)
               }
               return make_response(response_body, 422)



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)