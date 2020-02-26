DROP TABLE IF EXISTS model;
DROP TABLE IF EXISTS timestamp_model_join;
DROP TABLE IF EXISTS cell_model_join;
DROP TABLE IF EXISTS timestamp_cell_join;

CREATE TABLE model (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  time_elapsed INTEGER NOT NULL
);

CREATE TABLE timestamp_model_join (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_id INTEGER NOT NULL,
  time_stamp INTEGER,
  temperature REAL NOT NULL,
  FOREIGN KEY (model_id) REFERENCES model (id)
);

CREATE TABLE cell_model_join (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_number INTEGER,
  model_id INTEGER NOT NULL,
  FOREIGN KEY (model_id) REFERENCES model (id)
);

CREATE TABLE timestamp_cell_join (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cell_id INTEGER NOT NULL,
  time_stamp INTEGER NOT NULL,
  carnivore_abundance REAL NOT NULL,
  carnivore_biomass REAL NOT NULL,
  herbivore_abundance REAL NOT NULL,
  herbivore_biomass REAL NOT NULL,
  primary_producer_biomass REAL NOT NULL,
  FOREIGN KEY (cell_id) REFERENCES cell (id)
);