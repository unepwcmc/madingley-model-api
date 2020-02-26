import os
import sqlite3
from flask import Flask
from flask import request
import json
from . import SimpleMadingleyModel
from . import db
import pdb

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

    def get_cell_id(conn, cell_number, model_id):
      sql = "SELECT id FROM cell_model_join WHERE model_id = ? AND cell_number = ?"
      cur = conn.cursor()
      cur.execute(sql, (model_id, cell_number))
      cell = cur.fetchall()

      if len(cell) == 0:
        sql = "INSERT INTO cell_model_join (cell_number, model_id) VALUES (?,?)"
        cur = conn.cursor()
        cur.execute(sql, (cell_number, model_id))
        return cur.lastrowid
      else:
        return cell[0]

    def init_model(conn, model_id):
      init_model_state(conn, model_id)
      grid_state = SimpleMadingleyModel.ReturnInitialGrid()
      for cell_index in range(len(grid_state['herbivore_biomasses'])):
        cell_state_values_for_db = ()

        for property in grid_state:
          property_states = grid_state[property]
          cell_value = property_states[cell_index]

          if isinstance(cell_value, list):
            cell_state_values_for_db += (json.dumps(cell_value),)
          else:
            cell_state_values_for_db += (cell_value,)

        cell_id = get_cell_id(conn, cell_index + 1, model_id)

        sql = '''INSERT INTO timestamp_cell_join (
                cell_id, 
                timestamp,
                herbivore_biomasses,
                herbivore_abundances,
                carnivore_biomasses,
                carnivore_abundances,
                primary_producer_biomass
              ) VALUES (?,?,?,?,?,?,?)
              '''
        cur = conn.cursor()
        cur.execute(sql, (cell_id, 0,) + cell_state_values_for_db)

    def update_model(conn, data):
      print('Update model', data)

    def create_model(conn, model):
      sql = ''' INSERT INTO model (id, time_elapsed) 
                VALUES (?,?) '''
      cur = conn.cursor()
      cur.execute(sql, model)
      return cur.lastrowid

    def init_model_state(conn, model_id):
      sql = ''' INSERT INTO timestamp_model_join (model_id, timestamp, temperature) 
                VALUES (?,?,?) '''
      cur = conn.cursor()
      cur.execute(sql, (model_id, 0, 25))
      return cur.lastrowid

    db.init_app(app)

  return app