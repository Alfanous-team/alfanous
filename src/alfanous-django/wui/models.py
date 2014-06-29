from django.db import models
from django.contrib.auth.models import User

class Visit (models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField( max_length = 15 ) #may be this should be the key
    host = models.CharField( max_length = 255 )
    referer = models.CharField( max_length = 255 )
    request = models.CharField( max_length = 255 )
    query = models.CharField( max_length=255)
    sorted_by = models.CharField( max_length=10)
    recitation = models.CharField( max_length=30)
    translation =  models.CharField( max_length=30)

    def __unicode__(self):
            return u"%d.%s" % (self.id,self.query)
