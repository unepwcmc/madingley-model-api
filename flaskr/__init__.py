from flask import Flask
from flask import request
import json
import os
import sqlite3

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

  @app.route('/model/<model_id>', methods=['GET', 'POST'])

  def model(model_id):
    if request.method == 'GET':
      return 'Model' + model_id
    if request.method == 'POST':
      data = json.loads(request.data)

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
        'state': state
      }
  
  from . import db
  db.init_app(app)

  return app