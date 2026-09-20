from django.core.management.base import BaseCommand
from django.db import transaction

from gymapp.models import User
from gymapp.services import create_admin


class Command(BaseCommand):
    help = (
        'Create the initial FitFocus administrator account if it does not already exist. '
        'Does not create members, trainers, or sample gym records.'
    )

    ADMIN_EMAIL = 'admin@gmail.com'
    ADMIN_PASSWORD = 'admin123'
    ADMIN_USERNAME = 'admin'

    @transaction.atomic
    def handle(self, *args, **options):
        email = User.objects.normalize_email(self.ADMIN_EMAIL)
        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Administrator {email} already exists. No changes made.')
            )
            return

        create_admin(
            email=email,
            password=self.ADMIN_PASSWORD,
            username=self.ADMIN_USERNAME,
        )
        self.stdout.write(self.style.SUCCESS(f'Created administrator {email}.'))
        self.stdout.write('Log in on /login/ with role Admin. The password is stored as a Django hash, not as plain text.')
