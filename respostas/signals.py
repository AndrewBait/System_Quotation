# respostas/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RespostaCotacao
from accounts.models import Notification

@receiver(post_save, sender=RespostaCotacao)
def create_notification_on_response(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.cotacao.usuario_criador,
            message=f'Fornecedor {instance.fornecedor.name} da empresa {instance.fornecedor.company} respondeu a cotação {instance.cotacao.nome}.',
            url='#',  # Defina a URL apropriada para a cotação ou resposta
        )
