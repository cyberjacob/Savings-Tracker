from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import models


# Create your views here.
@csrf_exempt
def test():
    """Used by Grafana to test basic connectivity"""
    return "OK"


@csrf_exempt
def search(request):
    """Used by Grafana to find metrics"""
    return '["accounts", "balances"]'


@csrf_exempt
def query(request):
    return ""


@csrf_exempt
def annotations(request):
    return "[]"
