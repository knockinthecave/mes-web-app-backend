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

from .models import ExternalWarhousing, BOM, ImportInspection, AssemblyInstruction, AssemblyCompleted, ExternalMember, ExternalMemberToken, ExternalInventory
from .serializers import ExternalWarhousingSerializer, BOMSerializer, ImportInspectionSerializer, AssemblyInstructionSerializer, AssemblyCompletedSerializer, ExternalInventorySerializer
from .filters import AssemblyInstructionFilter

from django.db.models import Q # For OR query
from django.db.models import Sum # For Sum query


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ExternalMember

@api_view(['POST'])
def login_view(request):
    user_id = request.data.get("user_id")
    password = request.data.get("password")
    
    try:
        user = ExternalMember.objects.get(user_id=user_id)
        
        if user.password == password:
            
             # Generate or retrieve token for the user
            token, created = ExternalMemberToken.objects.get_or_create(user=user)
                       
            return Response({
                "message": "Successful login!", 
                "user_id": user_id,
                "username": user.username,
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            raise ExternalMember.DoesNotExist
    except ExternalMember.DoesNotExist:
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# External Inventory API
class ExternalInventoryPagination(PageNumberPagination):
    page_size = 8
    page_query_param = 'page'
    max_page_size = 10000000000

class ExternalInventoryViewSet(viewsets.ModelViewSet):
    queryset = ExternalInventory.objects.all().order_by('inputDateTime')
    serializer_class = ExternalInventorySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('partNumber', 'lotNo', 'state', 'stock', 'inputDateTime', 'user_id', 'date_of_receipt', 'state')
    pagination_class = ExternalInventoryPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        page_size = self.request.query_params.get('page_size')

        if page_size:
            self.pagination_class.page_size = page_size

        return queryset
    
    
    @action(detail=True, methods=['PUT'], url_path='update-state')
    def update_state(self, request, *args, **kwargs):
        instance = self.get_object()  # 현재 id에 해당하는 인스턴스 가져오기
        serializer = ExternalInventorySerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['DELETE'], url_path='receive-cancel')
    def receive_cancel(self, request, *args, **kwargs):
        part_number = request.query_params.get('partNumber')
        quantity = request.query_params.get('quantity')
        lot_no = request.query_params.get('lotNo')
        user_id = request.query_params.get('user_id')
        
        if not all([part_number, quantity, lot_no, user_id]):
            return Response({"message": "All parameters are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find receipts and delete them
        self.queryset.filter(
            partNumber=part_number,
            quantity=quantity,
            lotNo=lot_no,
            user_id=user_id
        ).delete()
        
        return Response({'detail': 'Receipts deleted successfully.'}, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['GET'], url_path='stock-summary')
    def stock_summary(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id', None)
        
        # Start with all records, but if a user_id is provided, filter by it
        queryset = self.queryset
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        
        stock_summary = queryset.values('partNumber').annotate(total_stock=Sum('stock')).order_by('partNumber')
        
        return Response(stock_summary, status=status.HTTP_200_OK)


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
    filterset_fields = ('warehousingDate', 'barcode', 'partNumber', 'quantity', 'lotNo', 'user_id')
    pagination_class = WareHousePagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        states = self.request.query_params.getlist('state')
        print(states)

        # Q 객체를 사용하여 OR 조건을 적용합니다.
        if states:
            q_objects = Q()  # 빈 Q 객체를 생성합니다.
            for state in states:
                q_objects |= Q(state=state)  # 각 state에 대해 OR 조건을 추가합니다.

            queryset = queryset.filter(q_objects)
        return queryset
        

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
        user_id = request.query_params.get('user_id')
    
        # Start with a query that fetches all objects
        query = ExternalWarhousing.objects.all()

        # Apply filters if the parameters are provided
        if warehousing_date:
            query = query.filter(warehousingDate=warehousing_date)
        if user_id:
            query = query.filter(user_id=user_id)

        # Order by inputDateTime
        recent_items = query.order_by('-inputDateTime')

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
    
    @action(detail=False, methods=['DELETE'], url_path='receive-cancel')
    def receive_cancel(self, request, *args, **kwargs):
        part_number = request.query_params.get('partNumber')
        quantity = request.query_params.get('quantity')
        lot_no = request.query_params.get('lotNo')
        user_id = request.query_params.get('user_id')
        
        if not all([part_number, quantity, lot_no, user_id]):
            return Response({"message": "All parameters are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find receipts and delete them
        self.queryset.filter(
            partNumber=part_number,
            quantity=quantity,
            lotNo=lot_no,
            user_id=user_id
        ).delete()
        
        return Response({'detail': 'Receipts deleted successfully.'}, status=status.HTTP_200_OK)


# BOM API 
class BOMPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 10000000000
    
    
    
class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all().order_by('id')
    serializer_class = BOMSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('partNumber', 'part1', 'part2', 'part3', 'part4', 'part5', 'part6') # you had this, which is just for direct matches
    pagination_class = None # Pagination Before
    
    def get_queryset(self):
        queryset = super().get_queryset()
        parts_numbers = self.request.query_params.getlist('partsNumber')

        if parts_numbers:
            # 모든 parts_number에 대해 정확히 일치하는 BOM 객체를 필터링합니다.
            for number in parts_numbers:
                queryset = queryset.filter(
                    Q(partNumber=number) | 
                    Q(part1=number) |                     
                    Q(part2=number) |                    
                    Q(part3=number) |                   
                    Q(part4=number) |                  
                    Q(part5=number) |                    
                    Q(part6=number) 
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


# Assembly Instruction API
class AssemblyInstructionPagination(PageNumberPagination):
    page_size = 1000
    page_query_param = 'page'
    max_page_size = 10000000000


class AssemblyInstructionProductsPagination(PageNumberPagination):
    page_size = 3    

class AssemblyInstructionViewSet(viewsets.ModelViewSet):
    queryset = AssemblyInstruction.objects.all().order_by('id')  # 기본 쿼리셋으로 변경
    serializer_class = AssemblyInstructionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssemblyInstructionFilter  # 이 부분을 추가합니다.
    pagination_class = AssemblyInstructionPagination

    def get_queryset(self):
        page_size = self.request.query_params.get('page_size')
        queryset = super().get_queryset()

        if page_size:
            self.pagination_class.page_size = page_size

        return queryset

    
    @action(detail=False, methods=['get'])
    def unique_product_nos(self, request):
        user_id = request.query_params.get('user_id', None)  # 요청에서 user_id 값을 가져옵니다.

        # 조립대기 상태를 필터링하고 user_id 값이 제공되면 해당 user_id도 필터링합니다.
        query = AssemblyInstruction.objects.filter(Q(state="조립대기"))
    
        if user_id:
            query = query.filter(user_id=user_id)  # user_id 값이 있으면 추가로 필터링합니다.

        unique_combinations = query.values('instruction_date', 'product_no', 'user_id').distinct()

        # unique_combinations에서 'product_no'와 'instruction_date'만 추출합니다.
        unique_product_nos = [{'product_no': item['product_no'], 'instruction_date': item['instruction_date']} for item in unique_combinations]

        return Response(unique_product_nos)


    
    @action(detail=True, methods=['PUT'], url_path='update-state')
    def update_state(self, request, *args, **kwargs):
        instance = self.get_object()  # 현재 id에 해당하는 인스턴스 가져오기
        serializer = AssemblyInstructionSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 
# Assembly Completed API   
class AssemblyCompletedPagination(PageNumberPagination):
    page_size = 1000
    page_query_param = 'page'
    max_page_size = 10000000000


class AssemblyCompletedProductsPagination(PageNumberPagination):
    page_size = 3    


class AssemblyCompletedViewSet(viewsets.ModelViewSet):
    queryset = AssemblyCompleted.objects.filter(state__in=["조립완료", "남은부품"]).order_by('id')
    serializer_class = AssemblyCompletedSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('state', 'partNumber', 'quantity', 'lotNo', 'user_id', 'receive_check', 'completed_date')
    pagination_class = AssemblyCompletedPagination # Pagination Before
    
    def get_queryset(self):
        queryset = super().get_queryset()
        page_size = self.request.query_params.get('page_size')

        if page_size:
            self.pagination_class.page_size = page_size

        return queryset
    
    @action(detail=True, methods=['PUT'], url_path='update-state')
    def update_state(self, request, *args, **kwargs):
        instance = self.get_object()  # 현재 id에 해당하는 인스턴스 가져오기
        serializer = AssemblyCompletedSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def unique_product_nos(self, request):
      user_id = request.query_params.get('user_id')
      
      # Filter by the state condition, user_id (if provided) and then get the distinct combinations of instruction_date, product_no, and user_id.
      query = AssemblyCompleted.objects.filter(Q(state="조립완료") | Q(state="남은부품"), receive_check="X")
      
      if user_id:
            query = query.filter(user_id=user_id)
            
      # Filter by the state condition and then get the distinct combinations of instruction_date, product_no, and user_id.
      unique_combinations = query.values('completed_date', 'product_no', 'user_id').distinct()

      # Extract only the 'product_no' and 'instruction_date' values from the unique_combinations.
      unique_product_nos = [{'product_no': item['product_no'], 'completed_date': item['completed_date']} for item in unique_combinations]
      # 페이지네이션 적용
      #paginator = AssemblyCompletedProductsPagination()
      #paginated_queryset = paginator.paginate_queryset(unique_product_nos, request, view=self)
      #if paginated_queryset is not None:
          #return paginator.get_paginated_response(paginated_queryset)

      return Response(unique_product_nos)
