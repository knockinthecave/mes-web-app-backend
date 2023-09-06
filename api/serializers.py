from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ExternalWarhousing, BOM, ImportInspection

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
            'part2',
            'part3',
            'part4',
            'part5',
            'part6'
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