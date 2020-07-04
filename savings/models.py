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

    has_interest_min = models.BooleanField()
    interest_min = models.DecimalField(decimal_places=4, max_digits=10, blank=True, null=True)

    has_interest_max = models.BooleanField()
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
        return self.balance_set.aggregate(models.Avg('APR'))['APR__avg']

    @property
    def returns(self) -> Decimal:
        """Total of all interest payments"""
        return self.current_balance.interest_increase - self.total_topup

    @property
    def balance_OK(self) -> bool:
        """Current balance allows interest payments"""
        return (not self.has_interest_min and not self.has_interest_max) or (
                (self.has_interest_min and (self.current_balance.balance > self.interest_min)) and
                (self.has_interest_max and (self.current_balance.balance < self.interest_max)))

    def __str__(self):
        return f'Account: {self.bank_name} {self.account_name}'

    def starting_balance_localized(self):
        return settings.CURRENCY_FORMAT.format(self.starting_balance.balance)
    starting_balance_localized.short_description = 'Starting Balance'

    def current_balance_localized(self):
        return settings.CURRENCY_FORMAT.format(self.current_balance.balance)
    current_balance_localized.short_description = 'Current Balance'

    def total_topup_localized(self):
        return settings.CURRENCY_FORMAT.format(self.total_topup)
    total_topup_localized.short_description = 'Total Topup'

    def average_APR_localized(self):
        return "{:.2%}".format(self.average_APR)
    average_APR_localized.short_description = 'Average APR'

    def returns_localized(self):
        return settings.CURRENCY_FORMAT.format(self.returns)
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

    @property
    def days_since_last_check(self) -> datetime.timedelta:
        """Number of days since the previous balance record"""
        return self.timestamp - self.previous_check.timestamp

    @property
    def interest_increase(self) -> Decimal:
        """Current balance of the account, excluding the most recent topup"""
        return self.balance - self.topup

    @computed(models.DecimalField(decimal_places=4, max_digits=6, null=True), depends=[['self', ['balance', 'topup', 'timestamp']]])
    def APR(self) -> Optional[Decimal]:
        """Current yearly interest for the account, calculated since the last balance record"""
        previous = self.previous_check
        if previous is not None:
            return (((self.interest_increase / previous.balance) - 1) / self.days_since_last_check.days) * 365
        else:
            return None

    def __str__(self):
        return f"Balance: {self.account} on {self.timestamp} - {settings.CURRENCY_FORMAT}".format(self.balance)

    def APR_localized(self):
        return "{:.2%}".format(self.APR)
    APR_localized.short_description = 'APR'
