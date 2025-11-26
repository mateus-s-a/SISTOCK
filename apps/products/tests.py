from django.test import TestCase, Client
from django.urls import reverse
from apps.products.models import Product, Category
import json

# Create your tests here.


class ProductAutocompleteAPITest(TestCase):
    """Testes para API de autocomplete de produtos"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('products:product_autocomplete')

        # Cria categoria de teste
        self.category = Category.objects.create(
            name='Eletrônicos',
            description='Categoria teste'
        )

        # Cria produtos de teste
        Product.objects.create(
            name='Mouse Gamer',
            sku='MOUSE-001',
            description='Mouse RGB',
            price=150.00,
            stock_quantity=50,
            minimum_stock=10,
            category=self.category
        )

        Product.objects.create(
            name='Teclado Mecânico',
            sku='TECL-001',
            description='Teclado RGB',
            price=300.00,
            stock_quantity=30,
            minimum_stock=5,
            category=self.category
        )
    

    def test_busca_por_nome(self):
        """Testa busca por nome de produto"""
        response = self.client.get(self.url, {'q': 'mouse'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['name'], 'Mouse Gamer')
    

    def test_busca_por_sku(self):
        """Teste busca por SKU"""
        response = self.client.get(self.url, {'q': 'TECL'})

        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['sku'], 'TECL-001')
    

    def test_query_muito_curta_retorna_vazio(self):
        """Teste que query com menos de 2 caracteres retorna vazio"""
        response = self.client.get(self.url, {'q': 'a'})

        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 0)
    

    def test_busca_case_insensitive(self):
        """Testa que busca é case-insensitive"""
        response = self.client.get(self.url, {'q': 'MOUSE'})
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)

        response = self.client.get(self.url, {'q': 'mouse'})
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
    

    def test_limite_de_resultados(self):
        """Testa que API limita resultados a 10"""
        
        # Cria 15 produtos
        for i in range(15):
            Product.objects.create(
                name=f'Produto Teste {i}',
                sku=f'TEST-{i:03d}',
                price=100.00,
                stock_quantity=10,
                minimum_stock=5,
                category=self.category
            )
        
        response = self.client.get(self.url, {'q': 'teste'})
        data = json.loads(response.content)

        # Deve retornar no máximo 10
        self.assertLessEqual(len(data['results']), 10)
    

    def test_estrutura_do_resultado(self):
        """Testa se resultado tem todos os campos necessários"""
        response = self.client.get(self.url, {'q': 'mouse'})
        data = json.loads(response.content)

        result = data['results'][0]
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertIn('sku', result)
        self.assertIn('category', result)
        self.assertIn('stock', result)
        self.assertIn('price', result)
        self.assertIn('url', result)
