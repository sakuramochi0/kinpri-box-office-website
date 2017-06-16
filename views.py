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

    if endpoint == 'v1/box-office.json':
        # make header
        data = [[
            {'id': '_id', 'label': '日付', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            # {'calc': 'stringify', 'sourceColumn': 1,
            #  'type': "string", 'role': "annotation"},
            # {'id': 'show_num', 'label': '上映回数', 'type': 'number'},
            # {'id': 'theater_num', 'label': '劇場数', 'type': 'number'},
        ]]
        
        # add rows
        for i in db.mimorin_daily.find().sort('_id'):
            row = [
                i['_id'].strftime('%m/%d({})'.format(get_weekday(i['_id']))),
                i['sell'],
            ]
            data.append(row)

    else:
        data = []
    return JsonResponse(data, safe=False)

