from django.db import models

class Member(models.Model):
    name = models.CharField(max_length=100)
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
        return self.name

class Trainer(models.Model):
    trainer_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    experience = models.CharField(max_length=50)
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    password = models.CharField(max_length=100, default='trainer123')

    def __str__(self):
        return self.name

class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name