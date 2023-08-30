from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate

# BOM 조회 Import
from django_filters import rest_framework as filters
from rest_framework import viewsets
from .models import ExternalWarhousing  # 모델 위치에 따라 import를 조정해주세요.
from .serializers import ExternalWarhousingSerializer  # Serializer를 import 해야 합니다.

# Login API
@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate a token or set a session and return it
            return Response({"message": "Successful login!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Warehouse API
class ExternalWarhousingViewSet(viewsets.ModelViewSet):
    queryset = ExternalWarhousing.objects.all().order_by('-warehousingDate')
    serializer_class = ExternalWarhousingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('warehousingDate',)
