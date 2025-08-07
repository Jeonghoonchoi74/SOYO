from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from firebase_admin import firestore
import asyncio
from config.database import get_db

router = APIRouter(prefix="/api", tags=["likes"])
db = get_db()

@router.post("/toggle_review_like")
async def toggle_review_like(request: Request):
    """리뷰 좋아요 토글 API"""
    data = await request.json()
    print("좋아요 토글 요청 데이터:", data)
    content_id = data.get('contentId')
    uid = data.get('uid')
    user_name = data.get('userName')
    
    print(f"파싱된 데이터: content_id={content_id}, uid={uid}")
    
    if not content_id or not uid:
        error_msg = f"Missing required fields: content_id={content_id}, uid={uid}"
        print("오류:", error_msg)
        return JSONResponse(content={'success': False, 'error': error_msg}, status_code=400)
    
    try:
        # 장소별 좋아요 확인
        place_like_ref = db.collection('places').document(content_id).collection('likes').document(uid)
        place_like_doc = await asyncio.to_thread(place_like_ref.get)
        
        if place_like_doc.exists:
            # 좋아요 취소
            await asyncio.to_thread(place_like_ref.delete)
            is_liked = False
        else:
            # 좋아요 추가
            like_data = {
                'uid': uid,
                'userName': user_name,
                'createdAt': firestore.SERVER_TIMESTAMP
            }
            await asyncio.to_thread(
                place_like_ref.set,
                like_data
            )
            is_liked = True
        
        # 총 좋아요 수 계산
        all_likes = await asyncio.to_thread(
            lambda: list(db.collection('places').document(content_id).collection('likes').stream())
        )
        total_likes = len(all_likes)
        
        return {
            'success': True,
            'isLiked': is_liked,
            'totalLikes': total_likes
        }
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/get_review_likes/{content_id}")
async def get_review_likes(content_id: str, request: Request):
    """특정 장소의 좋아요 정보를 가져오는 API"""
    try:
        data = await request.json()
        uid = data.get('uid')
        
        likes_docs = await asyncio.to_thread(
            lambda: list(db.collection('places').document(content_id).collection('likes').stream())
        )
        
        total_likes = len(likes_docs)
        
        # 현재 사용자의 좋아요 여부 확인
        user_liked = False
        if uid:
            user_like_doc = await asyncio.to_thread(
                db.collection('places').document(content_id).collection('likes').document(uid).get
            )
            user_liked = user_like_doc.exists
        
        return {
            'success': True, 
            'likes': total_likes,
            'userLiked': user_liked
        }
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)