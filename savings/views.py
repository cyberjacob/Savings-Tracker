from django.shortcuts import render
from . import models

# Create your views here.
def test():
    """Used by Grafana to test basic connectivity"""
    return "OK"

def search():
    """Used by Grafana to find metrics"""
    return '["accounts", "balances"]'

def query():
    return ""

def annotations():
    return "[]"
