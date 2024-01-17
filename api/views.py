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

from .models import ExternalWarhousing, BOM, ImportInspection, AssemblyInstruction, AssemblyCompleted, ExternalMember, ExternalMemberToken, ExternalInventory, WebLogs, SwintechWarehousing
from .serializers import ExternalWarhousingSerializer, BOMSerializer, ImportInspectionSerializer, AssemblyInstructionSerializer, AssemblyCompletedSerializer, ExternalInventorySerializer, WebLogsSerializer, SwintechWarehousingSerializer, ExternalMemberSerializer
from .filters import AssemblyInstructionFilter

from django.db.models import Q # For OR query
from django.db.models import Sum # For Sum query
from django.db.models import Count # For Count query
from django.db.models import F # For F query


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
# 23.11.15 이성범 수정 (branch : feature/warehouse)
# page_size 수정 => 창고조회 페이지에서 조회할 페이지 사이즈 8개가 아닌 10개로 수정
class ExternalInventoryPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 10000000000

# 23.11.16 이성범 수정.
# get_queryset에서 filter를 state 와 page_size로 창고조회 페이지에서 남은부품, 입고 상태만 보여줄 수 있도록 함. (= 조립완료 상태일 때는 현재수량 0)
class ExternalInventoryViewSet(viewsets.ModelViewSet):
    queryset = ExternalInventory.objects.all().order_by('inputDateTime')
    serializer_class = ExternalInventorySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('partNumber', 'lotNo', 'stock', 'inputDateTime', 'user_id', 'date_of_receipt')
    pagination_class = ExternalInventoryPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        states = self.request.query_params.getlist('state')
        page_size = self.request.query_params.get('page_size')

        if states:
            queryset = queryset.filter(state__in=states)

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
    
    # 23.11.23 이성범 수정
    # 작업지시 페이지에서 바코드 제출 시 state=입고 일 경우에 대한 처리
    # 바코드에 있는 제품번호가 창고에 남은부품이 존재하는지 COUNT를 Response로 제공하는 API
    @action(detail=False, methods=['GET'], url_path='remain-check')
    def remain_check(self, request, *args, **kwargs):
        part_number = request.query_params.get('partNumber')
        user_id = request.query_params.get('user_id')
        if not part_number:
            return Response({'error': 'Part number is required'}, status=400)

        # Query to count remaining parts for the given part number
        remaining_count = ExternalInventory.objects.filter(partNumber=part_number, user_id=user_id, state='남은부품').count()

        return Response({'partNumber': part_number, 'remainingCount': remaining_count})
        
        


# Warehouse API    
class WareHousePagination(PageNumberPagination):
    page_size = 8
    page_query_param = 'page'
    max_page_size = 10000000000
    


class RecentWarehousingPagination(PageNumberPagination):
    page_size = 5
    page_query_param = 'page'
    max_page_size = 10000000000
    

# 23.11.09 17:29 수정
# API Endpoint에 state를 여러개 적었을때, 계속해서 state를 한개로만 인식하여 filter가 충돌되는 문제가 발생.
# filterset_fileds에서 state를 제거하고 get_queryset이라는 사용자 정의 필터링을 통해 해결. 
class ExternalWarhousingViewSet(viewsets.ModelViewSet):
    queryset = ExternalWarhousing.objects.all().order_by('inputDateTime')
    serializer_class = ExternalWarhousingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('warehousingDate', 'barcode', 'partNumber', 'quantity', 'lotNo', 'user_id')
    pagination_class = WareHousePagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        states = self.request.query_params.getlist('state')
        if states:
            queryset = queryset.filter(state__in=states)
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
    queryset = BOM.objects.all().order_by('uid')
    serializer_class = BOMSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('uid', 'partNumber', 'part1', 'part2', 'part3', 'part4', 'part5', 'part6') # you had this, which is just for direct matches
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
    
    # 24.01.10 이성범 수정
    # 일부조립완료 페이지에서 바코드 제출 시 부품이 하우징인지 아닌지 체크하는 API Endpoint 추가
    @action(detail=False, methods=['GET'], url_path='check-is-housing-part')
    def check_is_housing_part(self, request):
        part_number = request.query_params.get('partNumber')
        
        if not part_number:
            return Response({'error': 'Part number is required'}, status=400)
        
        # Check if the part_number is in the BOM table
        isHousingPart = BOM.objects.filter(part1=part_number).exists()
        
        return Response({'isHousingPart': isHousingPart})
    

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
    queryset = AssemblyInstruction.objects.filter(state__in=["조립대기", "남은부품", "반조립"]).order_by('id')  # 기본 쿼리셋으로 변경
    serializer_class = AssemblyInstructionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssemblyInstructionFilter  # 이 부분을 추가합니다.
    pagination_class = AssemblyInstructionPagination

    def get_queryset(self):
        page_size = self.request.query_params.get('page_size')
        states = self.request.query_params.getlist('state')
        queryset = super().get_queryset()

        if page_size:
            self.pagination_class.page_size = page_size
            
        if states:
          queryset = queryset.filter(state__in=states)

        return queryset

    
    @action(detail=False, methods=['get'])
    def unique_product_nos(self, request):
        user_id = request.query_params.get('user_id', None)  # 요청에서 user_id 값을 가져옵니다.

        # 조립대기 상태를 필터링하고 user_id 값이 제공되면 해당 user_id도 필터링합니다.
        query = AssemblyInstruction.objects.filter(
            Q(state="조립대기") | Q(state="반조립")
        )
    
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
    
    
    # 23.12.27 이성범 수정
    # filter-work-num API 추가
    # 작업번호로 필터링을 한 후 하우징 부품번호를 param으로 받아 해당하는 부품을 제외시킨 후 Response
    # Front 단에서는 데이터를 받아와 렌더링만 하면됨.
    @action(detail=False, methods=['GET'], url_path='filter-work-num')
    def filter_by_work_num(self, request):
        work_num = request.query_params.get('work_num')
        part_number = request.query_params.get('partNumber')
        
        if not work_num:
            return Response({'error': 'Work number is required'}, status=400)
        
        query = AssemblyInstruction.objects.filter(work_num=work_num).exclude(partNumber=part_number)
        
        serializer = AssemblyInstructionSerializer(query, many=True)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['GET'], url_path='grouped-partial-assembly')
    def grouped_partial_assembly(self, request):
        # user_id 파라미터 추출
        user_id = request.query_params.get('user_id', None)
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)

        # '일부조립완료' 상태이며 해당 user_id를 가진 데이터 필터링
        partial_assembly_qs = AssemblyInstruction.objects.filter(user_id=user_id, state="일부조립완료")

        # 각 part_number에 대한 집계 데이터
        grouped_data = {}
        
        for item in partial_assembly_qs:
            part_number = item.partNumber
            
            # Initialize the part_number key if not already present
            if part_number not in grouped_data:
                grouped_data[part_number] = {
                    'product_no' : item.product_no,
                    'part_number': part_number,
                    'current_count' : 0,
                    'remaining_count' : 0, 
                    'work_num' : item.work_num
                }
            
            # Increment current_count for the part_number
            grouped_data[part_number]['current_count'] += 1
            
            # Calculate and add to remaining_count for the part_number
            remaining_count = AssemblyInstruction.objects.filter(user_id=user_id, work_num=item.work_num, partNumber=part_number, state="조립대기").count()
            grouped_data[part_number]['remaining_count'] = remaining_count
            
        # Convert the dictionary to a list for serialization
        serialized_data = list(grouped_data.values())
            
        return Response(serialized_data)

    
     
# Assembly Completed API   
class AssemblyCompletedPagination(PageNumberPagination):
    page_size = 1000
    page_query_param = 'page'
    max_page_size = 10000000000


class AssemblyCompletedProductsPagination(PageNumberPagination):
    page_size = 3    


class AssemblyCompletedViewSet(viewsets.ModelViewSet):
    queryset = AssemblyCompleted.objects.filter(state__in=["조립완료", "남은부품", "반조립완료"]).order_by('id')
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
      query = AssemblyCompleted.objects.filter(Q(state="조립완료") | Q(state="남은부품") | Q(state="반조립완료"), receive_check="X")
      
      if user_id:
            query = query.filter(user_id=user_id)
            
      # Filter by the state condition and then get the distinct combinations of instruction_date, product_no, and user_id.
      unique_combinations = query.values('work_num', 'product_no', 'user_id').distinct()

      # Extract only the 'product_no' and 'instruction_date' values from the unique_combinations.
      unique_product_nos = [{'product_no': item['product_no'], 'work_num': item['work_num']} for item in unique_combinations]
      # 페이지네이션 적용
      #paginator = AssemblyCompletedProductsPagination()
      #paginated_queryset = paginator.paginate_queryset(unique_product_nos, request, view=self)
      #if paginated_queryset is not None:
          #return paginator.get_paginated_response(paginated_queryset)

      return Response(unique_product_nos)
    
    @action(detail=False, methods=['GET'], url_path='grouped-partial-completed')
    def grouped_partial_completed(self, request):
        
        user_id = request.query_params.get('user_id')
        
        queryset = AssemblyCompleted.objects.filter(state="일부조립완료", user_id=user_id)
        
        grouped_data = queryset.values('product_no').annotate(count=Count('id'))
        
        response_data = [{'product_no': item['product_no'], 'count': item['count']} for item in grouped_data]
        
        return Response(response_data)
    
    @action(detail=False, methods=['GET'], url_path='check-partial-completed-is-exist')
    def check_partial_completed_is_exist(self, request):
        partNumber = request.query_params.get('partNumber')
        quantity = request.query_params.get('quantity')
        lotNo = request.query_params.get('lotNo')
        user_id = request.query_params.get('user_id')
        
        if not all([partNumber, quantity, lotNo]):
            return Response({'error': 'Invalid Barcode. Please Check.'}, status=400)
        
        # Check if there is a record with the given product_no and user_id
        exists = AssemblyCompleted.objects.filter(state="일부조립완료", partNumber=partNumber, quantity=quantity, lotNo=lotNo, user_id=user_id).exists()
        
        return Response({'exists': exists})
    
    

class WebLogsViewSet(viewsets.ModelViewSet):
    queryset = WebLogs.objects.filter().order_by('id')
    serializer_class = WebLogsSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('id', 'user_id', 'log', 'log_date')
    
    @action(detail=False, methods=['POST'], url_path='upload-log')
    def upload_log(self, request):
        user_id = request.data.get('user_id')
        log = request.data.get('log')
        
        if not all([user_id, log]):
            return Response({'error': 'user_id and log are required'}, status=400)
        
        WebLogs.objects.create(user_id=user_id, log=log)
        
    

# 24.01.17 이성범 수정
# warehousing 모델링 (Swintech MES 연동)
class SwintechWarehousingViewSet(viewsets.ModelViewSet):
    queryset = SwintechWarehousing.objects.filter().order_by('uid')
    serializer_class = SwintechWarehousingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('uid', 'state', 'partNumber', 'quantity', 'lotNo', 'warehousingDate', 'warehousingWorker', 'improvedItem', 'note', 'lastState')
    
    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset