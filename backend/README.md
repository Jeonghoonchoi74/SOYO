# Backend API Server

FastAPI 기반의 여행 리뷰 및 북마크 관리 API 서버입니다.

## 설치 및 실행 방법

### 1. 가상환경(venv) 생성 및 활성화
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Firebase 설정
- `firebase.json` 파일을 backend 디렉토리에 배치
- Firebase Admin SDK 서비스 계정 키 파일

### 4. FastAPI 서버 실행
```bash
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## 프로젝트 구조

```
backend/
├── app.py                    # 메인 애플리케이션 파일
├── main.py                   # 대안 메인 파일
├── config/
│   ├── __init__.py
│   └── database.py           # Firebase 설정 및 DB 연결
└── routes/
    ├── __init__.py
    ├── user_routes.py         # 사용자 관련 API
    ├── bookmark_routes.py     # 북마크 관련 API
    ├── review_routes.py       # 리뷰 관련 API
    ├── comment_routes.py      # 댓글 관련 API
    ├── like_routes.py         # 좋아요 관련 API
    └── statistics_routes.py   # 통계 및 기타 API
```

## API 엔드포인트

### 사용자 관리 (User Routes)
- `POST /api/register_user` - 사용자 등록
- `POST /api/update_user_language` - 사용자 언어 설정 업데이트
- `GET /api/get_user_info/{uid}` - 사용자 정보 조회
- `POST /api/save_user_preferences` - 사용자 선호도 저장
- `POST /api/delete_user_account` - 사용자 계정 삭제

### 북마크 관리 (Bookmark Routes)
- `POST /api/save_bookmark` - 북마크 저장
- `POST /api/get_user_bookmarks` - 사용자 북마크 목록 조회
- `POST /api/delete_user_bookmark` - 북마크 삭제
- `POST /api/update_bookmark_rating` - 북마크 평점 업데이트
- `POST /api/update_bookmark_visibility` - 북마크 공개여부 설정
- `GET /api/get_public_bookmarks` - 공개 북마크 목록 조회

### 리뷰 관리 (Review Routes)
- `POST /api/save_review` - 리뷰 저장
- `POST /api/get_user_reviews` - 사용자 리뷰 목록 조회
- `GET /api/get_all_reviews` - 모든 리뷰 조회
- `GET /api/get_public_reviews` - 공개 리뷰 조회
- `POST /api/delete_review` - 리뷰 삭제
- `POST /api/get_available_places_for_review` - 리뷰 작성 가능한 장소 조회

### 댓글 관리 (Comment Routes)
- `POST /api/add_review_comment` - 댓글 추가
- `GET /api/get_review_comments/{content_id}` - 댓글 목록 조회
- `POST /api/delete_review_comment` - 댓글 삭제

### 좋아요 관리 (Like Routes)
- `POST /api/toggle_review_like` - 좋아요 토글
- `POST /api/get_review_likes/{content_id}` - 좋아요 정보 조회

### 통계 및 기타 (Statistics Routes)
- `GET /api/get_statistics` - 통계 정보 조회
- `GET /api/get_regions` - 지역 목록 조회
- `GET /api/data` - 기본 데이터 조회

## 기술 스택

- **FastAPI**: 웹 프레임워크
- **Firebase Admin SDK**: 데이터베이스 및 인증
- **Python 3.8+**: 프로그래밍 언어
- **asyncio**: 비동기 처리

## 개발 환경

- Python 3.8 이상
- Firebase 프로젝트 설정 필요
- 가상환경 사용 권장

## 주요 기능

1. **모듈화된 구조**: 기능별로 라우터를 분리하여 유지보수성 향상
2. **비동기 처리**: asyncio를 사용한 효율적인 데이터베이스 작업
3. **Firebase 통합**: Firestore를 사용한 실시간 데이터 관리
4. **CORS 지원**: 프론트엔드와의 원활한 통신
5. **에러 처리**: 적절한 HTTP 상태 코드와 에러 메시지 제공