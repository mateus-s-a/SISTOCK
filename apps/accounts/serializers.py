from rest_framework import serializers
# from .models import CustomUser  # Futuramente, importar o modelo de usuário customizado

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # model = CustomUser  # Descomente quando o modelo customizado estiver disponível
        fields = ('id', 'username', 'email', 'role')  # Adicione outros campos conforme necessário
