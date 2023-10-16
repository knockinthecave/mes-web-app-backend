from django.db import models
     

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
        #managed = False  # Remove this if you want Django to manage this table
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
    
    class Meta:
        managed = True  # Remove this if you want Django to manage this table
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
    
    class Meta:
        managed = True
        db_table = 'assemblyCompleted'