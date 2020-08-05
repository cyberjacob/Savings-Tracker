from django.contrib import admin
from . import models
from computedfields.models import update_dependent


def update_APRs(modeladmin, request, queryset):
    update_dependent(models.Balance.objects.filter(account__in=queryset))


update_APRs.short_description = "Update Calculated APR"


# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    """Admin registration for the Account model"""
    readonly_fields = [
        'starting_balance_localized',
        'current_balance_localized',
        'total_topup_localized',
        'average_APR_localized',
        'returns_localized',
        'balance_OK'
    ]
    list_display = [
        'bank_name',
        'account_name',
        'current_balance_localized',
        'average_APR_localized',
        'balance_OK'
    ]

    actions = [update_APRs]

    def get_queryset(self, request):
        qs = super(AccountAdmin, self).get_queryset(request)
        qs = qs.order_by(F('average_APR_localized'))
        return qs


class BalanceAdmin(admin.ModelAdmin):
    """Admin registration for the Balance model"""
    readonly_fields = ['days_since_last_check', 'APR_localized']


admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Balance, BalanceAdmin)
