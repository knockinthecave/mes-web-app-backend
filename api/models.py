from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from rest_framework.authtoken.models import Token

import pytz
     
# 로그인 
class ExternalMemberManager(BaseUserManager):
    def create_user(self, user_id, password=None, **extra_fields):
        if not user_id:
            raise ValueError('The User ID must be set')
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(user_id, password, **extra_fields)

class ExternalMember(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)  # 해시된 비밀번호
    username = models.CharField(max_length=30)
    warehouse = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['username']

    objects = ExternalMemberManager()

    class Meta:
        db_table = 'external_member'
        managed = False

# 창고 
class ExternalInventory(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=100)
    partNumber = models.CharField(max_length=100)
    quantity = models.IntegerField()
    lotNo = models.CharField(max_length=100)
    stock = models.IntegerField()
    inputDateTime = models.DateTimeField()
    user_id = models.CharField(max_length=100)
    date_of_receipt = models.DateField()
     
    class Meta:
        managed = False
        db_table = 'external_inventory'
 
# 입고 목록 조회 (Warehousing list inquiry)
class ExternalWarhousing(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=30)
    partNumber = models.CharField(max_length=30)
    quantity = models.IntegerField()
    remains = models.IntegerField()
    lotNo = models.CharField(max_length=30)
    warehousingDate = models.DateField()
    warehousingWorker = models.CharField(max_length=30)
    note = models.CharField(max_length=100)
    warehouse_location = models.CharField(max_length=100)
    lastState = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)
    inputDateTime = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=100)
    
    class Meta:
        managed = False  # Remove this if you want Django to manage this table
        db_table = 'external_warehousing'



class BOM(models.Model):
    uid = models.AutoField(primary_key=True)
    no = models.CharField(max_length=11)
    partNumber = models.CharField(max_length=30)
    productName = models.CharField(max_length=400)
    part1 = models.CharField(max_length=30)
    USAGE1 = models.CharField(max_length=11)
    part2 = models.CharField(max_length=30)
    USAGE2 = models.CharField(max_length=11)
    part3 = models.CharField(max_length=30)
    USAGE3 = models.CharField(max_length=11)
    part4 = models.CharField(max_length=30)
    USAGE4 = models.CharField(max_length=11)
    part5 = models.CharField(max_length=30)
    USAGE5 = models.CharField(max_length=11)
    part6 = models.CharField(max_length=30)
    USAGE6 = models.CharField(max_length=11)
    
    class Meta:
        managed = False  # Remove this if you want Django to manage this table
        db_table = 'BOM'
 
 
        
class ImportInspection(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=30)
    partNumber = models.CharField(max_length=30)
    quantity = models.IntegerField()
    quantity2 = models.CharField(max_length=10)
    lotNo = models.CharField(max_length=30)
    importInspectionDate = models.DateTimeField()
    importInspectionWorker = models.CharField(max_length=100)
    Location = models.CharField(max_length=50)
      
    class Meta:
        managed = False  # Remove this if you want Django to manage this table
        db_table = 'importInspection'



class AssemblyInstruction(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=30)
    partNumber = models.CharField(max_length=30)
    quantity = models.IntegerField()
    lotNo = models.CharField(max_length=30)
    instruction_date = models.DateTimeField()
    instructed_quantity = models.IntegerField()
    remains = models.IntegerField()
    product_no = models.CharField(max_length=30)
    user_id = models.CharField(max_length=100)
    total_instructed = models.IntegerField()
    work_num = models.CharField(max_length=100)
    
    class Meta:
        managed = False  # Remove this if you want Django to manage this table
        db_table = 'assemblyInstruction'
        

class AssemblyCompleted(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=30)
    partNumber = models.CharField(max_length=30)
    quantity = models.IntegerField()
    lotNo = models.CharField(max_length=30)
    completed_date = models.DateTimeField()
    instructed_quantity = models.IntegerField()
    remains = models.IntegerField()
    product_no = models.CharField(max_length=30)
    user_id = models.CharField(max_length=100)
    receive_check = models.CharField(max_length=10)
    total_instructed = models.IntegerField()
    work_num = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        db_table = 'assemblyCompleted'
        

class WebLogs(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    log = models.CharField(max_length=100)
    log_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = 'web_logs'


       
# 24.01.17 이성범 수정
# warehousing 모델링
class SwintechWarehousing(models.Model):
    uid = models.AutoField(primary_key=True)
    state = models.CharField(max_length=30)
    partNumber = models.CharField(max_length=30)
    quantity = models.IntegerField()
    lotNo = models.CharField(max_length=30)
    warehousingDate = models.DateTimeField()
    warehousingWorker = models.CharField(max_length=30)
    improvedItem = models.CharField(max_length=20)
    note = models.CharField(max_length=100)
    lastState = models.CharField(max_length=20)
    
    class Meta:
        managed = False
        db_table = 'warehousing'
        
        

# 24.01.25 이성범 수정
# sub_log 모델링
class SubLog(models.Model):
    id = models.AutoField(primary_key=True)
    before_state = models.CharField(max_length=100)
    after_state = models.CharField(max_length=100)
    log_date = models.DateTimeField(auto_now_add=True)
    partNumber = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    lotNo = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    
    # DB에서 log_date가 MES와 혼동이 오지 않도록 timezone을 한국으로 설정
    def save(self, *args, **kwargs):
        if not self.id:
            self.log_date = timezone.now().astimezone(pytz.timezone('Asia/Seoul'))
        super().save(*args, **kwargs)
        
    class Meta:
        managed = False
        db_table = 'sub_log'