"""
This module contains a class that automatically creates a super user
if it doesn't already exist.
------------------------------------------------------------------------
"""


from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(
                username=settings.SUPERUSER_EMAIL_ADDRESS
        ).exists():
            User.objects.create_superuser(
                settings.SUPERUSER_EMAIL_ADDRESS,
                settings.SUPERUSER_EMAIL_ADDRESS,
                settings.SUPERUSER_PASSWORD
            )
            print('Superuser created.')
        else:
            print('Superuser already exists.')