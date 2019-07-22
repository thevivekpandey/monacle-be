from __future__ import absolute_import, unicode_literals

from django.utils import timezone
from datetime import datetime

from sqlalchemy import engine
from celery import task
from croniter import croniter

from analyst.models import Question
from feed.models import FeedCard
from pymongo import MongoClient
import json
import logging

logger = logging.getLogger('feed_card')


def get_sqlalchemy_engine_conn(uri):
    e = engine.create_engine(uri)
    return e.connect()


def execute_query(uri, query):
    if 'mongodb' in uri:
        conn_strings = uri.split('#')
        mongo_uri = conn_strings[0]
        db_props = conn_strings[1].split('&')
        conn_params = {}
        conn_params.setdefault(db_props[0].split('=')[0], db_props[0].split('=')[1])
        conn_params.setdefault(db_props[1].split('=')[0], db_props[1].split('=')[1])
        e = MongoClient(mongo_uri)[conn_params['db']][conn_params['coll']]
        qu_res = e.aggregate(json.loads(query))
        res = []
        row = {}
        for i in qu_res:
            row = i.pop('_id')
            row.update(i)
            res.append(row)
        return res, list(row.keys())
    else:
        e = engine.create_engine(uri)
        res = e.execute(query)
        column_names = res.keys()
        return res, column_names


def execute_question(question: Question):
    uri = question.data_source.uri
    query = question.query
    res, column_names = execute_query(uri, query)
    res_data = []
    for row in res:
        temp_row = {}
        for pos, column_name in enumerate(column_names):
            temp_row[column_name] = row[column_name]
        res_data.append(temp_row)
    return res_data, column_names


def generate_chart_data(question: Question):
    res_data, column_names = execute_question(question)
    return {
        "type": question.chart_type,
        **json.loads(question.chart_config),
        "data": res_data,
        "column_names": column_names
    }


def question_to_feed(question: Question, card_key):
    res = generate_chart_data(question)
    f = FeedCard()
    f.question = question
    f.team = question.team
    f.data = json.dumps(res)
    f.message = question.headline
    f.card_key = card_key
    f.save()
    return f


def get_next_cron_date_time(cron_config, base_datetime):
    cron_obj = croniter(cron_config, base_datetime)
    next_run_time = cron_obj.get_next(datetime)
    return next_run_time


def generate_feed_card():
    qss = Question.objects.filter(
        next_scheduled_run_time__lte=timezone.now(),
        is_running=False
    )
    logger.info('TotalPendingQuestions: %s ', qss.count())
    for q in qss:
        try:
            logger.info('Question: %s ', q.__dict__)
            logger.info('StartingFeedGenerationForQuestionId: %s ', q.id)
            q.last_run_start_time = timezone.now()
            q.is_running = True
            q.save()
            question_to_feed(q, card_key=q.next_scheduled_run_time.isoformat())
            q.next_scheduled_run_time = get_next_cron_date_time(q.cron, q.next_scheduled_run_time)
            q.last_run_end_time = timezone.now()
            q.is_running = False
            q.save()
            logger.info('CompletedFeedGenerationForQuestionId: %s ', q.id)
        except Exception as e:
            logger.exception(e)
    logger.info('CompletedFeedCardGeneration: %s ', qss.count())


@task()
def task_number_one():
    logger.info('Starting task one')
    generate_feed_card()
    logger.info('Task Completed')
