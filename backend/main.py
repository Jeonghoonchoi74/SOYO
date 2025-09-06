from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 임포트
from routes.user_routes import router as user_router
from routes.bookmark_routes import router as bookmark_router
from routes.review_routes import router as review_router
from routes.comment_routes import router as comment_router
from routes.like_routes import router as like_router
from routes.statistics_routes import router as statistics_router
from routes.translate_routes import router as translate_router
from routes.recommend_routes import router as recommend_router
from routes.firebase_routes import router as firebase_router

# 데이터베이스 초기화
from config.database import initialize_firebase

app = FastAPI(title="Travel Review API", version="1.0.0")

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중이니 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 초기화
initialize_firebase()

# 라우터 등록
app.include_router(user_router)
app.include_router(bookmark_router)
app.include_router(review_router)
app.include_router(comment_router)
app.include_router(like_router)
app.include_router(statistics_router)
app.include_router(translate_router)
app.include_router(recommend_router)
app.include_router(firebase_router)

@app.get("/")
async def root():
    return {"message": "Travel Review API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)