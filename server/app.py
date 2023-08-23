#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Scientists(Resource): 
    def get(self):
        scientists = [scientist.to_dict(rules=('-missions', '-planets')) for scientist in Scientist.query.all()]
        
        return make_response(scientists, 200)

    def post(self): 
        try: 
            data = request.get_json()
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()

            return make_response(new_scientist.to_dict(rules=('-missions',)), 201)

        except: 
            return make_response({"errors" : ["validation errors"]}, 400)
    
 

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).one_or_none()

        if scientist is None:
            return make_response({'error': 'Scientist not found'}, 404)

        return make_response(scientist.to_dict(), 200)
    
    def patch(self, id): 
        scientist = Scientist.query.filter(Scientist.id == id).one_or_none()
        if scientist is None: 
            return make_response({"error": "Scientist not found"}, 404)
        data = request.get_json()
        try: 
            for key in data: 
                setattr(scientist, key, data[key])
                
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(rules=('-mission', '-planets',)), 202)

        except: 
            return make_response({"errors": ["validation errors"]}, 400)
        
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).one_or_none()
        if scientist is None: 
            return make_response({"error": "Scientist not found"}, 404)
        if scientist: 
            db.session.delete(scientist)
            db.session.commit()

            return make_response({}, 204)

class Planets(Resource): 
    def get(self): 
        planets = [planet.to_dict(rules=("-missions", "-scientists",)) for planet in Planet.query.all()]
        return make_response(planets, 200)
    
    def post(self): 
        try: 
            data = request.get_json()
            new_planet = Planet(
                name = data['name'],
                distance_from_earth = data['distance_from_earth'],
                nearest_star = data['nearest_star']
            )
            db.session.add(new_planet)
            db.session.commit()
            return make_response(new_planet.to_dict(rules=('-missions', '-scientists')), 200)
        except ValueError: 
            return make_response({"errors": ["validation errors"]})

class Missions(Resource): 
    def post(self): 
        try: 
            data = request.get_json()
            new_mission = Mission(
                name = data["name"],
                scientist_id = data["scientist_id"],
                planet_id = data['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except ValueError: 
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Missions, "/missions")
api.add_resource(Planets, "/planets")
api.add_resource(Scientists, "/scientists")
api.add_resource(ScientistById, "/scientists/<int:id>")


@app.route('/')
def home():
    return ''

if __name__ == '__main__':
    app.run(port=5555, debug=True)
