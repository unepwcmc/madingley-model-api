from flask import current_app, g
from . import db
import pdb

def execute_sql(sql, values):
  conn = db.get_db()
  cur = conn.cursor()
  cur.execute(sql, values)

  return cur

def get_model_time_elapsed(model_id):
  return get_model(model_id)[1]

def get_model(model_id):
  sql = "SELECT * FROM model WHERE id = ?"
  cur = execute_sql(sql, (model_id))
  data = cur.fetchall()

  return data[0] if len(data) != 0 else None

def create_model(model_id):
  sql = "INSERT INTO model (id, time_elapsed) VALUES (?,?)"
  cur = execute_sql(sql, (model_id, 0))

  return cur.lastrowid

def get_timestamp_model_join(timestamp, model_id):
  sql = "SELECT * FROM timestamp_model_join WHERE model_id = ? and timestamp = ?"
  cur = execute_sql(sql, (model_id, timestamp))
  data = cur.fetchall()

  return data[0] if len(data) != 0 else None

def get_model_at_t(timestamp, model_id):
  return dict(get_timestamp_model_join(timestamp, model_id))

def init_timestamp_model_join(model_id):
  sql = ''' INSERT INTO timestamp_model_join (model_id, timestamp, temperature) 
            VALUES (?,?,?) '''
  cur = execute_sql(sql, (model_id, 0, 25))

  return cur.lastrowid

def get_cell_model_join_id(cell_number, model_id):
  cell_model_join = get_cell_model_join(cell_number, model_id)

  return cell_model_join[0] if len(cell_model_join) != 0 else None

def get_cell_model_join(cell_number, model_id):
  sql = "SELECT * FROM cell_model_join WHERE model_id = ? AND cell_number = ?"
  cur = execute_sql(sql, (model_id, cell_number))
  cell_model_join = cur.fetchall()

  return cell_model_join[0] if len(cell_model_join) != 0 else None

def create_cell(cell_number, model_id):
  sql = "INSERT INTO cell_model_join (cell_number, model_id) VALUES (?,?)"
  cur = execute_sql(sql, (cell_number, model_id))
  
  return cur.lastrowid

def get_cells_at_t(model_id, timestamp):
  sql = "SELECT id FROM cell_model_join WHERE model_id = ? ORDER BY cell_number"
  cur = execute_sql(sql, (model_id))
  cell_ids = map((lambda x: x[0]), cur.fetchall())
  
  cell_states = []

  for cell_id in cell_ids:
    cell_states.append(get_cell_at_t(cell_id, timestamp))
  
  return cell_states

def get_cell_at_t(cell_id, timestamp):
  return dict(get_timestamp_cell_join(timestamp, cell_id)) if cell_id else None

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
