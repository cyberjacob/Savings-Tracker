import datetime
import json

from django.http import JsonResponse
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
def test(request):
    """Used by Grafana to test basic connectivity"""
    return JsonResponse("OK", safe=False)


@csrf_exempt
def search(request):
    """Used by Grafana to find metrics"""
    return JsonResponse(["accounts", "balances", "APRs", "returns"], safe=False)


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
                            float(account.starting_balance.balance) if account.starting_balance else None,
                            float(account.current_balance.balance) if account.current_balance else None,
                            float(account.total_topup),
                            float(account.average_APR),
                            float(account.returns),
                            account.balance_OK,
                            account.__str__(),
                            account.bank_name,
                            account.account_name,
                            account.account_number,
                            account.sort_code,
                            float(account.predicted_interest),
                            float(account.interest_min) if account.interest_min else None,
                            float(account.interest_max) if account.interest_max else None,
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
                            float(account.starting_balance.balance) if account.starting_balance else None,
                            float(account.current_balance.balance) if account.current_balance else None,
                            float(account.total_topup) if account.total_topup else None,
                            float(account.average_APR) if account.average_APR else None,
                            float(account.returns) if account.returns else None,
                            account.balance_OK,
                            account.__str__(),
                            account.bank_name,
                            account.account_name,
                            account.account_number,
                            account.sort_code,
                            float(account.predicted_interest) if account.predicted_interest else None,
                            float(account.interest_min) if account.interest_min else None,
                            float(account.interest_max) if account.interest_max else None,
                            account.instant_withdrawal
                        ] for account in accounts],
                    "type": "table"
                })
        elif target["target"] == "balances":
            for account in models.Account.objects.all():
                response.append({
                    "target": str(account),
                    "datapoints": sorted([
                        [
                            float(balance.balance),
                            int(datetime.datetime.combine(balance.timestamp, datetime.datetime.min.time()).timestamp()*1000)
                        ] for balance in account.balance_set.all()], key=lambda tup: tup[1])
                })
        elif target["target"] == "APRs":
            for account in models.Account.objects.all():
                response.append({
                    "target": str(account),
                    "datapoints": sorted([
                        [
                            float(balance.APR) if balance.APR else None,
                            int(datetime.datetime.combine(balance.timestamp, datetime.datetime.min.time()).timestamp()*1000)
                        ] for balance in account.balance_set.all()], key=lambda tup: tup[1])
                })
        elif target["target"] == "returns":
            for account in models.Account.objects.all():
                response.append({
                    "target": str(account),
                    "datapoints": sorted([
                        [
                            float(balance.returns) if balance.returns else None,
                            int(datetime.datetime.combine(balance.timestamp, datetime.datetime.min.time()).timestamp()*1000)
                        ] for balance in account.balance_set.all()], key=lambda tup: tup[1])
                })

    return JsonResponse(response, safe=False)


@csrf_exempt
def annotations(request):
    return JsonResponse([], safe=False)
