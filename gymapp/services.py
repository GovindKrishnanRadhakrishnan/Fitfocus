from django.db import transaction

from .models import Admin, Member, Trainer, User


@transaction.atomic
def create_member(password, **details):
    email = User.objects.normalize_email(details.pop('email'))
    user = User.objects.create_user(
        email=email,
        password=password,
        role=User.Role.MEMBER,
        first_name=details.get('fullname', '').split(' ')[0],
    )
    return Member.objects.create(user=user, **details)


@transaction.atomic
def create_trainer(password, **details):
    email = User.objects.normalize_email(details.pop('email'))
    user = User.objects.create_user(
        email=email,
        password=password,
        role=User.Role.TRAINER,
        first_name=details.get('fullname', '').split(' ')[0],
        is_staff=False,
    )
    return Trainer.objects.create(user=user, **details)


@transaction.atomic
def create_admin(email, password, username):
    email = User.objects.normalize_email(email)
    user = User.objects.create_user(
        email=email,
        password=password,
        role=User.Role.ADMIN,
        is_staff=True,
        is_superuser=True,
        first_name=username,
    )
    return Admin.objects.create(user=user, username=username)


@transaction.atomic
def update_trainer(trainer, *, password=None, email=None, **details):
    for field, value in details.items():
        setattr(trainer, field, value)
    trainer.save()
    user = trainer.user
    if email and user.email != email:
        user.email = email
    if password:
        user.set_password(password)
    user.save()
    return trainer
