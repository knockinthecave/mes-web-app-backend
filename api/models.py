from django.db import models
from django.utils import timezone
from datetime import timedelta
from rest_framework.authtoken.models import Token
     
# 로그인 
class ExternalMember(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    warehouse = models.CharField(max_length=30)
    
    class Meta:
        managed = False
        db_table = 'external_member'


class ExternalMemberToken(models.Model):
    key = models.CharField("Key", max_length=40, primary_key=True)
    user = models.OneToOneField(
        ExternalMember,
        related_name='auth_token',
        on_delete=models.CASCADE,
        verbose_name="External Member"
    )
    created = models.DateTimeField("Created", auto_now_add=True)
    expires_at = models.DateTimeField("Expires At", null=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expires_at = timezone.now() + timedelta(hours=24)  # 예시로 24시간 후 만료
        return super().save(*args, **kwargs)

    def generate_key(self):
        return Token.generate_key()

    class Meta:
        unique_together = (('user', 'key'),)


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
    id = models.AutoField(primary_key=True)
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
        db_table = 'BOM_web'
 
 
        
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