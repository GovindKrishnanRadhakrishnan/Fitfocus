from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', User.Role.MEMBER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        TRAINER = 'trainer', 'Trainer'
        MEMBER = 'member', 'Member'

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile',
    )
    username = models.CharField(max_length=150)

    def __str__(self):
        return self.username


class Trainer(models.Model):
    trainer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer_profile',
    )
    fullname = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    specialization = models.CharField(max_length=150)
    qualification = models.CharField(max_length=150)

    def __str__(self):
        return self.fullname

    @property
    def email(self):
        return self.user.email


class Member(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    member_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile',
    )
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_members',
    )
    fullname = models.CharField(max_length=150)
    dob = models.DateField()
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text='Height in centimetres')
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text='Weight in kilograms')
    goal = models.CharField(max_length=150)

    def __str__(self):
        return self.fullname

    @property
    def email(self):
        return self.user.email

    def calculate_bmi(self, weight=None):
        from .utils import calculate_bmi

        return calculate_bmi(weight if weight is not None else self.weight, self.height)

    def clean(self):
        if self.height is not None and self.height <= 0:
            raise ValidationError({'height': 'Height must be greater than zero.'})
        if self.weight is not None and self.weight <= 0:
            raise ValidationError({'weight': 'Weight must be greater than zero.'})


class Progress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='progress_records',
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField()
    updated_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-updated_date', '-progress_id']

    def __str__(self):
        return f'{self.member.fullname} ({self.updated_date})'

    @property
    def bmi(self):
        return self.member.calculate_bmi(self.weight)


class DietPlan(models.Model):
    diet_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='diet_plans',
    )
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='diet_plans',
    )
    breakfast = models.TextField()
    lunch = models.TextField()
    dinner = models.TextField()
    snacks = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Diet plan for {self.member.fullname}'


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'Cash', 'Cash'
        CARD = 'Card', 'Card'
        UPI = 'UPI', 'UPI'
        BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer'

    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        PAID = 'Paid', 'Paid'
        FAILED = 'Failed', 'Failed'

    payment_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=30, choices=Method.choices)
    payment_status = models.CharField(max_length=20, choices=Status.choices)

    class Meta:
        ordering = ['-payment_date', '-payment_id']

    def __str__(self):
        return f'Payment {self.payment_id} - {self.member.fullname}'


class WorkoutPlan(models.Model):
    workout_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='workout_plans',
    )
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='workout_plans',
    )
    workout_name = models.CharField(max_length=150)
    exercise_type = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    sets = models.PositiveIntegerField()
    repetitions = models.PositiveIntegerField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.workout_name} ({self.member.fullname})'
