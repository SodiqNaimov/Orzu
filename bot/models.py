from django.db import models

# Create your models here.
class Savat(models.Model):
    user_id = models.TextField()
    product_name =models.TextField()
    count = models.TextField()
    price = models.IntegerField()
    total_price = models.IntegerField()

    class Meta:
        db_table = "savat"
class Sorov(models.Model):
    user_id = models.TextField()
    mahsulot_zakasi = models.IntegerField()
    class Meta:
        db_table = "sorov"