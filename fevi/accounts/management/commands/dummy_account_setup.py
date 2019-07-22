import requests
from accounts.models import (
    Account,
    User,
    Team,
    AccountSettings
)
from rest_framework.authtoken.models import Token


def create_data_source(team_id, user_token, local=True):
    if local:
        url = 'http://localhost:8000/analyst/team/team_id/data-sources/'
    else:
        url = 'https://api.fevicult.link/analyst/team/team_id/data-sources/'
    url = url.replace('team_id', str(team_id))
    payload = {
        'connection': {
            'host': '127.0.0.1',
            'port': 3306,
            'database': 'classicmodels',
            'user': 'toiuser',
            'password': 'toipass'
        },
        'ssh_tunnel': {},
        'type': 'MySQL',
        'name': 'dummy_data_source',
        'active': True}
    headers = {
        'Authorization': 'Token ' + str(user_token),
        'Content-Type': 'application/json',
        'cache-control': 'no-cache',
        'Postman-Token': "2476e7c8-89dd-4b3d-930c-f0af3fea6dae"
    }

    response = requests.request('POST', url, json=payload, headers=headers)
    print('Creating data source for demo account')
    print(response.status_code)
    print(response.text)
    return response.json()


def create_question(team_id, user_token, data_source_id, local=True):
    if local:
        url = 'http://localhost:8000/analyst/team/team_id/questions/'
    else:
        url = 'https://api.fevicult.link/analyst/team/team_id/questions/'
    url = url.replace('team_id', str(team_id))
    headers = {
        'Authorization': 'Token ' + str(user_token),
        'Content-Type': 'application/json'
    }
    table_payload = {
        'chart_config': {
            'header': [
                {'name': 'count', 'display': 'Count'},
                {'name': 'STATUS', 'display': 'Status'}
            ]
        },
        'headline': 'Order  status by count',
        'query': 'SELECT count(*) as count, status as STATUS FROM classicmodels.orders group by status;',
        'publish': True,
        'cron': '0 9 * * *',
        'chart_type': 'TABLE',
        'data_source': data_source_id
    }

    chart_payload = {
        'chart_config': {
            'header': [
                {'name': 'count', 'display': 'Count', 'axis': 'Y'},
                {'name': 'STATUS', 'display': 'Status', 'axis': 'X'}
            ]
        },
        'headline': 'Order  status by count',
        'query': 'SELECT count(*) as count, status as STATUS FROM classicmodels.orders group by status;',
        'publish': True,
        'cron': '0 9 * * *',
        'chart_type': 'LINE_CHART',
        'data_source': data_source_id
    }
    print('Creating table question for demo account')
    response = requests.request('POST', url, json=table_payload, headers=headers)
    print(response.status_code)
    print(response.text)
    print('Generating feed card')
    print('Creating line chart question for demo account')
    response2 = requests.request('POST', url, json=chart_payload, headers=headers)
    print(response2.status_code)
    print(response2.text)
    return response.json(), response2.json()


def generate_feed(team_id, user_token, question_id_1, question_id_2, local=True):
    if local:
        url = 'http://localhost:8000/analyst/team/team_id/questions/question_id/generate-feed-card/'
    else:
        url = 'https://api.fevicult.link/analyst/team/team_id/questions/question_id/generate-feed-card/'

    url = url.replace('team_id', str(team_id))
    url1 = url.replace('question_id', str(question_id_1))
    url2 = url.replace('question_id', str(question_id_2))
    headers = {
        'Authorization': 'Token ' + str(user_token),
        'Content-Type': 'application/json'
    }
    print('generating feed cards for line chart and table questions')
    response_1 = requests.request('GET', url1, headers=headers)
    response_2 = requests.request('GET', url2, headers=headers)
    print(response_1.json(), response_2.json())


def generate_demo_data(local=True, workspace='demo'):
    workspace_exists = AccountSettings.objects.filter(workspace=workspace).exists()
    if workspace_exists:
        print('Workspace exists, gracefully kicking you')
        return
    a = Account()
    a.name = workspace
    a.save()
    t = Team()
    t.account = a
    t.save()
    us = []
    first_names = ['Louis', 'Eddie', 'Robin', 'Paula', 'Adrian']
    last_names = ['Skinner', 'Clews', 'Stubson', 'Shanon', 'Engquist']
    for i in range(0, 5):
        u = User()
        u.username = workspace + 'user' + str(i) + '@' + workspace + '.com'
        u.first_name = first_names[i]
        u.last_name = last_names[i]
        u.set_unusable_password()
        u.is_superuser = False
        u.is_active = True
        u.account = a
        if i == 4:
            u.role = 'ANALYST'
        u.save()
        us.append(u)
        t.users.add(u)
    t.save()
    acs = AccountSettings()
    acs.account = a
    acs.all_users_team = t
    acs.admin = us[0]
    acs.workspace = workspace
    acs.gsuite_domain_only = False
    acs.gsuite_domain = workspace
    acs.save()
    analyst_user = us[-1]
    print(analyst_user.role)
    t_c, created = Token.objects.get_or_create(user=analyst_user)
    token = t_c.key
    team_id = t.id
    user_token = token
    data_source = create_data_source(team_id, user_token, local=local)
    data_source_id = data_source['id']
    question_1, question_2 = create_question(team_id, user_token, data_source_id, local=local)
    question_1_id = question_1['id']
    question_2_id = question_2['id']
    generate_feed(team_id, user_token, question_1_id, question_2_id)


