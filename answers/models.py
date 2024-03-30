# Em answers/models.py

from django.db import models
from suppliers.models import Supplier
from cotacao.models import ItemCotacao

class Answer(models.Model):
    item_cotacao = models.ForeignKey(ItemCotacao, on_delete=models.CASCADE, related_name='answers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_answers')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_cotacao} - {self.supplier} - {self.price}"
