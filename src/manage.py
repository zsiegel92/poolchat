import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db

app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
#manager.add_command("runserver", Server(port=8383, host='127.0.0.1'))#Default included
#manager.add_command('debug', Server(use_debugger=True, use_reloader=True, port=8383, host='127.0.0.1'))


if __name__ == '__main__':
	manager.run()
