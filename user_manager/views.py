from distutils.log import error
import json
from django.conf import settings
# Django REST Framework
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from user_manager.serializers import *
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated  # <-- Here is the code that you need to add
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.contrib.auth import login
from drf_api_logger import API_LOGGER_SIGNAL
from drf_api_logger.models import APILogsModel
from user_manager.models import *
from django.contrib.sessions.models import Session


class UserViewSet(viewsets.GenericViewSet):
    """
    API para registro de usuarios y autenticación.
    """

    queryset = User.objects.filter(is_active=True)
    serializer_class = UserModelSerializer
    # Detail define si es una petición de detalle o no, en methods añadimos el método permitido, en nuestro caso solo vamos a permitir post
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Autenticación de usuarios.
        parametros:
            username: nombre de usuario
            password: contraseña
        devuelve:
            token: token de autenticación
        """
        
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'jwt': token
        }
        request.session['user'] = data
        login(request, user)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """
        Registro de usuarios.
        Parámetros de registro se debe enviar un JSON con los siguientes campos:
            - username
            - password
            - email
            - first_name
            - last_name    
        Devuelve:
            - username: usuario registrado
        """
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
        }
        return Response(data, status=status.HTTP_201_CREATED)

def diff_days(request):
    """
    Diferrencia de dias entre dos fechas
    parametros:
        - fecha_inicio: fecha de inicio
        - fecha_fin: fecha de fin
    devuelve:
        - diferencia de dias
    """
    if request.method == 'GET':
        error = 'Debes enviar los parametros de fecha_inicio y fecha_fin'
        try:
            data = JSONParser().parse(request)
            serializer = DiffDateSerializer(data=data)
        except Exception as e:
            return JsonResponse({'error': error}, status=400)

        if serializer.is_valid():
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%d/%m/%Y')
            fecha_fin = datetime.strptime(data['fecha_fin'], '%d/%m/%Y')

            dias_diff = (fecha_fin - fecha_inicio).days
            data = {
                'diferencia_dias': dias_diff
            }
            return JsonResponse(data, status=201)
        return JsonResponse(serializer.errors, status=400)

def operation_logs(request):
    """
    Listado de logs de operaciones
    requisito:
        - el usuario debe estar logeado
    parametros:
        None
    devuelve:
        - logs de operaciones del usuario
    """   
    user = request.user
    error = 'Debes iniciar session para ver tus registos' 
    if user.is_authenticated:
        user_id = user.id
        query = APILogsModel.objects.filter(client_ip_address=str(user_id))
        data = {}
        if query.count() > 0:
            for i in query:
                data[i.id] = {
                    'api': i.api,
                    'metodo': i.method,
                    'status_code': i.status_code,
                    'fecha': datetime.strftime(i.added_on, '%d/%m/%Y %H:%M:%S'),
                }
            return JsonResponse(data, status=201)
    return JsonResponse({'error': error}, status=400)

def listener_one(**kwargs):
    """
        Escucha los eventos de la API de registro de logs de operaciones
    """
    try:    
        api_login = "http://localhost:8000/users/login/"
        json_format = json.dumps(kwargs, indent=4, sort_keys=True, default=str)
        json_data = json.loads(json_format)
        api = json_data['api']
        status_code = json_data['status_code']
        if api==api_login and status_code == 201:
            user = json_data['response']['user']['username']
            user_id = User.objects.get(username=user).id
        else:
            session_id = json_data['headers']['COOKIE'].split(';')[1].split('=')[1]
            session_key = session_id
            session = Session.objects.get(session_key=session_key) 
            user_id = session.get_decoded().get('_auth_user_id')
        consulta = APILogsModel.objects.latest('id')
        APILogsModel.objects.filter(id=consulta.id).update(client_ip_address=user_id)
    except Exception as e:
        pass
    
API_LOGGER_SIGNAL.listen += listener_one