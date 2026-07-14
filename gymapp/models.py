from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('Admin','Admin'),
        ('Trainer','Trainer'),
        ('Member','Member'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.name