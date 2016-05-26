from django.db import models
import base64

class Base64Field(models.Field):
    __metaclass__ = models.SubfieldBase 

    def __init__(self, *args, **kwargs):
        #self.td = base64.b64encode(self.td)
        super(Base64Field, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'text'
    
    #def pre_save(self, model_instance, add):
        #return base64.b64encode(model_instance.name)

    def to_python(self, value):
        #todo improve later
        try:
            value = base64.b64decode(value)
        except:
            pass
        return value

    def get_prep_value(self, value):
        return base64.b64encode(value)
    