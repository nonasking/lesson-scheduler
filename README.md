# LESSON-SCHEDULER

---

## Description

`LESSON-SCHEDULER`는 선생님이 선생님-학생 간의 수업 스케줄을 관리할 수 있는 시스템입니다.
<br/>
`Django` 프레임워크와 `PostgreSQL` DB를 기반으로 만들었습니다.

---

## 구조

```
├── manage.py
├── .env
├── README.md
├── requirements.txt
├── .gitignore
├── lesson_scheduler /
  ├── __init__.py
  ├── asgi.py
  ├── settings.py
  ├── urls.py
  └── wsgi.py
├── schedules /
  ├── migrations /
  ├── __init__.py
  ├── admin.py
  ├── apps.py
  ├── constants.py
  ├── models.py
  ├── serializers.py
  ├── tests.py
  ├── urls.py
  ├── utils.py
  └── views.py
```

---

## DB Tables ERD

![LESSON-SCHEDULER-ERD-DIAGRAM](https://github.com/user-attachments/assets/2d20448e-0fa6-4e1f-8111-4fb915e0ac66)

---

## 구동

### 1. 환경변수 파일 `.env` 세팅

보안상 민감할 수 있는 정보는 환경변수 파일로 분리해두었습니다.
파일은 별도로 전달드리겠습니다.

```shell
SECRET_KEY=
DB_ENGINE=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

### 2. 필요 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 구동

```bash
python manage.py runserver
```

### cf. 테스트 코드 실행

```bash
python manage.py test
```

---

## API 명세

[API docs (Postman)](https://documenter.getpostman.com/view/18889475/2sAXjKbtLG)

---

## 적용 기술

- main
  - `Python`: 3.12.5
  - `Django`: 5.1
  - `djangorestframework`: 3.15.2
  - `PostgreSQL`: 14.11
- library
  - `python-decouple`: 3.8
    - 환경변수 관리를 위해 사용했습니다.

---

## 기타

### 인증 관련

인증(로그인, 회원가입)을 생략하고 스케줄 관련 API만 구현하면서, 추후 인증 로직을 추가할 때 수정을 최소화할 수 있도록 구현하고자 했습니다.
<br/>
이를 위해 API에서 현재 유저를 검증하는 부분은 프론트엔드로부터 API Header로 Teacher의 id를 받아서 처리하도록 구현했습니다. 추후 인증을 추가 구현하여 프론트엔드로부터 id가 아닌 암호화된 사용자 정보(ex. 토큰)를 받아오도록 수정해야 합니다.
