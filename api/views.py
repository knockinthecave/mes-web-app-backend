from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_filters import rest_framework as filters
from django.http import Http404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import ExternalWarhousing, BOM, ImportInspection
from .serializers import ExternalWarhousingSerializer, BOMSerializer, ImportInspectionSerializer


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
    pagination_class = None
    
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
        warehousing_date = request.query_params.get('warehousingDate')
    
        if warehousing_date:
            recent_items = ExternalWarhousing.objects.filter(warehousingDate=warehousing_date).order_by('-inputDateTime')
        else:
        # This could be today's date or whatever default behavior you'd like.
            recent_items = ExternalWarhousing.objects.all().order_by('-inputDateTime')

        # Serializing the data
        serializer = ExternalWarhousingSerializer(recent_items, many=True)
    
        return Response(serializer.data, status=status.HTTP_200_OK)


# BOM API 
class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all().order_by('id')
    serializer_class = BOMSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('partNumber',)


  
class ImportInspectionPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 10000000000


    
class ImportInspectionViewSet(viewsets.ModelViewSet):
    queryset = ImportInspection.objects.filter(state__in=["조립 대기", "남은 부품"]).order_by('id')
    serializer_class = ImportInspectionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('state',)
    pagination_class = ImportInspectionPagination # Pagination Before
    
    def get_queryset(self):
        queryset = super().get_queryset()
        page_size = self.request.query_params.get('page_size')

        if page_size:
            self.pagination_class.page_size = page_size

        return queryset
