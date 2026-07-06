from django.db import models

class Member(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    height = models.FloatField()
    weight = models.FloatField()
    goal = models.CharField(max_length=50)

    def __str__(self):
        return self.name