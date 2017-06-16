import datetime
from dateutil.parser import parse
from get_mongo_client import get_mongo_client

from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse

def get_weekday(day):
    return '月火水木金土日'[day.weekday()]


def index(request):
    return render(request, 'kinpri_box_office/index.html')


def api(request, endpoint):
    db = get_mongo_client().kinpri_box_office

    if endpoint == 'v1/mimorin/daily.json':
        # make header
        data = [[
            {'id': '_id', 'label': '日付', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            {'id': 'show_num', 'label': '上映回数', 'type': 'number'},
            # {'calc': 'stringify', 'sourceColumn': 1,
            #  'type': "string", 'role': "annotation"},
            # {'id': 'theater_num', 'label': '劇場数', 'type': 'number'},
        ]]
        
        # add rows
        for i in db.mimorin_daily.find().sort('_id'):
            row = [
                i['_id'].strftime('%m/%d({})'.format(get_weekday(i['_id']))),
                i['sell'],
                i['show_num'],
            ]
            data.append(row)
    elif endpoint == 'v1/mimorin/weekly.json':
        # make header
        data = [[
            {'id': '_id', 'label': '上映週', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            {'id': 'show_num', 'label': '上映回数', 'type': 'number'},
        ]]

        # add rows
        today = datetime.datetime.today()
        publish_date = parse('6/10')
        weeks = (today - publish_date).days // 7 + 1
        for week in range(weeks):
            start = publish_date + datetime.timedelta(days=week*7)
            end = start + datetime.timedelta(days=6)
            i = db.mimorin_daily.aggregate([{
                '$group': {'_id': '第{}週'.format(week + 1),
                           'sell': {'$sum': '$sell'},
                           'show_num': {'$sum': '$show_num'}},
            }]).next()
            row = [
                i['_id'],
                i['sell'],
                i['show_num'],
            ]
            data.append(row)
        # additional empty data
        data.append(['第{}週'.format(week + 2), 0, None])
    else:
        data = []
    return JsonResponse(data, safe=False)

