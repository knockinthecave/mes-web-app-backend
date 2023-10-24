# filters.py 파일에 추가
import django_filters
from .models import AssemblyInstruction  # 필요한 경우 모델 import 경로를 확인하여 수정해주세요.

class AssemblyInstructionFilter(django_filters.FilterSet):
    state = django_filters.MultipleChoiceFilter(choices=[("조립대기", "조립대기"), ("남은부품", "남은부품")], conjoined=False)

    class Meta:
        model = AssemblyInstruction
        fields = ['state', 'partNumber', 'quantity', 'lotNo', 'user_id', 'product_no', 'instruction_date']
