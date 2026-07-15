from celery import Celery

from celery.schedules import crontab

from app import app


def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config["CELERY_BROKER_URL"],
        backend=flask_app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(
        timezone="Asia/Kolkata",
        enable_utc=False,
        beat_schedule={
            "daily-trek-reminders": {
                "task": "tasks.daily_trek_reminders",
                "schedule": crontab(hour=8, minute=0),
            },
            "monthly-activity-report": {
                "task": "tasks.monthly_activity_report",
                "schedule": crontab(day_of_month=1, hour=9, minute=0),
            },
        },
    )


    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)

import tasks
