from django.urls import path, include
from rest_framework import routers
from . import views 
from rest_framework.authtoken.views import obtain_auth_token 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = routers.DefaultRouter()
router.register(r'inventory', views.ExternalInventoryViewSet)
router.register(r'warehouse', views.ExternalWarhousingViewSet)
router.register(r'bom', views.BOMViewSet)
router.register(r'importinspection', views.ImportInspectionViewSet)
router.register(r'assembly-instruction', views.AssemblyInstructionViewSet)
router.register(r'assembly-completed', views.AssemblyCompletedViewSet)
router.register(r'logs', views.WebLogsViewSet)
router.register(r'swintech-warehouse', views.SwintechWarehousingViewSet)
router.register(r'sublog', views.SubLogViewSet)

urlpatterns = [
    path('login/', views.login_view, name='login'),  # 로그인 URL
    path('', include(router.urls)),  # 입고 목록 조회 URL
    path('auth/', obtain_auth_token),  # 토큰 발급 URL
    
    # 2024.08.26 이성범 수정
    # Content : JWT 토큰 발행 및 인증 URL 추가
    # Purpose : JWT 인증 방식 사용
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 로그인 시 JWT 토큰 발급
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 리프레시 토큰을 사용해 새로운 액세스 토큰 발급
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # JWT 토큰 검증
]
