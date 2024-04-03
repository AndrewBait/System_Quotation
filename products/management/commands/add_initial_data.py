from django.core.management.base import BaseCommand
from products.models import Departamento, Category, Subcategory

# Dados iniciais
initial_data = {
    "Hortifrúti": {
        "Frutas": ["Frescas", "Secas", "Exóticas"],
        "Legumes": ["Raízes", "Tubérculos", "Folhosos"],
        "Verduras": ["Folhas verdes", "Ervas aromáticas"]
    },
    "Padaria": {
        "Pães": ["Francês", "Integral", "De forma", "Artesanais"],
        "Doces": ["Bolos", "Tortas", "Doces variados", "Pães doces"],
        "Salgados": ["Pães de queijo", "Coxinhas", "Empadas"]
    },
    "Açougue": {
        "Carnes Vermelhas": ["Cortes bovinos", "Suínos", "Cordeiro"],
        "Aves": ["Frango", "Peru", "Pato"],
        "Peixes e Frutos do Mar": ["Peixes frescos", "Congelados", "Mariscos"]
    },
    "Frios e Laticínios": {
        "Queijos": ["Nacionais", "Importados", "Frescos", "Curados"],
        "Laticínios": ["Leite", "Iogurtes", "Manteigas", "Cremes"],
        "Embutidos": ["Presuntos", "Salames", "Salsichas"]
    },
    "Mercearia Seca": {
        "Cereais e Grãos": ["Arroz", "Feijão", "Lentilhas", "Quinoa"],
        "Massas": ["Espaguete", "Macarrão", "Lasanhas"],
        "Enlatados e Conservas": ["Atum", "Sardinha", "Legumes em conserva"],
        "Condimentos e Temperos": ["Sal", "Pimenta", "Ervas", "Molhos"],
        "Doces e Sobremesas": ["Geleias", "Compotas", "Chocolates"]
    },
    "Bebidas": {
        "Não Alcoólicas": ["Águas", "Sucos", "Refrigerantes", "Chás"],
        "Alcoólicas": ["Cervejas", "Vinhos", "Destilados"]
    },
    "Congelados": {
        "Carnes e Aves": ["Cortes diversos", "Prontos para consumo"],
        "Frutos do Mar": ["Peixes", "Camarões", "Lulas"],
        "Pratos Prontos": ["Lasanhas", "Pizzas", "Sopas"],
        "Vegetais": ["Misturas de legumes", "Ervilhas", "Milho"],
        "Sorvetes e Sobremesas": ["Diversos sabores e marcas"]
    },
    "Produtos Naturais e Orgânicos": {
        "Alimentos Orgânicos": ["Frutas", "Legumes", "Carnes com certificação orgânica"],
        "Superalimentos": ["Chia", "Linhaça", "Quinoa"],
        "Produtos Integrais": ["Pães", "Cereais", "Massas"],
        "Alimentos Funcionais": ["Produtos voltados para saúde específica"]
    },
    "Snacks e Petiscos": {
        "Salgadinhos": ["Batatas fritas", "Amendoins", "Mix de nuts"],
        "Doces": ["Barras de cereal", "Chocolates", "Biscoitos doces"],
        "Biscoitos e Crackers": ["Variedades salgadas", "Integrais"]
    },
    "Gourmet e Importados": {
        "Queijos e Frios": ["Seleções especiais", "Importadas"],
        "Azeites e Vinagres": ["Diversidade de origens", "Sabores"],
        "Doces e Conservas": ["Produtos exclusivos", "De nicho"]
    },
    "Diet e Light": {
        "Alimentos sem Glúten": ["Pães", "Massas", "Biscoitos"],
        "Alimentos sem Lactose": ["Leites", "Queijos", "Iogurtes"],
        "Produtos com Baixas Calorias": ["Refeições prontas", "Snacks"]
    }
}

class Command(BaseCommand):
    help = 'Adiciona dados iniciais de departamentos, categorias e subcategorias ao banco de dados'

    def handle(self, *args, **kwargs):
        for dept_name, categories in initial_data.items():
            dept, created = Departamento.objects.get_or_create(nome=dept_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Departamento criado: {dept_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Departamento já existe: {dept_name}'))
            
            for cat_name, subcategories in categories.items():
                cat, created = Category.objects.get_or_create(name=cat_name, department=dept)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Categoria criada: {cat_name} no departamento {dept_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Categoria já existe: {cat_name} no departamento {dept_name}'))
                
                for subcat_name in subcategories:
                    subcat, created = Subcategory.objects.get_or_create(name=subcat_name, category=cat)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Subcategoria criada: {subcat_name} na categoria {cat_name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Subcategoria já existe: {subcat_name} na categoria {cat_name}'))