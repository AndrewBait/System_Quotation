# accounts/context_processors.py
from django.utils import timezone
from respostas.models import RespostaCotacao
from suppliers.models import Supplier
from django.db.models import Q

def notification_processor(request):
    notifications = []

    if request.user.is_authenticated:
        # Notificações de respostas de fornecedores nas últimas 24 horas
        resposta_cotacoes = RespostaCotacao.objects.filter(data_resposta__gte=timezone.now() - timezone.timedelta(days=1))
        for resposta in resposta_cotacoes:
            notifications.append({
                'message': f'Fornecedor {resposta.fornecedor.name} da empresa {resposta.fornecedor.company} respondeu a cotação {resposta.cotacao.nome}.',
                'url': '#'  # Você pode definir a URL para a cotação específica ou resposta específica
            })

        # Notificações de prazo de pedidos próximos
        fornecedores_perto_do_prazo = Supplier.objects.filter(
            Q(order_response_deadline__lte=timezone.now() + timezone.timedelta(days=3))
        )
        for fornecedor in fornecedores_perto_do_prazo:
            notifications.append({
                'message': f'O horário de envio do pedido de {fornecedor.name} da empresa {fornecedor.company} está fechando.',
                'url': '#'
            })

    return {'notifications': notifications}
