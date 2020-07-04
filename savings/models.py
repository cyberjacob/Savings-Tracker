from __future__ import annotations

from decimal import Decimal
from typing import Optional

from computedfields.models import ComputedFieldsModel, computed
from django.db import models
from django.conf import settings
import datetime


# Create your models here.
class Account(models.Model):
    """Used to track a single bank account"""
    bank_name = models.CharField(max_length=50)
    account_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=25, blank=True)
    sort_code = models.CharField(max_length=10, blank=True)
    predicted_interest = models.DecimalField(decimal_places=4, max_digits=6)

    interest_min = models.DecimalField(decimal_places=4, max_digits=10, blank=True, null=True)
    interest_max = models.DecimalField(decimal_places=4, max_digits=10, blank=True, null=True)

    instant_withdrawal = models.BooleanField()

    @property
    def starting_balance(self) -> Balance:
        """First available balance for this account"""
        return self.balance_set.order_by('timestamp').first()

    @property
    def current_balance(self) -> Balance:
        """Most recent available balance for this account"""
        return self.balance_set.order_by('timestamp').last()

    @property
    def total_topup(self) -> Decimal:
        """Total amount tranfered into this account from external funds"""
        return self.balance_set.aggregate(models.Sum('topup'))['topup__sum']

    @property
    def average_APR(self) -> Decimal:
        """Average yearly interest %"""
        return self.balance_set.aggregate(models.Avg(models.F('APR') * models.F('days_since_last_check')))['APR__avg']

    @property
    def returns(self) -> Optional[Decimal]:
        """Total of all interest payments"""
        if self.current_balance:
            return self.current_balance.interest_increase - self.total_topup
        else:
            return None

    @property
    def balance_OK(self) -> Optional[bool]:
        """Current balance allows interest payments"""
        if (self.interest_max is None) and (self.interest_min is None):
            return True
        if self.current_balance is None:
            return None
        return ((self.interest_min is None) or (self.current_balance.balance >= self.interest_min)) and \
               ((self.interest_max is None) or (self.current_balance.balance <= self.interest_max))


    def __str__(self):
        return f'{self.bank_name} - {self.account_name}'

    def starting_balance_localized(self):
        if self.starting_balance:
            return settings.CURRENCY_FORMAT.format(self.starting_balance.balance)
        else:
            return "-"
    starting_balance_localized.short_description = 'Starting Balance'

    def current_balance_localized(self):
        if self.current_balance:
            return settings.CURRENCY_FORMAT.format(self.current_balance.balance)
        else:
            return "-"
    current_balance_localized.short_description = 'Current Balance'

    def total_topup_localized(self):
        if self.total_topup:
            return settings.CURRENCY_FORMAT.format(self.total_topup)
        else:
            return "-"
    total_topup_localized.short_description = 'Total Topup'

    def average_APR_localized(self):
        if self.average_APR:
            return "{:.2%}".format(self.average_APR)
        else:
            return "-"
    average_APR_localized.short_description = 'Average APR'

    def returns_localized(self):
        if self.returns:
            return settings.CURRENCY_FORMAT.format(self.returns)
        else:
            return "-"
    returns_localized.short_description = 'Returns'


class Balance(ComputedFieldsModel):
    """Point-in-time record of the balance for an account"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    timestamp = models.DateField()
    balance = models.DecimalField(decimal_places=4, max_digits=10)
    topup = models.DecimalField(decimal_places=4, max_digits=10, default=0)

    @property
    def previous_check(self) -> Balance:
        """Most recent previous balance record for this account"""
        return Balance.objects.filter(account=self.account, timestamp__lt=self.timestamp).order_by('timestamp').last()

    @computed(models.IntegerField(null=True), [['self', ['timestamp']]])
    def days_since_last_check(self) -> Optional[int]:
        """Number of days since the previous balance record"""
        if self.previous_check:
            return (self.timestamp - self.previous_check.timestamp).days
        else:
            return None

    @property
    def interest_increase(self) -> Decimal:
        """Current balance of the account, excluding the most recent topup"""
        return self.balance - self.topup

    @computed(models.DecimalField(decimal_places=4, max_digits=6, null=True), depends=[['self', ['balance', 'topup', 'timestamp']]])
    def APR(self) -> Optional[Decimal]:
        """Current yearly interest for the account, calculated since the last balance record"""
        previous = self.previous_check
        if previous is not None:
            return (((self.interest_increase / previous.balance) - 1) / self.days_since_last_check) * 365
        else:
            return None

    def __str__(self):
        return f"{self.account} Balance on {self.timestamp} - {settings.CURRENCY_FORMAT}".format(self.balance)

    def APR_localized(self):
        if self.APR:
            return "{:.2%}".format(self.APR)
        else:
            return "-"
    APR_localized.short_description = 'APR'
