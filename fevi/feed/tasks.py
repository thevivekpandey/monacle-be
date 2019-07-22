from __future__ import absolute_import, unicode_literals
from celery import task
from celery.utils.log import get_task_logger

logger = get_task_logger('fevi')

@task()
def task_number_two():
    print(logger)
    print('twotwotwtowtwotwotwotwotowtwotowtowotwotwotwtowtowtowotwotowoot')
    logger.info('logglgoglgoglgoglgoglgoglgoglgoglgolgoglgolgoglgolgogllgo')
    logger.debug('debuggging everything')
    return 'I am number two'
