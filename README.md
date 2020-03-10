# Installation

Install python3

Navigate to the project root and...

Create a virtual environment folder (venv):
`python3 -m venv venv`

To activate the environment:
`. venv/bin/activate`

Install dependencies:
```
pip install Flask
pip install numpy
```

Set app env variables:
```
export FLASK_APP=flaskr
export FLASK_ENV=development
```

Initiate the db:
`flask init-db`

Run the app:
`flask run`
