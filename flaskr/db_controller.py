from flask import current_app, g
from . import db

def execute_sql(sql, values):
  conn = db.get_db()
  cur = conn.cursor()
  cur.execute(sql, values)

  return cur

def get_model(model_id):
  sql = "SELECT * FROM model WHERE id = ?"
  cur = execute_sql(sql, (model_id))
  data = cur.fetchall()

  return data[0] if len(data) != 0 else None

def update_model(data):
  print('Update model', data)

def create_model(model_id):
  sql = "INSERT INTO model (id, time_elapsed) VALUES (?,?)"
  cur = execute_sql(sql, (model_id, 0))

  return cur.lastrowid

def get_timestamp_model_join(model_id, timestamp):
  sql = "SELECT * FROM timestamp_model_join WHERE model_id = ? and timestamp = ?"
  cur = execute_sql(sql, (model_id, timestamp))
  data = cur.fetchall()

  return data[0] if len(data) != 0 else None

def init_timestamp_model_join(model_id):
  sql = ''' INSERT INTO timestamp_model_join (model_id, timestamp, temperature) 
            VALUES (?,?,?) '''
  cur = execute_sql(sql, (model_id, 0, 25))

  return cur.lastrowid

def get_cell_model_join_id(cell_number, model_id):
  cell_model_join = get_cell_model_join(cell_number, model_id)

  return cell_model_join[0][0] if len(cell_model_join) != 0 else None

def get_cell_model_join(cell_number, model_id):
  sql = "SELECT * FROM cell_model_join WHERE model_id = ? AND cell_number = ?"
  cur = execute_sql(sql, (model_id, cell_number))
  cell_model_join = cur.fetchall()

  return cell_model_join if len(cell_model_join) != 0 else None

def create_cell(cell_number, model_id):
  sql = "INSERT INTO cell_model_join (cell_number, model_id) VALUES (?,?)"
  cur = execute_sql(sql, (cell_number, model_id))
  
  return cur.lastrowid