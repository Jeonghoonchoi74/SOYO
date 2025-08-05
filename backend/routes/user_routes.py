from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from firebase_admin import firestore
import asyncio
import time
from config.database import get_db

router = APIRouter(prefix="/api", tags=["users"])
db = get_db()

@router.post("/register_user")
async def register_user(request: Request):
    data = await request.json()
    uid = data.get('uid')
    name = data.get('name')
    lang = data.get('lang')
    email = data.get('email')
    provider = data.get('provider', 'email')
    
    if not uid or not name or not lang:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    user_data = {
        'name': name,
        'lang': lang,
        'createdAt': firestore.SERVER_TIMESTAMP,
        'provider': provider
    }
    
    if email:
        user_data['email'] = email
    
    await asyncio.to_thread(
        db.collection('users').document(uid).set,
        user_data
    )
    return {'success': True}

@router.post("/update_user_language")
async def update_user_language(request: Request):
    data = await request.json()
    uid = data.get('uid')
    lang = data.get('lang')
    
    if not uid or not lang:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    try:
        await asyncio.to_thread(
            db.collection('users').document(uid).update,
            {
                'lang': lang,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
        )
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.get("/get_user_info/{uid}")
async def get_user_info(uid: str):
    try:
        user_doc = await asyncio.to_thread(
            db.collection('users').document(uid).get
        )
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return {'success': True, 'user': user_data}
        else:
            return JSONResponse(content={'success': False, 'error': 'User not found'}, status_code=404)
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/save_user_preferences")
async def save_user_preferences(request: Request):
    try:
        data = await request.json()
        print("받은 데이터:", data)
        uid = data.get('uid')
        preferences = data.get('preferences', {})
        print(f"UID: {uid}, Preferences: {preferences}")
        
        if not uid:
            return JSONResponse(content={'success': False, 'error': 'Missing user ID'}, status_code=400)
        
        user_preferences = {
            'food': preferences.get('food'),
            'shopping': preferences.get('shopping'),
            'attraction': preferences.get('attraction'),
            'sns': preferences.get('sns'),
            'purpose': preferences.get('purpose'),
            'freeText': preferences.get('freeText', ''),
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        print("저장할 데이터:", user_preferences)
        
        doc_id = str(int(time.time() * 1000))
        print(f"문서 ID: {doc_id}")
        
        await asyncio.to_thread(
            db.collection('users').document(uid).collection('preferences').document(doc_id).set,
            user_preferences
        )
        print("Firestore 저장 성공")
        return {'success': True}
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        import traceback
        print("전체 에러:", traceback.format_exc())
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/delete_user_account")
async def delete_user_account(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
        user_ref = db.collection('users').document(uid)
        
        # 북마크 컬렉션 삭제
        bookmarks = await asyncio.to_thread(lambda: list(user_ref.collection('bookmarks').stream()))
        for bookmark in bookmarks:
            await asyncio.to_thread(bookmark.reference.delete)
        
        # 선호도 컬렉션 삭제
        preferences = await asyncio.to_thread(lambda: list(user_ref.collection('preferences').stream()))
        for preference in preferences:
            await asyncio.to_thread(preference.reference.delete)
        
        # 사용자 문서 삭제
        await asyncio.to_thread(user_ref.delete)
        
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)