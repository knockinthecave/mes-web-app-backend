from django.conf.urls import url, include
from django.urls import path, include
from rest_framework import routers
from . import views 
from rest_framework.authtoken.views import obtain_auth_token 

router = routers.DefaultRouter()
router.register(r'inventory', views.ExternalInventoryViewSet)
router.register(r'warehouse', views.ExternalWarhousingViewSet)
router.register(r'bom', views.BOMViewSet)
router.register(r'importinspection', views.ImportInspectionViewSet)
router.register(r'assembly-instruction', views.AssemblyInstructionViewSet)
router.register(r'assembly-completed', views.AssemblyCompletedViewSet)
router.register(r'logs', views.WebLogsViewSet)
router.register(r'packaging', views.PackagingViewSet)


urlpatterns = [
    path('login/', views.login_view, name='login'), # 로그인 URL
    path('', include(router.urls)), # 입고 목록 조회 URL
    path('auth/', obtain_auth_token), # 토큰 발급 URL
]
