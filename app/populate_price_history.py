import os
import sys
import django
import random
from datetime import datetime, timedelta

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append('C:/Users/cj3014916/System_Quotation/System_Quotation')

# Ajuste o DJANGO_SETTINGS_MODULE para 'app.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from products.models import Product, ProductPriceHistory

def generate_price_history():
    products = Product.objects.all()
    today = datetime.today()

    for product in products:
        for day in range(360):  # Últimos 360 dias
            date = today - timedelta(days=day)
            price = round(random.uniform(10.0, 500.0), 2)  # Gera um preço entre 10.0 e 500.0

            ProductPriceHistory.objects.create(
                product=product,
                price=price,
                date=date
            )

if __name__ == "__main__":
    generate_price_history()
    print("Dados gerados com sucesso!")
