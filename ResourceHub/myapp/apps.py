from django.apps import AppConfig


class MyappConfig(AppConfig):
    name = 'myapp'

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        import myapp.signals
