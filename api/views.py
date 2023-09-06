from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate

# Imports related to Warehouse
from django_filters import rest_framework as filters
from rest_framework import viewsets
from .models import ExternalWarhousing
from .serializers import ExternalWarhousingSerializer
from django.http import Http404
from rest_framework.decorators import action

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
    queryset = ExternalWarhousing.objects.all().order_by('inputDateTime')
    serializer_class = ExternalWarhousingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('warehousingDate',)
    
    @action(detail=False, methods=['GET'], url_path='check-barcode')
    def check_barcode(self, request, *args, **kwargs):
        barcode = request.query_params.get('barcode')
        
        if barcode:
            item_exists = ExternalWarhousing.objects.filter(barcode=barcode).exists()
            
            if item_exists:
                return Response({"message": "Item with this barcode already exists."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Item does not exist."}, status=status.HTTP_204_NO_CONTENT)
        
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['GET'], url_path='recent-warehousing')
    def recent_warehousing(self, request, *args, **kwargs):
        # Assuming you want a default of 10 recent items.
        # You can adjust this number or use pagination for larger datasets.
        recent_items = ExternalWarhousing.objects.all().order_by('-inputDateTime')
        
        # Serializing the data
        serializer = ExternalWarhousingSerializer(recent_items, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

