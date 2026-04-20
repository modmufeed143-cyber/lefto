from django.db import models
from django.contrib.auth.models import User
from django.db.models import FileField

# Create your models here.


class user_table(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    photo=models.FileField()
    phone=models.BigIntegerField()
    address=models.TextField()
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)

class hotel_table(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    phone=models.BigIntegerField()
    logo=models.FileField()
    proof=models.FileField()
    address=models.TextField()
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.CharField(max_length=100,default='pending')

class food_table(models.Model):
    name=models.CharField(max_length=100)
    details=models.CharField(max_length=100)
    image=models.FileField()
    mfg=models.CharField(max_length=300)
    quantity=models.IntegerField()
    price=models.FloatField()
    HOTEL=models.ForeignKey(hotel_table,on_delete=models.CASCADE)
    status=models.CharField(max_length=100)

class leftover_foodtable(models.Model):
    FOOD=models.ForeignKey(food_table,on_delete=models.CASCADE)
    discountprice=models.FloatField()
    date=models.DateField(auto_now_add=True)
    valid=models.CharField(max_length=100)
    status=models.CharField(max_length=100)

class complaint_table(models.Model):
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    complaint=models.CharField(max_length=100)
    replay=models.TextField()
    date=models.DateField()

class order_table(models.Model):
    FOOD=models.ForeignKey(food_table,on_delete=models.CASCADE)
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    date=models.DateField()
    status=models.CharField(max_length=100)

class leftover_order_table(models.Model):
    LEFT=models.ForeignKey(leftover_foodtable,on_delete=models.CASCADE)
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    status=models.CharField(max_length=100)
    date=models.DateField()


    

