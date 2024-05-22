import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Adiciona a raiz do projeto ao PYTHONPATH
sys.path.append('C:/Users/cj3014916/System_Quotation/System_Quotation')

# Ajuste o DJANGO_SETTINGS_MODULE para 'app.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from products.models import Product, ProductPriceHistory

def generate_random_date_within_last_year():
    today = datetime.today()
    one_year_ago = today - timedelta(days=365) 
    random_date = one_year_ago + timedelta(days=random.randint(0, 365))  
    return random_date.date()  # Retorna apenas a data (sem hora)

def generate_price_history():
    products = Product.objects.all()

    for product in products:
        ProductPriceHistory.objects.filter(product=product).delete()

        dates = set()
        while len(dates) < 360:  # Garante 360 datas únicas
            new_date = generate_random_date_within_last_year()
            dates.add(new_date)

        for date in dates:
            price = Decimal(random.uniform(0.001, 59.999)).quantize(Decimal("0.001"))
            ProductPriceHistory.objects.create(
                product=product,
                price=price, 
                date=date
            )

if __name__ == "__main__":
    generate_price_history()
    print("Dados gerados com sucesso!")