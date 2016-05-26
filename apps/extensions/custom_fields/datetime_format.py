from django.db import models
import datetime

FORMAT_STRING = "Y-m-d H:M:S"

class ConvertingDateTimeFeild(models.DateTimeField):
    def get_prep_value(self, value):
        return str(datetime.strptime(value, FORMAT_STRING))