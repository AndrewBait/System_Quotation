from django.apps import AppConfig


class RespostasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'respostas'
    
    def ready(self):
        import respostas.signals
