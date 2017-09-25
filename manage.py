from flask_script import Manager
from app import create_app, db
from app.models import User, Styles
import datetime
from flask_migrate import MigrateCommand, Migrate, upgrade

app = create_app('default')

with app.app_context():
    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    upgrade = upgrade()


@manager.command
def sys_init(username, email, password):
    # 生成管理员账户
    user = User(username=username,
                email=email,
                password=password,
                confirmed=1,
                confirmed_on=datetime.datetime.now(),
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                last_login=datetime.datetime.now(),
                role=1)
    user.set_password(password)
    db.session.add(user)
    # 生成文章来源
    s1 = Styles(name='原创', name1='原创')
    db.session.add(s1)
    s2 = Styles(name='转载', name1='转载')
    db.session.add(s2)
    db.session.commit()


@manager.command
def init():
    pass


if __name__ == '__main__':
    manager.run()
