from django.db import models

class User(models.Model):
    full_name = models.CharField(max_length=100)
    dob = models.DateField()
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    height = models.FloatField()
    weight = models.FloatField()
    address = models.TextField()
    goal = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name