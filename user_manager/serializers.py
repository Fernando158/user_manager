
"""Users serializers."""
from django.contrib.auth.models import User
# Django
from django.contrib.auth import authenticate, password_validation

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from datetime import datetime

class UserModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = (
            'username',
        )

class UserLoginSerializer(serializers.Serializer):

    # Campos que vamos a requerir
    username = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=64)
    # Primero validamos los datos
    def validate(self, data):
        # authenticate recibe las credenciales, si son válidas devuelve el objeto del usuario
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Las credenciales no son válidas')

        # Guardamos el usuario en el contexto para posteriormente en create recuperar el token
        self.context['user'] = user
        return data

    def create(self, data):
        """Generar o recuperar token."""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key

class UserSignUpSerializer(serializers.Serializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    first_name = serializers.CharField(min_length=2, max_length=50)
    last_name = serializers.CharField(min_length=2, max_length=100)

    def validate(self, data):
        passwd = data['password']
        passwd_conf = data['password_confirmation']

        if passwd != passwd_conf:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        password_validation.validate_password(passwd)
        
        return data

    def create(self, data):
        data.pop('password_confirmation')
        user = User.objects.create_user(**data)
        return user


class DiffDateSerializer(serializers.Serializer):
    fecha_inicio = serializers.DateField(format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])
    fecha_fin = serializers.DateField(format="%d/%m/%Y", input_formats=['%d/%m/%Y', 'iso-8601'])

    def validate(self, data):
        fecha_ini = data['fecha_inicio']
        fecha_fin = data['fecha_fin']

        if fecha_ini > fecha_fin:
            raise serializers.ValidationError({'error': 'La fecha de inicio no puede ser mayor a la fecha de fin.'})
        
        
        dias_diff = (fecha_fin - fecha_ini).days
        
        return dias_diff