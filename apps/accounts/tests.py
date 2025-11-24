from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from apps.accounts.forms import UserRegistrationForm


class UserRegistrationFormTest(TestCase):
    """Testes para o formulário de registro de usuário"""

    def test_form_valido_cria_usuario_com_role(self):
        """Testa se formulário válido cria usuário corretamente"""
        data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'senha123456',
            'password2': 'senha123456',
            'role': 'STAFF'
        }

        form = UserRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.profile.role, 'STAFF')
        self.assertTrue(user.groups.filter(name='Staff').exists())

    def test_senhas_diferentes_invalida_form(self):
        """Testa se senhas diferentes invalidam o formulário"""
        data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'senha123456',
            'password2': 'senha654321',  # Diferente
            'role': 'STAFF'
        }

        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_senha_curta_invalida_form(self):
        """Testa se senha com menos de 8 caracteres invalida"""
        data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'curta',  # Menos de 8 caracteres
            'password2': 'curta',
            'role': 'STAFF'
        }

        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
