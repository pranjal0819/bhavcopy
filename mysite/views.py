import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect

from .bhavcopy import Bhavcopy
from .redis_client import RedisClient
from .tasks import refresh_data


def get_bhavcopy(request):
    r = RedisClient().connect(decode_responses=True)

    keys = r.keys('BSE:*')
    dump_data = r.mget(keys)
    data = [json.loads(value) for value in dump_data]

    date = datetime.strptime(r.get('date'), Bhavcopy.DATE_FORMAT) if r.get('date') else datetime.now()
    response = {'data': data, 'latest_date': date.strftime("%b %d, %Y %H:%M")}

    return render(request, 'index.html', response)


def search_bhavcopy(request):
    r = RedisClient().connect(decode_responses=True)

    query = request.GET.get('query', None)
    name = f'*{query.strip().upper()}*' if query else '*'

    keys = r.keys(f'BSE:*:{name}')
    dump_data = r.mget(keys)
    data = [json.loads(value) for value in dump_data]

    date = datetime.strptime(r.get('date'), Bhavcopy.DATE_FORMAT) if r.get('date') else datetime.now()
    response = {'data': data, 'latest_date': date.strftime("%b %d, %Y %H:%M")}

    return JsonResponse(response)


def fetch_bse_date(request):
    refresh_data.delay()
    return redirect('home')


def clear_all_data(request):
    r = RedisClient().connect(decode_responses=True)
    r.flushall()

    return redirect('home')
