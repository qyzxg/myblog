from flask_script import Manager
from app import create_app, db

from flask_migrate import MigrateCommand, Migrate, upgrade

app = create_app()

with app.app_context():
    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    upgrade = upgrade()

if __name__ == '__main__':
    manager.run()