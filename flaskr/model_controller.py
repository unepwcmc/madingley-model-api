import json
from . import simple_madingley_model
from . import db_controller

def init_model(model_id):
  db_controller.create_model(model_id)
  db_controller.init_timestamp_model_join(model_id)
  db_controller.init_model_cells(model_id, simple_madingley_model.N_CELLS)

  model_state = simple_madingley_model.ReturnInitialGrid()
  db_controller.update_timestamp_cell_joins(0, model_id, model_state)
  
def update_model(model_id, data):
  new_model_state = get_new_model_state(model_id, data)

  new_temp = new_model_state['temperature']
  new_timestamp = new_model_state['timestamp']
  update_model_state_in_db(model_id, new_model_state)
  
  return get_response(new_model_state)

def get_new_model_state(model_id, data):
  current_model_state_params = get_current_model_state(model_id)

  new_model_state = simple_madingley_model.UpdateModelState(
    current_model_state_params,
    data
  )

  new_model_state['timestamp'] = current_model_state_params['timestamp'] + data['timestep']

  return new_model_state

def update_model_state_in_db(model_id, state):
  timestamp = state['timestamp']

  db_controller.update_model_time_elapsed(model_id, timestamp)
  db_controller.update_timestamp_model_join(timestamp, model_id, state['temperature'])
  db_controller.update_timestamp_cell_joins(timestamp, model_id, state)

def get_response(state):
  return json.dumps({
    'herbivore_biomasses': simple_madingley_model.GetSumOverBodymasses(state['herbivore_biomasses']),
    'herbivore_abundances': simple_madingley_model.GetSumOverBodymasses(state['herbivore_abundances']),
    'carnivore_biomasses': simple_madingley_model.GetSumOverBodymasses(state['carnivore_biomasses']),
    'carnivore_abundances': simple_madingley_model.GetSumOverBodymasses(state['carnivore_abundances']),
    'harvested_biomass': state['harvested_biomass'] if 'harvested_biomass' in state else [],
    'mean_harvested_bodymass': state['mean_harvested_bodymass'] if 'mean_harvested_bodymass' in state else [],
    'temperature': state['temperature'],
    'timestamp': state['timestamp']
  })

def get_current_model_state(model_id):
  current_timestamp = db_controller.get_model_time_elapsed(model_id)
  current_model_state_db = db_controller.get_model_at_t(current_timestamp, model_id)
  current_cell_states_db = db_controller.get_cells_at_t(model_id, current_timestamp)
  
  model_state_params = get_model_state_from_model_state_db(current_model_state_db, current_cell_states_db)
  model_state_params['timestamp'] = current_timestamp

  return model_state_params

def get_model_state_from_model_state_db(current_model_state_db, current_cell_states_db):
  current_state_for_model = {k: [] for k in simple_madingley_model.CELL_STATE_PROPERTIES}
  current_state_for_model['temperature'] = current_model_state_db['temperature']

  for cell_state in current_cell_states_db:
    for property in simple_madingley_model.CELL_STATE_PROPERTIES:
      cell_property_value = cell_state[property]

      current_state_for_model[property].append(
        cell_property_value if isinstance(cell_property_value, float) else json.loads(cell_property_value)
      )

  return current_state_for_model