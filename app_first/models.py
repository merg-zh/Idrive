from django.db import models
from django_mysql.models import ListCharField

class data(models.Model):
    username = models.CharField(max_length=50)
    title = ListCharField(
        base_field=models.CharField(max_length=100),
        size = 1000,
        max_length=(101 * 1000),
    )
    play_list = ListCharField(
        base_field=models.CharField(max_length=10000),
        size = 2,
        max_length = (2 * 10001),
    )
    volume = models.IntegerField(default=50)
