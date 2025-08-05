from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from firebase_admin import firestore
import asyncio
import datetime
from config.database import get_db

router = APIRouter(prefix="/api", tags=["comments"])
db = get_db()

@router.post("/add_review_comment")
async def add_review_comment(request: Request):
    """리뷰에 댓글 추가 API"""
    data = await request.json()
    print("댓글 추가 요청 데이터:", data)
    content_id = data.get('contentId')
    uid = data.get('uid')
    user_name = data.get('userName')
    comment_text = data.get('comment')
    
    print(f"파싱된 데이터: content_id={content_id}, uid={uid}, comment={comment_text}")
    
    if not all([content_id, uid, user_name, comment_text]):
        error_msg = f"Missing required fields: content_id={content_id}, uid={uid}, comment={comment_text}"
        print("오류:", error_msg)
        return JSONResponse(content={'success': False, 'error': error_msg}, status_code=400)
    
    try:
        comment_data = {
            'uid': uid,
            'userName': user_name,
            'text': comment_text,
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = await asyncio.to_thread(
            db.collection('places').document(content_id).collection('comments').add,
            comment_data
        )
        
        # 생성된 댓글 정보 반환
        comment_response = {
            'id': doc_ref[1].id,
            'uid': uid,
            'userName': user_name,
            'text': comment_text,
            'createdAt': datetime.datetime.now(datetime.timezone.utc)
        }
        
        return {
            'success': True,
            'comment': comment_response
        }
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.get("/get_review_comments/{content_id}")
async def get_review_comments(content_id: str):
    """특정 장소의 댓글들을 가져오는 API"""
    try:
        comments_docs = await asyncio.to_thread(
            lambda: list(db.collection('places').document(content_id).collection('comments').order_by('createdAt').stream())
        )
        
        comments = []
        for doc in comments_docs:
            comment_data = doc.to_dict()
            comment_data['id'] = doc.id
            comments.append(comment_data)
        
        return {'success': True, 'comments': comments}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/delete_review_comment")
async def delete_review_comment(request: Request):
    """리뷰 댓글 삭제 API"""
    data = await request.json()
    content_id = data.get('contentId')
    comment_id = data.get('commentId')
    uid = data.get('uid')
    
    if not all([content_id, comment_id, uid]):
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    try:
        # 댓글 문서 가져오기
        comment_ref = db.collection('places').document(content_id).collection('comments').document(comment_id)
        comment_doc = await asyncio.to_thread(comment_ref.get)
        
        if not comment_doc.exists:
            return JSONResponse(content={'success': False, 'error': 'Comment not found'}, status_code=404)
        
        comment_data = comment_doc.to_dict()
        
        # 댓글 작성자인지 확인
        if comment_data.get('uid') != uid:
            return JSONResponse(content={'success': False, 'error': 'Unauthorized'}, status_code=403)
        
        # 댓글 삭제
        await asyncio.to_thread(comment_ref.delete)
        
        return {'success': True, 'message': 'Comment deleted successfully'}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)