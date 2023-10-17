from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ExternalWarhousing, BOM, ImportInspection, AssemblyInstruction, AssemblyCompleted, ExternalMember

class ExternalMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalMember
        fields = [
            'id',
            'user_id',
            'password',
            'username',
            'warehouse'
        ]
        read_only_fields = ['id',]
    
class ExternalWarhousingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalWarhousing
        fields = [
            'id', 
            'state', 
            'partNumber', 
            'quantity', 
            'remains',
            'lotNo', 
            'warehousingDate', 
            'warehousingWorker', 
            'note', 
            'warehouse_location',
            'lastState',
            'barcode',
            'inputDateTime',
            'user_id'
        ]
        read_only_fields = ['id',]

class BOMSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOM
        fields = [
            'id',
            'no',
            'partNumber',
            'productName',
            'part1',
            'USAGE1',
            'part2',
            'USAGE2',
            'part3',
            'USAGE3',
            'part4',
            'USAGE4',
            'part5',
            'USAGE5',
            'part6',
            'USAGE6'
        ]
        read_only_fields = ['id',]
        
class ImportInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportInspection
        fields = [
            'id',
            'state',
            'partNumber',
            'quantity',
            'quantity2',
            'lotNo',
            'importInspectionDate',
            'importInspectionWorker',
            'Location'
        ]
        read_only_fields = ['id',]

class AssemblyInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssemblyInstruction
        fields = [
            'id',
            'state',
            'partNumber',
            'quantity',
            'lotNo',
            'instruction_date',
            'instructed_quantity',
            'remains',
            'product_no',
            'user_id',
            'total_instructed'
        ]
        read_only_fields = ['id',]



class AssemblyCompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssemblyCompleted
        fields = [
            'id',
            'state',
            'partNumber',
            'quantity',
            'lotNo',
            'completed_date',
            'instructed_quantity',
            'remains',
            'product_no',
            'user_id',
            'receive_check',
            'total_instructed'
        ]
        read_only_fields = ['id',]            