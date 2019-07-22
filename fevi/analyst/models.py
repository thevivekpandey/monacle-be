from django.db import models
from accounts.models import Team
import json


class DBConfigurations:
    MYSQL = 'MySQL'
    MONGODB = 'MONGODB'
    DB_CHOICES = (
        (MYSQL, 'MySQL'),
        (MONGODB, 'MONGODB'),
    )
    TEMPLATES = {MYSQL: {
        'keys': ['host', 'port', 'user', 'password', 'database', 'additional_parameters'],
        'host': {'name': 'Host',
                 'hint': 'Host of your database',
                 'default': '',
                 'type': 'String'},
        'port': {'name': 'PORT',
                 'default': 3306,
                 'hint': 'Please provide port',
                 'type': 'Number'},
        'user': {'name': 'MySQL user',
                 'hint': 'Please provide mysql user',
                 'default': '',
                 'type': 'String'},
        'database': {'name': 'Database Name',
                     'hint': 'Please provide mysql database name',
                     'default': '',
                     'type': 'String'},
        'password': {'name': 'MySQL password',
                     'hint': 'Please provide mysql password',
                     'default': '',
                     'type': 'String'},
        'additional_parameters': {'name': 'Additional JDBC connection string options:',
                                  'hint': 'tinyInt1isBit=false',
                                  'default': '',
                                  'optional': True,
                                  'type': 'String'},
        'uri': {
            'key': 'mysql+pymysql://user:password@host/database?additional_parameters',
            'hidden': True
        }
    },
        MONGODB: {
            'keys': ['host', 'port', 'user', 'password', 'database', 'collection', 'options'],
            'host': {'name': 'Host',
                     'hint': 'Host of your database',
                     'default': '',
                     'type': 'String'},
            'port': {'name': 'PORT',
                     'default': 27017,
                     'hint': 'Please provide port',
                     'type': 'Number'},
            'user': {'name': 'Mongodb user',
                     'hint': 'Please provide mongodb user',
                     'default': '',
                     'type': 'String'},
            'database': {'name': 'Database Name',
                         'hint': 'Please provide mysql database name',
                         'default': '',
                         'type': 'String'},
            'collection': {'name': 'Collection Name',
                           'hint': 'Please provide mysql database name',
                           'default': '',
                           'type': 'String'},
            'password': {'name': 'Mongodb password',
                         'hint': 'Please provide mongodb password',
                         'default': '',
                         'type': 'String'},
            'options': {'name': 'Additional JDBC connection string options:',
                        'hint': 'readPreference=secondary',
                        'default': '',
                        'optional': True,
                        'type': 'String'},
            'uri': {
                'key': (
                    'mongodb://user:password@host:port/database?options'
                    '#db=database&coll=collection'
                ),
                'hidden': True
            }
        }
    }

    @staticmethod
    def get_uri(conn_type, conn_settings):
        db_conf = DBConfigurations.TEMPLATES[conn_type]
        uri_conn = db_conf['uri']['key']
        for key in db_conf['keys']:
            if key in conn_settings:
                val = conn_settings[key]
            else:
                val = ''
            uri_conn = uri_conn.replace(key, str(val))
        return uri_conn


class DataSource(models.Model):
    type = models.CharField(choices=DBConfigurations.DB_CHOICES, max_length=300)
    team = models.ForeignKey(Team,
                             related_name='data_sources',
                             related_query_name='data_source',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    ssh_tunnel = models.TextField(default='{}')
    connection = models.TextField(default='{}')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    @property
    def uri(self):
        """Returns the database uri"""
        conn_settings = json.loads(self.connection)
        return DBConfigurations.get_uri(self.type, conn_settings)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created', 'team']


class Question(models.Model):
    """
    Question metadata
    """
    SELECT = 'SELECT_ONE'
    LINE_CHART = 'LINE_CHART'
    TABLE = 'TABLE'
    NUMBER = 'NUMBER'
    TEXT = 'TEXT'
    CHART_CHOICES = (
        (LINE_CHART, 'Line Chart'),
        (TABLE, 'Table'),
        (NUMBER, 'Number'),
        (TEXT, 'Text'),
        (SELECT, 'Select One')
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='questions')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    headline = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    query = models.TextField()
    publish = models.BooleanField(default=False)
    cron = models.CharField(max_length=100, default='0 9 * * *')
    last_run_start_time = models.DateTimeField(blank=True, null=True)  # celery task initiated
    last_run_end_time = models.DateTimeField(blank=True, null=True)  # celery task completed
    next_scheduled_run_time = models.DateTimeField(blank=True, null=True)  # celery task next pick up time
    is_running = models.BooleanField(default=False)
    chart_type = models.CharField(choices=CHART_CHOICES, default=SELECT, max_length=50)
    chart_config = models.TextField(blank=True, default='{}')
    on_demand = models.BooleanField(default=False)

    def __str__(self):
        return self.headline
