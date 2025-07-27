from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import time
import asyncio

app = FastAPI()

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중이니 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase Admin SDK 초기화 (한 번만)
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase.json')  # 서비스 계정 키 경로
    print ("파일 확인 완료")
    firebase_admin.initialize_app(cred)
    print ("파이어베이스 초기화 완료")

db = firestore.client()

@app.post("/api/register_user")
async def register_user(request: Request):
    data = await request.json()
    uid = data.get('uid')
    name = data.get('name')
    lang = data.get('lang')
    email = data.get('email')
    provider = data.get('provider', 'email')  # 기본값은 email
    
    if not uid or not name or not lang:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    # Firestore에 저장
    user_data = {
        'name': name,
        'lang': lang,
        'createdAt': firestore.SERVER_TIMESTAMP,
        'provider': provider
    }
    
    # 이메일이 제공된 경우 추가
    if email:
        user_data['email'] = email
    
    await asyncio.to_thread(
        db.collection('users').document(uid).set,
        user_data
    )
    return {'success': True}

@app.post("/api/update_user_language")
async def update_user_language(request: Request):
    data = await request.json()
    uid = data.get('uid')
    lang = data.get('lang')
    
    if not uid or not lang:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    try:
        # 사용자 언어 설정 업데이트
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

@app.get("/api/get_user_info/{uid}")
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

@app.post("/api/save_user_preferences")
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
        
        # 타임스탬프 기반 고유 문서ID 생성
        doc_id = str(int(time.time() * 1000))
        print(f"문서 ID: {doc_id}")
        
        # Firestore 작업을 별도 스레드에서 실행
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

@app.post("/api/save_bookmark")
async def save_bookmark(request: Request):
    data = await request.json()
    uid = data.get('uid')
    place_id = data.get('placeId')
    bookmark = data.get('bookmark')
    name = data.get('name')
    desc = data.get('desc')
    image = data.get('image')
    if not uid or not place_id:
        return JSONResponse(content={'success': False, 'error': 'Missing uid or placeId'}, status_code=400)
    try:
        await asyncio.to_thread(
            db.collection('users').document(uid).collection('bookmarks').document(str(place_id)).set,
            {
                'bookmark': bookmark,
                'name': name,
                'desc': desc,
                'image': image,
                'rating': 0,  # 기본 평점
                'isPublic': False,  # 기본 비공개
                'createdAt': firestore.SERVER_TIMESTAMP
            },
            merge=True
        )
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/get_user_bookmarks")
async def get_user_bookmarks(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
        docs = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('bookmarks').where('bookmark', '==', True).stream())
        )
        bookmarks = [doc.to_dict() for doc in docs]
        return {'success': True, 'bookmarks': bookmarks}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/delete_user_bookmark")
async def delete_user_bookmark(request: Request):
    data = await request.json()
    uid = data.get('uid')
    place_id = data.get('placeId')
    if not uid or not place_id:
        return JSONResponse(content={'success': False, 'error': 'Missing uid or placeId'}, status_code=400)
    try:
        await asyncio.to_thread(
            db.collection('users').document(uid).collection('bookmarks').document(str(place_id)).delete
        )
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/delete_user_account")
async def delete_user_account(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
        # 사용자의 모든 데이터 삭제
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

@app.post("/api/save_review")
async def save_review(request: Request):
    data = await request.json()
    print("리뷰 저장 요청 데이터:", data)
    
    uid = data.get('uid')
    place_id = data.get('placeId')
    place_name = data.get('placeName')
    place_desc = data.get('placeDesc')
    place_image = data.get('placeImage')
    review = data.get('review')
    user_name = data.get('userName')
    
    print(f"파싱된 데이터: uid={uid}, place_id={place_id}, review={review}")
    
    if not uid or not place_id or not review:
        error_msg = f"Missing required fields: uid={uid}, place_id={place_id}, review={review}"
        print("오류:", error_msg)
        return JSONResponse(content={'success': False, 'error': error_msg}, status_code=400)
    
    try:
        user_reviews_ref = db.collection('users').document(uid).collection('reviews')
        existing = await asyncio.to_thread(lambda: list(user_reviews_ref.where('placeId', '==', place_id).stream()))
        if existing:
            # 이미 있으면 update
            review_doc = existing[0]
            await asyncio.to_thread(
                review_doc.reference.update,
                {
                    'review': review,
                    'createdAt': firestore.SERVER_TIMESTAMP
                }
            )
            # 북마크도 update
            await asyncio.to_thread(
                db.collection('users').document(uid).collection('bookmarks').document(str(place_id)).update,
                {'review': review}
            )
            # all_reviews도 update (여러 개일 수 있으니 모두)
            all_reviews_ref = db.collection('all_reviews')
            docs = await asyncio.to_thread(lambda: list(all_reviews_ref.where('uid', '==', uid).where('placeId', '==', place_id).stream()))
            for doc in docs:
                await asyncio.to_thread(
                    doc.reference.update,
                    {
                        'review': review,
                        'createdAt': firestore.SERVER_TIMESTAMP
                    }
                )
            print("리뷰 수정 성공")
            return {'success': True, 'updated': True}
        else:
            review_id = str(int(time.time() * 1000))
            # 사용자별 리뷰 저장
            user_review_data = {
                'placeId': place_id,
                'placeName': place_name,
                'placeDesc': place_desc,
                'placeImage': place_image,
                'review': review,
                'createdAt': firestore.SERVER_TIMESTAMP
            }
            await asyncio.to_thread(
                db.collection('users').document(uid).collection('reviews').document(review_id).set,
                user_review_data
            )
            # 북마크에 리뷰 추가
            await asyncio.to_thread(
                db.collection('users').document(uid).collection('bookmarks').document(str(place_id)).update,
                {'review': review}
            )
            # 전체 리뷰 컬렉션에 저장 (관리자용) - 북마크 정보도 포함
            bookmark_doc = await asyncio.to_thread(
                db.collection('users').document(uid).collection('bookmarks').document(str(place_id)).get
            )
            bookmark_data = bookmark_doc.to_dict() if bookmark_doc.exists else {}
            
            all_review_data = {
                'uid': uid,
                'userName': user_name,
                'placeId': place_id,
                'placeName': place_name,
                'placeDesc': place_desc,
                'placeImage': place_image,
                'review': review,
                'rating': bookmark_data.get('rating', 0),
                'isPublic': bookmark_data.get('isPublic', False),
                'createdAt': firestore.SERVER_TIMESTAMP
            }
            await asyncio.to_thread(
                db.collection('all_reviews').document(review_id).set,
                all_review_data
            )
            print("리뷰 저장 성공")
            return {'success': True, 'created': True}
    except Exception as e:
        print("리뷰 저장 오류:", str(e))
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/get_user_reviews")
async def get_user_reviews(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
        docs = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('reviews').stream())
        )
        reviews = [doc.to_dict() for doc in docs]
        return {'success': True, 'reviews': reviews}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.get("/api/get_all_reviews")
async def get_all_reviews():
    try:
        docs = await asyncio.to_thread(
            lambda: list(db.collection('all_reviews').order_by('createdAt', direction=firestore.Query.DESCENDING).stream())
        )
        reviews = [doc.to_dict() for doc in docs]
        return {'success': True, 'reviews': reviews}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.get("/api/get_public_bookmarks")
async def get_public_bookmarks():
    """모든 사용자의 공개된 북마크들을 가져오는 API"""
    try:
        public_bookmarks = []
        
        # 모든 사용자 문서 가져오기
        users = await asyncio.to_thread(lambda: list(db.collection('users').stream()))
        
        for user in users:
            user_data = user.to_dict()
            user_name = user_data.get('name', 'Unknown')
            
            # 각 사용자의 공개된 북마크들 가져오기
            bookmarks = await asyncio.to_thread(
                lambda: list(user.reference.collection('bookmarks').where('isPublic', '==', True).stream())
            )
            
            for bookmark in bookmarks:
                bookmark_data = bookmark.to_dict()
                bookmark_data['userName'] = user_name
                bookmark_data['userId'] = user.id
                public_bookmarks.append(bookmark_data)
        
        # 평점 높은 순으로 정렬
        public_bookmarks.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return {'success': True, 'bookmarks': public_bookmarks}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/update_bookmark_rating")
async def update_bookmark_rating(request: Request):
    data = await request.json()
    uid = data.get('uid')
    place_id = data.get('placeId')
    rating = data.get('rating')
    
    if not uid or not place_id or rating is None:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    if not isinstance(rating, int) or rating < 0 or rating > 5:
        return JSONResponse(content={'success': False, 'error': 'Rating must be an integer between 0 and 5'}, status_code=400)
    
    try:
        await asyncio.to_thread(
            db.collection('users').document(uid).collection('bookmarks').document(str(place_id)).update,
            {
                'rating': rating,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
        )
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/update_bookmark_visibility")
async def update_bookmark_visibility(request: Request):
    data = await request.json()
    uid = data.get('uid')
    place_id = data.get('placeId')
    is_public = data.get('isPublic')
    
    if not uid or not place_id or is_public is None:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    if not isinstance(is_public, bool):
        return JSONResponse(content={'success': False, 'error': 'isPublic must be a boolean'}, status_code=400)
    
    try:
        await asyncio.to_thread(
            db.collection('users').document(uid).collection('bookmarks').document(str(place_id)).update,
            {
                'isPublic': is_public,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
        )
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.get("/api/get_statistics")
async def get_statistics():
    try:
        # 전체 사용자 수
        users = await asyncio.to_thread(lambda: list(db.collection('users').stream()))
        total_users = len(users)
        
        # 전체 리뷰 수
        reviews = await asyncio.to_thread(lambda: list(db.collection('all_reviews').stream()))
        total_reviews = len(reviews)
        
        # 전체 북마크 수
        total_bookmarks = 0
        users = await asyncio.to_thread(lambda: list(db.collection('users').stream()))
        for user in users:
            bookmarks = await asyncio.to_thread(lambda: list(user.reference.collection('bookmarks').stream()))
            total_bookmarks += len(bookmarks)
        
        # 장소별 방문 통계
        place_stats = {}
        reviews = await asyncio.to_thread(lambda: list(db.collection('all_reviews').stream()))
        for review in reviews:
            review_data = review.to_dict()
            place_name = review_data.get('placeName', 'Unknown')
            if place_name in place_stats:
                place_stats[place_name] += 1
            else:
                place_stats[place_name] = 1
        
        return {
            'success': True,
            'statistics': {
                'total_users': total_users,
                'total_reviews': total_reviews,
                'total_bookmarks': total_bookmarks,
                'place_stats': place_stats
            }
        }
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.get("/api/data")
async def get_data():
    return {'message': '안녕하세요, FastAPI에서 보낸 데이터입니다!'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)