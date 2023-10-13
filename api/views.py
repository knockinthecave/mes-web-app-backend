from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django_filters import rest_framework as filters
from django.http import Http404
from django.http import JsonResponse

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token

from .models import ExternalWarhousing, BOM, ImportInspection, AssemblyInstruction
from .serializers import ExternalWarhousingSerializer, BOMSerializer, ImportInspectionSerializer, AssemblyInstructionSerializer

from django.db.models import Q # For OR query


# Login API
@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate a token or set a session and return it
            return Response({"message": "Successful login!", 
                             "username": username}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)



# Warehouse API    
class WareHousePagination(PageNumberPagination):
    page_size = 8
    page_query_param = 'page'
    max_page_size = 10000000000
    


class RecentWarehousingPagination(PageNumberPagination):
    page_size = 5
    page_query_param = 'page'
    max_page_size = 10000000000
    
    
    
class ExternalWarhousingViewSet(viewsets.ModelViewSet):
    queryset = ExternalWarhousing.objects.all().order_by('inputDateTime')
    serializer_class = ExternalWarhousingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('warehousingDate', 'barcode', 'state', 'partNumber', 'quantity', 'lotNo', 'user_id')
    pagination_class = WareHousePagination
    
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
            recent_items = ExternalWarhousing.objects.all().order_by('-inputDateTime')

        # Apply pagination
        paginator = RecentWarehousingPagination()
        paginated_items = paginator.paginate_queryset(recent_items, request)
        
        # Serializing the paginated data
        serializer = ExternalWarhousingSerializer(paginated_items, many=True)
    
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['PUT'], url_path='update-state')
    def update_state(self, request, *args, **kwargs):
        instance = self.get_object()  # 현재 id에 해당하는 인스턴스 가져오기
        serializer = ExternalWarhousingSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# BOM API 
class BOMPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 10000000000
    
    
    
class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all().order_by('id')
    serializer_class = BOMSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('partNumber',) # you had this, which is just for direct matches
    pagination_class = None # Pagination Before
    
    def get_queryset(self):
        queryset = super().get_queryset()
        parts_number = self.request.query_params.get('partsNumber', None)

        if parts_number:
            queryset = queryset.filter(
                Q(partNumber=parts_number) | 
                Q(part1=parts_number) |
                Q(USAGE1=parts_number) |
                Q(part2=parts_number) |
                Q(USAGE2=parts_number) |    
                Q(part3=parts_number) |
                Q(USAGE3=parts_number) |
                Q(part4=parts_number) |
                Q(USAGE4=parts_number) |
                Q(part5=parts_number) |
                Q(USAGE5=parts_number) |
                Q(part6=parts_number) |
                Q(USAGE6=parts_number)
            )
        return queryset

# Import Inspection API
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

class AssemblyInstructionPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 10000000000


class AssemblyInstructionViewSet(viewsets.ModelViewSet):
    queryset = AssemblyInstruction.objects.filter(state__in=["조립대기"]).order_by('id')
    serializer_class = AssemblyInstructionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('state', 'partNumber', 'quantity', 'lotNo', 'user_id')
    pagination_class = AssemblyInstructionPagination # Pagination Before
    
    def get_queryset(self):
        queryset = super().get_queryset()
        page_size = self.request.query_params.get('page_size')

        if page_size:
            self.pagination_class.page_size = page_size

        return queryset
    
    @action(detail=False, methods=['get'])
    def unique_product_nos(self, request):
    # This queryset will return distinct combinations of instruction_date, product_no, and user_id.
        unique_combinations = AssemblyInstruction.objects.values('instruction_date', 'product_no', 'user_id').distinct()

    # If you still want to only return the unique product numbers but with the above distinction,
    # you can extract only the 'product_no' values from the unique_combinations.
        unique_product_nos = [{'product_no': item['product_no'], 'instruction_date': item['instruction_date']} for item in unique_combinations]
    
        return Response(unique_product_nos)