import json
from flask import current_app, g
from . import db
from . simple_madingley_model import CELL_STATE_PROPERTIES

def get_model_at_t(timestamp, model_id):
  return dict(get_timestamp_model_join(timestamp, model_id))

def get_cells_at_t(model_id, timestamp):
  cell_ids = get_cell_ids_for_model(model_id)

  cell_states = []

  for cell_id in cell_ids:
    cell_states.append(get_cell_at_t(cell_id, timestamp))

  return cell_states

def get_cell_at_t(cell_id, timestamp):
  return dict(get_timestamp_cell_join(timestamp, cell_id)) if cell_id else None

def get_model(model_id):
  sql = "SELECT * FROM model WHERE id = ?"
  cur = execute_sql(sql, (model_id))
  data = cur.fetchall()

  return data[0] if len(data) != 0 else None

def get_model_time_elapsed(model_id):
  return get_model(model_id)[1]

def create_model(model_id):
  sql = "INSERT INTO model (id, time_elapsed) VALUES (?,?)"
  cur = execute_sql(sql, (model_id, 0))

  return cur.lastrowid

def get_timestamp_model_join(timestamp, model_id):
  sql = "SELECT * FROM timestamp_model_join WHERE model_id = ? and timestamp = ?"
  cur = execute_sql(sql, (model_id, timestamp))
  data = cur.fetchall()

  return data[0] if len(data) != 0 else None

def init_timestamp_model_join(model_id):
  update_timestamp_model_join(0, model_id, 25)

def update_timestamp_model_join(timestamp, model_id, temperature):
  sql = ''' INSERT INTO timestamp_model_join (timestamp, model_id, temperature) 
            VALUES (?,?,?) '''
  cur = execute_sql(sql, (timestamp, model_id, temperature))

  return cur.lastrowid

def get_cell_ids_for_model(model_id):
  sql = "SELECT id FROM cell_model_join WHERE model_id = ? ORDER BY cell_number"
  cur = execute_sql(sql, (model_id))

  return list(map((lambda x: x[0]), cur.fetchall()))
  
def get_cell_model_join(cell_number, model_id):
  sql = "SELECT * FROM cell_model_join WHERE model_id = ? AND cell_number = ?"
  cur = execute_sql(sql, (model_id, cell_number))
  cell_model_join = cur.fetchall()

  return cell_model_join[0] if len(cell_model_join) != 0 else None

def get_cell_model_join_id(cell_number, model_id):
  cell_model_join = get_cell_model_join(cell_number, model_id)

  return cell_model_join[0] if len(cell_model_join) != 0 else None

def create_cell(cell_number, model_id):
  sql = "INSERT INTO cell_model_join (cell_number, model_id) VALUES (?,?)"
  cur = execute_sql(sql, (cell_number, model_id))
  
  return cur.lastrowid

def get_timestamp_cell_join(timestamp, cell_id):
  sql = "SELECT * FROM timestamp_cell_join WHERE cell_id = ? AND timestamp = ?"
  cur = execute_sql(sql, (cell_id, timestamp))
  timestamp_cell_join = cur.fetchall()

  return timestamp_cell_join[0] if len(timestamp_cell_join) != 0 else None

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
  return d

def init_model_cells(model_id, length):
  for cell_index in range(length):
    create_cell(cell_index + 1, model_id)

def update_timestamp_cell_joins(timestamp, model_id, state):
  cell_ids = get_cell_ids_for_model(model_id)
  cell_states = {k: state[k] for k in CELL_STATE_PROPERTIES}

  for cell_index in range(len(cell_ids)):
    cell_id = cell_ids[cell_index]
    update_timestamp_cell_join(timestamp, cell_id, cell_index, cell_states)

def update_model_time_elapsed(model_id, time_elapsed):
  sql = '''
    UPDATE model 
    SET time_elapsed = ? 
    WHERE id = ?
  '''
  cur = execute_sql(sql, (time_elapsed, model_id))
  
  return cur.lastrowid

def update_timestamp_cell_join(timestamp, cell_id, cell_index, cell_states):
  cell_state_values_for_db = ()

  for property in cell_states:
    cell_value = cell_states[property][cell_index]
    cell_state_values_for_db += (json.dumps(cell_value),) if isinstance(cell_value, list) else (cell_value,)

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
  execute_sql(sql, (cell_id, timestamp,) + cell_state_values_for_db)

def execute_sql(sql, values):
  conn = db.get_db()
  cur = conn.cursor()
  cur.execute(sql, values)

  return cur
