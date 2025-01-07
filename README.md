# MES 모바일 웹 앱 Backend

## 설치방법

1. 가상환경 설치 및 실행
```python
python -m venv venv(가상환경이름)
venv\Scripts\activate(윈도우 전용)
```

2. requirements.txt를 통한 필요 라이브러리 설치
```
pip install -r requirements.txt
```

3. 서버 실행
```
python manage.py runserver xxx.xxx.xxx.xxx:port
```

부록. 마이그레이션
DB에 테이블이나 칼럼이 변경되는 변경사항 존재시 변경됨을 migrate 해야함.
```
python manage.py migrate
```
