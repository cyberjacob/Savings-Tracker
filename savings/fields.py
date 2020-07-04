from django.db import models

class CurrencyField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(decimal_places=4, max_digits=10, *args, **kwargs)

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        if val is None:
            data = ''
        elif val.year == val.day == val.month == 1:
            data = date_111_str
        else:
            data = datetime_safe.new_date(val).strftime("%Y-%m-%d")
        return data

    def get_prep_value(self, value):
        if value == date_111_str:
            value = datetime.date(1,1,1)
        return super(MyCustomDateField,self).get_prep_value(self, value)