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
      db_controller.init_model_cells(model_id, 9)

      grid_state = simple_madingley_model.ReturnInitialGrid()
      db_controller.update_timestamp_cell_joins(0, model_id, grid_state)
      
    def update_model(model_id, data):
      current_timestamp = db_controller.get_model_time_elapsed(model_id)
      current_model_state = db_controller.get_model_at_t(current_timestamp, model_id)
      current_cell_states = db_controller.get_cells_at_t(model_id, current_timestamp)
      
      simple_madingley_model.ResetCellStateGlobals()
      current_state_for_model = simple_madingley_model.GetCellStates()
      current_state_for_model['temperature'] = current_model_state['temperature']

      for cell_state in current_cell_states:
        for property in simple_madingley_model.CELL_STATE_PROPERTIES:
          cell_property_value = cell_state[property]

          current_state_for_model[property].append(
            cell_property_value if isinstance(cell_property_value, float) else json.loads(cell_property_value)
          )

      new_state = simple_madingley_model.UpdateModelState(
        current_state_for_model,
        data['timestep'],
        data['warming']
      )

      new_temp = new_state['temperature']
      new_timestamp = current_timestamp + data['timestep']
      db_controller.update_model_time_elapsed(model_id, new_timestamp)
      db_controller.update_timestamp_model_join(new_timestamp, model_id, new_temp)
      db_controller.update_timestamp_cell_joins(new_timestamp, model_id, new_state)

      #TODO: add harvest data
      new_state_for_frontend = {
        'herbivore_biomasses': simple_madingley_model.GetSumOverBodymasses(new_state['herbivore_biomasses']),
        'herbivore_abundances': simple_madingley_model.GetSumOverBodymasses(new_state['herbivore_abundances']),
        'carnivore_biomasses': simple_madingley_model.GetSumOverBodymasses(new_state['carnivore_biomasses']),
        'carnivore_abundances': simple_madingley_model.GetSumOverBodymasses(new_state['carnivore_abundances']),
        'temperature': new_temp,
        'timestamp': new_timestamp
      }

      return json.dumps({
        'db': new_state,
        'frontend': new_state_for_frontend
      })

    db.init_app(app)

  return app