# 인벤토리 관리 백엔드

## 개요
이 프로젝트는 재고 관리를 위한 백엔드 시스템으로, Python과 Django 프레임워크를 사용하여 개발되었습니다. 제품 관리, 재고 추적, 주문 처리, 보고서 생성을 위한 API를 제공합니다.

---

## 주요 기능
- **제품 관리**: 제품 생성, 조회, 수정, 삭제 기능 제공
- **재고 추적**: 제품의 실시간 재고 현황 추적
- **주문 처리**: 고객 주문 생성 및 관리
- **보고서 생성**: 판매 및 재고에 대한 다양한 보고서 생성

---

## 사용 기술
- **프로그래밍 언어**: Python
- **웹 프레임워크**: Django
- **데이터베이스**: SQLite (MySQL 또는 PostgreSQL로 변경 가능)
- **API 문서화**: Swagger (`drf-yasg`) 또는 Django REST Framework 자동 문서화 도구

---

## 설치 및 실행 방법

### 1. 저장소 클론
```bash
git clone https://github.com/knockinthecave/inventory-manage-backend.git
cd inventory-manage-backend
```

### 2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 마이그레이션 적용
```bash
python manage.py migrate
```

### 5. 개발 서버 실행
```bash
python manage.py runserver
```
다음 주소에서 서버를 확인할 수 있습니다: [http://localhost:8000](http://localhost:8000)

---

## URL 명세서

### 기본 라우터 URL
다음 URL은 Django REST Framework의 `DefaultRouter`를 통해 자동으로 생성됩니다:

- **URL**: `/inventory/`
  - **View**: `ExternalInventoryViewSet`
  - **설명**: 외부 재고 조회 및 관리

- **URL**: `/warehouse/`
  - **View**: `ExternalWarhousingViewSet`
  - **설명**: 창고 입고 및 관리

- **URL**: `/bom/`
  - **View**: `BOMViewSet`
  - **설명**: BOM(자재 명세서) 관리

- **URL**: `/importinspection/`
  - **View**: `ImportInspectionViewSet`
  - **설명**: 수입 검사 관리

- **URL**: `/assembly-instruction/`
  - **View**: `AssemblyInstructionViewSet`
  - **설명**: 조립 지침 관리

- **URL**: `/assembly-completed/`
  - **View**: `AssemblyCompletedViewSet`
  - **설명**: 조립 완료 데이터 관리

- **URL**: `/logs/`
  - **View**: `WebLogsViewSet`
  - **설명**: 웹 로그 관리

- **URL**: `/swintech-warehouse/`
  - **View**: `SwintechWarehousingViewSet`
  - **설명**: Swintech 창고 관리

- **URL**: `/sublog/`
  - **View**: `SubLogViewSet`
  - **설명**: 서브 로그 관리

---

### 추가 URL

- **URL**: `/login/`
  - **Method**: `POST`
  - **View**: `login_view`
  - **설명**: 사용자 로그인

- **URL**: `/auth/`
  - **Method**: `POST`
  - **View**: `obtain_auth_token`
  - **설명**: 토큰 발급

- **JWT 관련 URL**
  - **URL**: `/token/`
    - **Method**: `POST`
    - **View**: `TokenObtainPairView`
    - **설명**: JWT 토큰 발급

  - **URL**: `/token/refresh/`
    - **Method**: `POST`
    - **View**: `TokenRefreshView`
    - **설명**: 리프레시 토큰을 사용해 새로운 액세스 토큰 발급

  - **URL**: `/token/verify/`
    - **Method**: `POST`
    - **View**: `TokenVerifyView`
    - **설명**: JWT 토큰 검증

---

## 기여 방법
1. 저장소를 포크합니다.
2. 새 브랜치를 생성합니다:
   ```bash
   git checkout -b feature/기능명
   ```
3. 변경사항을 커밋합니다:
   ```bash
   git commit -m "메시지 입력"
   ```
4. 브랜치를 푸시합니다:
   ```bash
   git push origin feature/기능명
   ```
5. 풀 리퀘스트를 생성합니다.

---

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

---

