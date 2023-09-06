from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ExternalWarhousing

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
