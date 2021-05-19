from celery.utils.log import get_task_logger

from mysite.bhavcopy import Bhavcopy
from mysite.celery import app

logger = get_task_logger(__name__)


@app.task(name='refresh_data')
def refresh_data():
    logger.info('Start Refreshing data!!!')
    Bhavcopy(logger).perform()
    logger.info('Finish Refreshing data!!!')
