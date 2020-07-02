from celery import Celery
from celery.schedules import crontab
from celery.task import periodic_task
from celery.utils.log import get_task_logger

from excel_parser.utils import get_daily_data


logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(minute='*/15')),
    name="task_get_daily_data",
    ignore_result=True
)
def task_get_daily_data():
    """
    Gets latest data from the API
    """
    get_daily_data()
    logger.info("Got todays data!")
