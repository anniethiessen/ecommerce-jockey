from django.apps import AppConfig


class MainAppConfig(AppConfig):
    name = 'main'
    verbose_name = 'Main'

    # def ready(self):
    #     # noinspection PyUnresolvedReferences
    #     from .signals import *
