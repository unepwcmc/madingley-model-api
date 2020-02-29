import os
import sqlite3
from flask import Flask
from flask import request
import json
from . import simple_madingley_model
from . import db_controller
from . import model_controller
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
        return model_controller.get_current_state_response(model_id)

      if request.method == 'POST':
        data = json.loads(request.data)
        response = None

        with db.get_db():
          if not db_controller.get_model(model_id):
            model_controller.init_model(model_id)
            response = model_controller.get_current_state_response(model_id)
          else:
            response = model_controller.update_model(model_id, data)

        return response

    db.init_app(app)

  return app