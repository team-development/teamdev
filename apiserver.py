#!/usr/bin/env python3


from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required
from security import authenticate, identity
from user import UserRegister
import sqlite3
import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


def init_db():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    create_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username text, password text)"
    cursor.execute(create_table)
    create_table = "CREATE TABLE IF NOT EXISTS projects (name text PRIMARY KEY, platform text, linux text, username text, password text, project text, github text)"
    cursor.execute(create_table)
    try:
        cursor.execute("INSERT INTO projects VALUES ('ahead', 'vagrant', 'amazon', 'jknott', 'password', 'osdp', 'https://github.com/james-knott/amazon.git')")
    except:
        pass
    connection.commit()
    connection.close()




def server():
    init_db()

    app = Flask(__name__)
    app.secret_key = 'osdp'
    api = Api(app)
    jwt = JWT(app, authenticate, identity)


    class Project(Resource):
        #@jwt_required()
        def get(self, name):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "SELECT * FROM projects WHERE name=?"
            result = cursor.execute(query, (name,))
            row = result.fetchone()
            connection.close()

            if row:
                return {'project': {'name': row[0], 'platform': row[1], 'linux': row[2], 'username': row[3], 'password': row[4], 'project': row[5], 'github': row[6]}}
            return {'message': 'Project not found'}, 404

        @classmethod
        def find_by_name(cls, name):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "SELECT * FROM projects WHERE name=?"
            result = cursor.execute(query, (name,))
            row = result.fetchone()
            connection.close()
            if row:
                return {'project': {'name': row[0], 'platform': row[1], 'linux': row[2], 'username': row[3], 'password': row[4], 'project': row[5], 'github': row[6]}}


        def post(self, name):
            if self.find_by_name(name):
                return {'message': 'The project {} already exists'.format(name)}, 400

            data = request.get_json()
            project = self.find_by_name(name)
            updated_project = {'name': name, 'platform': data['platform'], 'linux': data['linux'], 'username': data['username'], 'password': data['password'], 'project': data['project'], 'github': data['github']}

            if project is None:
                try:
                    self.insert(updated_project)
                except:
                    return {"message": "An error occurred inserting the project."}, 500
            else:
                try:
                    self.update(updated_project)
                except:
                    return {"message": "An error occurred updating the project."}, 500

            return updated_project, 201

        def put(self, name):
            data = request.get_json()
            project = self.find_by_name(name)
            updated_project = {'name': name, 'platform': data['platform'], 'linux': data['linux'], 'username': data['username'], 'password': data['password'], 'project': data['project'], 'github': data['github']}

            if project is None:
                try:
                    self.insert(updated_project)
                except:
                    return {"message": "An error occurred inserting the project."}, 500
            else:
                try:
                    self.update(updated_project)
                except:
                    return {"message": "An error occurred updating the project."}, 500

            return updated_project, 201


        @classmethod
        def insert(cls, project):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "INSERT INTO projects VALUES (?,?,?,?,?,?,?)"
            cursor.execute(query, (project['name'], project['platform'], project['linux'], project['username'], project['password'], project['project'], project['github']))
            connection.commit()
            connection.close()


        def delete(self, name):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "DELETE FROM projects WHERE name=?"
            cursor.execute(query, (name,))
            connection.commit()
            connection.close()

            return {'message': 'Project Deleted'}

        def update(cls, project):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "UPDATE projects SET platform=?, linux=?, username=?, password=?, project=?, github=? WHERE name=?"
            cursor.execute(query, (project['platform'], project['linux'], project['username'], project['password'], project['project'], project['github'], project['name']))
            connection.commit()
            connection.close()





    class ProjectList(Resource):
        def get(self):
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "SELECT * FROM projects"
            result = cursor.execute(query)
            projects = []
            for row in result:
                projects.append({'name': row[0], 'platform': row[1], 'linux': row[2], 'username': row[3], 'password': row[4], 'project': row[5], 'github': row[6]})

            connection.close()

            return {'projects': projects}

    api.add_resource(Project, '/project/<string:name>')
    api.add_resource(ProjectList, '/projects')
    api.add_resource(UserRegister, '/register')


    #app.run(port=5000)
    options = {
        'bind': '%s:%s' % ('127.0.0.1', '8080'),
        'workers': number_of_workers(),
    }
    StandaloneApplication(app, options).run()

server()


