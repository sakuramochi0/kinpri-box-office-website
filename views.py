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

    if endpoint == 'v1/mimorin/daily.json' or \
       endpoint == 'v2/kinpri2/daily.json':
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
            date = i['_id']
            row = [
                date.strftime('%-m/%-d({})'.format(get_weekday(i['_id']))),
                i['sell'],
                i['show_num'],
            ]
            data.append(row)
        # additional empty data
        date = date + datetime.timedelta(days=1)
        date = date.strftime('%-m/%-d({})'.format(get_weekday(date)))
        data.append([date, 0, None])
    elif endpoint == 'v1/mimorin/weekly.json' or \
         endpoint == 'v2/kinpri2/weekly.json':
        # make header
        data = [[
            {'id': '_id', 'label': '上映週', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            {'id': 'show_num', 'label': '上映回数', 'type': 'number'},
        ]]

        # add rows
        today = datetime.datetime.today()
        publish_date = parse('2017/6/10')
        weeks = (today - publish_date).days // 7 + 1
        for week in range(weeks):
            start = publish_date + datetime.timedelta(days=week * 7)
            end = start + datetime.timedelta(days=6)
            if week == weeks - 1: # latest week
                haxes_label = '第{}週\n{}〜'.format(week + 1,
                                                      start.strftime('%-m/%-d'))
            else:
                haxes_label = '第{}週\n{}〜{}'.format(week + 1,
                                                      start.strftime('%-m/%-d'),
                                                      end.strftime('%-m/%-d'))
            cursor = db.mimorin_daily.aggregate([{
                '$match': {'_id': {'$gte': start, '$lte': end}},
            }, {
                '$group': {'_id': haxes_label,
                           'sell': {'$sum': '$sell'},
                           'show_num': {'$sum': '$show_num'}},
            }])
            if cursor.alive:
                i = cursor.next()
                row = [
                    i['_id'],
                    i['sell'],
                    i['show_num'],
                ]
                data.append(row)
        # additional empty data
        data.append(['第{}週'.format(len(data)), 0, None])
    elif endpoint == 'v2/kinpri/daily.json':
        # make header
        data = [[
            {'id': '_id', 'label': '日付', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            {'id': 'show_num', 'label': '上映回数', 'type': 'number'},
        ]]
        
        # add rows
        for i in db.mimorin_daily_kinpri1.find().sort('_id'):
            date = i['_id']
            row = [
                date.strftime('%-m/%-d({})'.format(get_weekday(i['_id']))),
                i['sell'],
                i['show_num'],
            ]
            data.append(row)
        # additional empty data
        date = date + datetime.timedelta(days=1)
        date = date.strftime('%-m/%-d({})'.format(get_weekday(date)))
        data.append([date, 0, None])
    elif endpoint == 'v2/kinpri/weekly.json':
        # make header
        data = [[
            {'id': '_id', 'label': '上映週', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            {'id': 'show_num', 'label': '上映回数', 'type': 'number'},
        ]]

        # add rows
        last_date = parse('2017/3/17') # last date recorded
        publish_date = parse('2016/1/9')
        weeks = (last_date - publish_date).days // 7 + 1
        for week in range(weeks):
            start = publish_date + datetime.timedelta(days=week * 7)
            end = start + datetime.timedelta(days=6)
            if week == weeks - 1: # latest week
                haxes_label = '第{}週\n{}〜'.format(week + 1,
                                                      start.strftime('%Y/%-m/%-d'))
            else:
                haxes_label = '第{}週\n{}〜{}'.format(week + 1,
                                                      start.strftime('%Y/%-m/%-d'),
                                                      end.strftime('%Y/%-m/%-d'))
            cursor = db.mimorin_daily_kinpri1.aggregate([{
                '$match': {'_id': {'$gte': start, '$lte': end}},
            }, {
                '$group': {'_id': haxes_label,
                           'sell': {'$sum': '$sell'},
                           'show_num': {'$sum': '$show_num'}},
            }])
            if cursor.alive:
                i = cursor.next()
                row = [
                    i['_id'],
                    i['sell'],
                    i['show_num'],
                ]
                data.append(row)
    elif endpoint == 'v1/korea/daily.json' or \
         endpoint == 'v2/korea-kinpri2/daily.json':
        # make header
        data = [[
            {'id': '_id', 'label': '日付', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            {'id': 'box_office', 'label': '興行収入', 'type': 'number'},
        ]]

        # add rows
        for i in db.korea.find().sort('_id'):
            row = [
                i['_id'].strftime('%-m/%-d({})'.format(get_weekday(i['_id']))),
                i['sell'],
                i['box_office'],
            ]
            data.append(row)
        # additional empty data
        date = i['_id'] + datetime.timedelta(days=1)
        date = date.strftime('%-m/%-d({})'.format(get_weekday(date)))
        data.append([date, 0, None])
    elif endpoint == 'v2/korea-kinpri2/weekly.json':
        # make header
        data = [[
            {'id': '_id', 'label': '上映週', 'type': 'string'},
            {'id': 'sell', 'label': '販売座席数', 'type': 'number'},
            {'id': 'box_office', 'label': '興行収入', 'type': 'number'},
        ]]

        # add rows
        today = datetime.datetime.today()
        publish_date = parse('2017/6/10')
        weeks = (today - publish_date).days // 7 + 1
        for week in range(weeks):
            start = publish_date + datetime.timedelta(days=week * 7)
            end = start + datetime.timedelta(days=6)
            if week == weeks - 1: # latest week
                haxes_label = '第{}週\n{}〜'.format(week + 1,
                                                      start.strftime('%-m/%-d'))
            else:
                haxes_label = '第{}週\n{}〜{}'.format(week + 1,
                                                      start.strftime('%-m/%-d'),
                                                      end.strftime('%-m/%-d'))
            cursor = db.korea.aggregate([{
                '$match': {'_id': {'$gte': start, '$lte': end}},
            }, {
                '$group': {'_id': haxes_label,
                           'sell': {'$sum': '$sell'},
                           'box_office': {'$sum': '$box_office'}},
            }])
            if cursor.alive:
                i = cursor.next()
                row = [
                    i['_id'],
                    i['sell'],
                    i['box_office'],
                ]
                data.append(row)
        # additional empty data
        data.append(['第{}週'.format(len(data)), 0, None])
    else:
        data = []
    return JsonResponse(data, safe=False)

