from flask.cli import FlaskGroup
from interpreter.core.core import app, db
from flask_migrate import Migrate

migrate = Migrate(app, db)

cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()