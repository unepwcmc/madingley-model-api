import os
import sqlite3
from flask import Flask
from flask import request
import json
from . import simple_madingley_model
from . import db_controller
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
        response = 'initing'
        with db.get_db():
          if not db_controller.get_model(model_id):
            init_model(model_id)
          else:
            response = update_model(model_id, data)

        return response
    
    def init_model(model_id):
      db_controller.create_model(model_id)
      db_controller.init_timestamp_model_join(model_id)

      grid_state = simple_madingley_model.ReturnInitialGrid()
      for cell_index in range(len(grid_state['herbivore_biomasses'])):
        cell_state_values_for_db = ()

        for property in grid_state:
          property_states = grid_state[property]
          cell_value = property_states[cell_index]

          if isinstance(cell_value, list):
            cell_state_values_for_db += (json.dumps(cell_value),)
          else:
            cell_state_values_for_db += (cell_value,)

        cell_id = db_controller.create_cell(cell_index + 1, model_id)

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
        db_controller.execute_sql(sql, (cell_id, 0,) + cell_state_values_for_db)

    def update_model(model_id, data):
      current_timestamp = db_controller.get_model_time_elapsed(model_id)
      current_model_state = db_controller.get_model_at_t(current_timestamp, model_id)
      current_cell_states = db_controller.get_cells_at_t(model_id, current_timestamp)

      return {
        'current_t': current_timestamp,
        'model': current_model_state,
        'cells': current_cell_states
      }

    db.init_app(app)

  return app