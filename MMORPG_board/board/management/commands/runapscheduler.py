import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

import datetime
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from ...models import *
from datetime import datetime, timedelta
from decouple import config

logger = logging.getLogger(__name__)

def send_weekly_new_ads():
    start_date = datetime.today() - timedelta(days=6)
    this_week_ads = Ad.objects.filter(dateCreation__gt=start_date)
    if this_week_ads:
        users = User.objects.all()
        context = {
            'this_week_ads': this_week_ads,
        }

        for user in users:
            context['user'] = user
            html_content = render_to_string('weekly_new_ads_email.html', context)

            msg = EmailMultiAlternatives(
                subject='Новые объявления за прошедшую неделю',
                from_email=config('DEFAULT_FROM_EMAIL'),
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # print(html_content)


# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(scheduler, max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Runs apscheduler."

    # Здесь будет прописываться как часто будет отправляться сообщение (раз в неделю)
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_weekly_new_ads,
            trigger=CronTrigger(week="*/1"),
            id="send_weekly_new_ads",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_new_ads'.")

        delete_old_job_executions(scheduler)

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")