from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ExternalWarhousing, BOM, ImportInspection, Assembly

class ExternalWarhousingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalWarhousing
        fields = [
            'id', 
            'state', 
            'partNumber', 
            'quantity', 
            'lotNo', 
            'warehousingDate', 
            'warehousingWorker', 
            'note', 
            'warehouse_location',
            'lastState',
            'barcode',
            'inputDateTime'
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

class AssemblySerializer(serializers.ModelSerializer):
    class Meta:
        model = Assembly
        fields = [
            'id',
            'state',
            'partNumber',
            'quantity',
            'lotNo',
            'assemblyDate',
            'assemblyPN',
            'remainingQuantity',
            'Assembly_No'
        ]
        read_only_fields = ['id',]
            