from app import create_app
from app.tasks.celery_tasks import ReadLog,Scheduler
app = create_app('default')

if __name__ == '__main__':
    app.jinja_env.cache = {}
    log = ReadLog()
    scheduler = Scheduler(1, log.read_content)
    scheduler.start()
    app.run(debug=False)
    scheduler.stop()
