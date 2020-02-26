from flask import Flask
from flask import request
import json
import os
import sqlite3
from . import db

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
      SECRET_KEY='dev',
      DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
  )

  if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
  else:
      # load the test config if passed in
      app.config.from_mapping(test_config)

  # ensure the instance folder exists
  try:
      os.makedirs(app.instance_path)
  except OSError:
      pass

  with app.app_context():
    @app.route('/model/<model_id>', methods=['GET', 'POST'])

    def model(model_id):
      if request.method == 'GET':
        return 'Model' + model_id
      if request.method == 'POST':
        data = json.loads(request.data)

        conn = db.get_db()
        with conn:
          if not get_model(conn, model_id):
            create_model(conn, (model_id, 0))
            init_model(conn, model_id)
          else:
            update_model(conn, data)

        array = [1,2,3,4]
        state = {
          'herbivoreBiomasses': array,
          'herbivoreAbundances': array,
          'carnivoreBiomasses': array,
          'carnivoreAbundances': array,
          'temperature': 25,
          'timeElapsed': 1,
        }

        return {
          'biodiversityScores': array,
          'harvestedBiomasses': array,
          'meanHarvestedBiomass': array,
          'model_id': model_id,
          'state': state
        }
    
    def get_model(conn, model_id):
      sql = "SELECT * FROM model WHERE id = ?"
      cur = conn.cursor()
      cur.execute(sql, (model_id))
      data = cur.fetchall()

      if len(data) == 0:
        return None
      else:
        return data[0]

    def init_model(conn, model_id):
      print('Init model', model_id)

    def update_model(conn, data):
      print('Update model', data)

    def create_model(conn, model):
      sql = ''' INSERT INTO model (id, time_elapsed) 
                VALUES (?,?) '''
      cur = conn.cursor()
      cur.execute(sql, model)
      return cur.lastrowid

    db.init_app(app)

  return app