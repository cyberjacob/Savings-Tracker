import json
import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import models

ACCOUNT_DEF = [
    {"text": "Starting Balance",    "type": "number"},
    {"text": "Current Balance",     "type": "number"},
    {"text": "Total Topup",         "type": "number"},
    {"text": "Average APR",         "type": "number"},
    {"text": "Returns",             "type": "number"},
    {"text": "Balance OK",          "type": "bool"},
    {"text": "Name",                "type": "string"},
    {"text": "Bank Name",           "type": "string"},
    {"text": "Account Name",        "type": "string"},
    {"text": "Account Number",      "type": "string"},
    {"text": "Sort Code",           "type": "string"},
    {"text": "Predicted Interest",  "type": "number"},
    {"text": "Interest Min",        "type": "number"},
    {"text": "Interest Max",        "type": "number"},
    {"text": "Instant Withdrawal",  "type": "bool"},
]


# Create your views here.
@csrf_exempt
def test():
    """Used by Grafana to test basic connectivity"""
    return JsonResponse("OK")


@csrf_exempt
def search(request):
    """Used by Grafana to find metrics"""
    return JsonResponse(["accounts", "balances"], safe=False)


@csrf_exempt
def query(request):
    response = []
    data = json.loads(request.body)
    for target in data["targets"]:
        if target["target"] == "accounts":
            if "data" in target and target["data"] is not None and "pk" in target["data"]:
                account = models.Account.objects.get(pk=target["data"]["pk"])
                response.append({
                    "columns": ACCOUNT_DEF,
                    "rows": [
                        [
                            account.starting_balance.balance if account.starting_balance else None,
                            account.current_balance.balance if account.current_balance else None,
                            account.total_topup,
                            account.average_APR,
                            account.returns,
                            account.balance_OK,
                            account.__str__(),
                            account.bank_name,
                            account.account_name,
                            account.account_number,
                            account.sort_code,
                            account.predicted_interest,
                            account.interest_min,
                            account.interest_max,
                            account.instant_withdrawal
                        ],
                    ],
                    "type": "table"
                })
            else:
                accounts = models.Account.objects.all()
                response.append({
                    "columns": ACCOUNT_DEF,
                    "rows":
                        [[
                            account.starting_balance.balance if account.starting_balance else None,
                            account.current_balance.balance if account.current_balance else None,
                            account.total_topup,
                            account.average_APR,
                            account.returns,
                            account.balance_OK,
                            account.__str__(),
                            account.bank_name,
                            account.account_name,
                            account.account_number,
                            account.sort_code,
                            account.predicted_interest,
                            account.interest_min,
                            account.interest_max,
                            account.instant_withdrawal
                        ] for account in accounts],
                    "type": "table"
                })
        if target["target"] == "balances":
            for account in models.Account.objects.all():
                response.append({
                    "target": str(account),
                    "datapoints": [
                        [balance.balance, int(datetime.datetime.combine(balance.timestamp, datetime.datetime.min.time()).timestamp()*1000)]
                        for balance in account.balance_set.all()]
                })

    return JsonResponse(response, safe=False)


@csrf_exempt
def annotations(request):
    return JsonResponse([], safe=False)
