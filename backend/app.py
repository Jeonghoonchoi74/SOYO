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
    print("북마크 저장 요청 데이터:", data)
    
    uid = data.get('uid')
    content_id = data.get('contentId')  # placeId를 contentId로 변경
    bookmark = data.get('bookmark')
    name = data.get('name')
    desc = data.get('desc')
    image = data.get('image')
    region = data.get('region', '전국')
    
    print(f"파싱된 데이터: uid={uid}, content_id={content_id}, region={region}")
    
    if not uid or not content_id:
        return JSONResponse(content={'success': False, 'error': 'Missing uid or contentId'}, status_code=400)
    
    try:
        # 1. 장소 정보를 /places/{contentId}/info에 저장
        place_info = {
            'name': name,
            'desc': desc,
            'image': image,
            'region': region,
            'createdAt': firestore.SERVER_TIMESTAMP
        }
        
        await asyncio.to_thread(
            db.collection('places').document(content_id).collection('info').document('details').set,
            place_info,
            merge=True
        )
        
        # 2. 사용자별 북마크 저장 (간단한 형태)
        user_bookmark_data = {
            'bookmark': bookmark,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'title': name,
            'contentid' : content_id
        }
        
        await asyncio.to_thread(
            db.collection('users').document(uid).collection('bookmarks').document(content_id).set,
            user_bookmark_data,
            merge=True
        )
        
        print("북마크 저장 성공")
        return {'success': True}
    except Exception as e:
        print("북마크 저장 오류:", str(e))
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/get_user_bookmarks")
async def get_user_bookmarks(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
        # 사용자 북마크 가져오기
        user_bookmarks = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('bookmarks').where('bookmark', '==', True).stream())
        )
        
        bookmarks = []
        for bookmark_doc in user_bookmarks:
            content_id = bookmark_doc.id
            print(f"북마크 처리 중: content_id={content_id}")
            
            # 장소 정보 가져오기
            place_info_doc = await asyncio.to_thread(
                db.collection('places').document(content_id).collection('info').document('details').get
            )
            
            print(f"장소 정보 존재 여부: {place_info_doc.exists}")
            
            if place_info_doc.exists:
                place_info = place_info_doc.to_dict()
                print(f"장소 정보: {place_info}")
                
                # 사용자의 리뷰 정보 가져오기 (평점, 리뷰, 공개여부)
                user_review_doc = await asyncio.to_thread(
                    db.collection('places').document(content_id).collection('reviews').document(uid).get
                )
                
                bookmark_data = {
                    'contentId': content_id,  # placeId를 contentId로 변경
                    'name': place_info.get('name'),
                    'desc': place_info.get('desc'),
                    'image': place_info.get('image'),
                    'region': place_info.get('region', '전국'),
                    'bookmark': True,
                    'createdAt': bookmark_doc.to_dict().get('createdAt')
                }
                
                # 리뷰 정보가 있으면 추가
                if user_review_doc.exists:
                    review_data = user_review_doc.to_dict()
                    bookmark_data.update({
                        'rating': review_data.get('rating', 0),
                        'review': review_data.get('review', ''),
                        'isPublic': review_data.get('isPublic', False)
                    })
                else:
                    # 리뷰가 없으면 기본값 설정
                    bookmark_data.update({
                        'rating': 0,
                        'review': '',
                        'isPublic': False
                    })
                
                bookmarks.append(bookmark_data)
            else:
                print(f"장소 정보가 없음: content_id={content_id}")
                # 장소 정보가 없어도 기본 북마크 데이터는 반환
                bookmark_data = {
                    'contentId': content_id,
                    'name': '알 수 없는 장소',
                    'desc': '',
                    'image': '',
                    'region': '전국',
                    'bookmark': True,
                    'rating': 0,
                    'review': '',
                    'isPublic': False,
                    'createdAt': bookmark_doc.to_dict().get('createdAt')
                }
                bookmarks.append(bookmark_data)
        
        print(f"최종 북마크 개수: {len(bookmarks)}")
        return {'success': True, 'bookmarks': bookmarks}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/delete_user_bookmark")
async def delete_user_bookmark(request: Request):
    data = await request.json()
    uid = data.get('uid')
    content_id = data.get('contentId')  # placeId를 contentId로 변경
    if not uid or not content_id:
        return JSONResponse(content={'success': False, 'error': 'Missing uid or contentId'}, status_code=400)
    try:
        print(f"북마크 삭제 요청: uid={uid}, content_id={content_id}")
        
        # 1. 북마크 문서 가져오기 (리뷰 관련 필드 확인)
        bookmark_ref = db.collection('users').document(uid).collection('bookmarks').document(str(content_id))
        bookmark_doc = await asyncio.to_thread(bookmark_ref.get)
        
        if bookmark_doc.exists:
            bookmark_data = bookmark_doc.to_dict()
            print(f"북마크 데이터: {bookmark_data}")
            
            # 리뷰 관련 필드가 있는지 확인
            has_review = bookmark_data.get('review') or bookmark_data.get('rating') or bookmark_data.get('isPublic') is not None
            print(f"리뷰 관련 필드 존재 여부: {has_review}")
            
            # 2. 북마크의 리뷰 관련 필드만 초기화 (북마크 자체는 유지)
            update_data = {
                'review': None,
                'rating': None,
                'isPublic': None,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            await asyncio.to_thread(bookmark_ref.update, update_data)
            print("북마크 리뷰 관련 필드 초기화 완료")
        else:
            print("북마크 문서가 존재하지 않습니다")
            return JSONResponse(content={'success': False, 'error': 'Bookmark not found'}, status_code=404)
        
        # 장소별 고유한 리뷰 ID 생성
        review_id = f"{uid}_{content_id}"
        
        # 3. 사용자별 리뷰 삭제
        user_review_ref = db.collection('users').document(uid).collection('reviews').document(review_id)
        user_review_doc = await asyncio.to_thread(user_review_ref.get)
        
        if user_review_doc.exists:
            print(f"삭제할 사용자별 리뷰: {user_review_doc.to_dict()}")
            await asyncio.to_thread(user_review_ref.delete)
            print("사용자별 리뷰 삭제 완료")
        else:
            print("삭제할 사용자별 리뷰가 없습니다")
        
        # 4. places 컬렉션에서 리뷰 삭제
        place_review_ref = db.collection('places').document(content_id).collection('reviews').document(uid)
        place_review_doc = await asyncio.to_thread(place_review_ref.get)
        
        if place_review_doc.exists:
            print(f"삭제할 places 리뷰: {place_review_doc.to_dict()}")
            await asyncio.to_thread(place_review_ref.delete)
            print("places 리뷰 삭제 완료")
            
            # 5. 관련 댓글들 삭제
            comments = await asyncio.to_thread(
                lambda: list(db.collection('places').document(content_id).collection('comments').stream())
            )
            for comment in comments:
                comment_data = comment.to_dict()
                if comment_data.get('uid') == uid:  # 해당 사용자의 댓글만 삭제
                    await asyncio.to_thread(comment.reference.delete)
            print(f"사용자 댓글 삭제 완료")
            
            # 6. 관련 좋아요들 삭제
            likes = await asyncio.to_thread(
                lambda: list(db.collection('places').document(content_id).collection('likes').stream())
            )
            for like in likes:
                like_data = like.to_dict()
                if like_data.get('uid') == uid:  # 해당 사용자의 좋아요만 삭제
                    await asyncio.to_thread(like.reference.delete)
            print(f"사용자 좋아요 삭제 완료")
        else:
            print("삭제할 places 리뷰가 없습니다")
        
        print("북마크 리뷰 관련 필드 초기화 및 관련 데이터 삭제 완료")
        return {'success': True}
    except Exception as e:
        print(f"북마크 삭제 오류: {str(e)}")
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
    content_id = data.get('contentId')  # placeId를 contentId로 변경
    review = data.get('review')
    user_name = data.get('userName')
    rating = data.get('rating', 0)
    is_public = data.get('isPublic', False)
    
    print(f"파싱된 데이터: uid={uid}, content_id={content_id}, review={review}, rating={rating}, isPublic={is_public}")
    
    if not uid or not content_id or not review:
        error_msg = f"Missing required fields: uid={uid}, content_id={content_id}, review={review}"
        print("오류:", error_msg)
        return JSONResponse(content={'success': False, 'error': error_msg}, status_code=400)
    
    try:
        # 장소 정보 가져오기
        place_info_doc = await asyncio.to_thread(
            db.collection('places').document(content_id).collection('info').document('details').get
        )
        
        if not place_info_doc.exists:
            return JSONResponse(content={'success': False, 'error': 'Place not found'}, status_code=404)
        
        place_info = place_info_doc.to_dict()
        
        # 장소별 리뷰 데이터
        place_review_data = {
            'uid': uid,
            'userName': user_name,
            'contentId': content_id,  # placeId를 contentId로 변경
            'placeName': place_info.get('name'),
            'placeDesc': place_info.get('desc'),
            'placeImage': place_info.get('image'),
            'review': review,
            'rating': rating,
            'isPublic': is_public,
            'region': place_info.get('region', ''),
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # 장소별 리뷰 저장/업데이트
        place_review_ref = db.collection('places').document(content_id).collection('reviews').document(uid)
        place_review_doc = await asyncio.to_thread(place_review_ref.get)
        
        if place_review_doc.exists:
            # 기존 리뷰 업데이트
            update_data = {**place_review_data}
            update_data['updatedAt'] = firestore.SERVER_TIMESTAMP
            await asyncio.to_thread(
                place_review_ref.update,
                update_data
            )
            created = False
        else:
            # 새 리뷰 생성
            await asyncio.to_thread(
                place_review_ref.set,
                place_review_data
            )
            created = True
        
        # 사용자별 리뷰 저장 (간단한 형태)
        user_review_data = {
            'contentId': content_id,  # placeId를 contentId로 변경
            'review': review,
            'rating': rating,
            'isPublic': is_public,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        user_review_ref = db.collection('users').document(uid).collection('reviews').document(content_id)
        await asyncio.to_thread(
            user_review_ref.set,
            user_review_data
        )
        
        print("리뷰 저장 성공")
        return {'success': True, 'created': created}
        
    except Exception as e:
        print("리뷰 저장 오류:", str(e))
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/delete_review_comment")
async def delete_review_comment(request: Request):
    """리뷰 댓글 삭제 API"""
    data = await request.json()
    content_id = data.get('contentId')  # reviewId 대신 contentId 사용
    comment_id = data.get('commentId')
    uid = data.get('uid')
    
    if not all([content_id, comment_id, uid]):
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    try:
        # 댓글 문서 가져오기 (places 컬렉션에서)
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

@app.post("/api/get_user_reviews")
async def get_user_reviews(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
        # 사용자 리뷰 가져오기
        user_reviews = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('reviews').stream())
        )
        
        reviews = []
        for review_doc in user_reviews:
            content_id = review_doc.id
            review_data = review_doc.to_dict()
            
            # 장소 정보 가져오기
            place_info_doc = await asyncio.to_thread(
                db.collection('places').document(content_id).collection('info').document('details').get
            )
            
            if place_info_doc.exists:
                place_info = place_info_doc.to_dict()
                full_review_data = {
                    'contentId': content_id,  # placeId를 contentId로 변경
                    'placeName': place_info.get('name'),
                    'placeDesc': place_info.get('desc'),
                    'placeImage': place_info.get('image'),
                    'region': place_info.get('region', '전국'),
                    'review': review_data.get('review'),
                    'rating': review_data.get('rating', 0),
                    'isPublic': review_data.get('isPublic', False),
                    'createdAt': review_data.get('createdAt'),
                    'updatedAt': review_data.get('updatedAt')
                }
                reviews.append(full_review_data)
        
        return {'success': True, 'reviews': reviews}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.get("/api/get_all_reviews")
async def get_all_reviews():
    try:
        # places 컬렉션에서 모든 리뷰 가져오기
        places_docs = await asyncio.to_thread(
            lambda: list(db.collection('places').stream())
        )
        
        reviews = []
        for place_doc in places_docs:
            content_id = place_doc.id
            place_reviews = await asyncio.to_thread(
                lambda: list(db.collection('places').document(content_id).collection('reviews').stream())
            )
            
            for review_doc in place_reviews:
                review_data = review_doc.to_dict()
                review_data['id'] = review_doc.id
                review_data['contentId'] = content_id
                reviews.append(review_data)
        
        # 생성일 기준으로 정렬 (최신순)
        reviews.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
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
    content_id = data.get('contentId')  # placeId를 contentId로 변경
    rating = data.get('rating')
    
    if not uid or not content_id or rating is None:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    if not isinstance(rating, int) or rating < 0 or rating > 5:
        return JSONResponse(content={'success': False, 'error': 'Rating must be an integer between 0 and 5'}, status_code=400)
    
    try:
        # 장소별 리뷰에서 평점 업데이트
        place_review_ref = db.collection('places').document(content_id).collection('reviews').document(uid)
        place_review_doc = await asyncio.to_thread(place_review_ref.get)
        
        if place_review_doc.exists:
            # 기존 리뷰가 있으면 평점만 업데이트
            await asyncio.to_thread(
                place_review_ref.update,
                {
                    'rating': rating,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
            )
        else:
            # 리뷰가 없으면 새로 생성 (기본값으로)
            await asyncio.to_thread(
                place_review_ref.set,
                {
                    'uid': uid,
                    'rating': rating,
                    'review': '',
                    'isPublic': False,
                    'createdAt': firestore.SERVER_TIMESTAMP,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
            )
        
        # 사용자별 리뷰도 업데이트
        user_review_ref = db.collection('users').document(uid).collection('reviews').document(content_id)
        await asyncio.to_thread(
            user_review_ref.set,
            {
                'contentId': content_id,  # placeId를 contentId로 변경
                'rating': rating,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            },
            merge=True
        )
        
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/update_bookmark_visibility")
async def update_bookmark_visibility(request: Request):
    data = await request.json()
    uid = data.get('uid')
    content_id = data.get('contentId')  # placeId를 contentId로 변경
    is_public = data.get('isPublic')
    
    if not uid or not content_id or is_public is None:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    if not isinstance(is_public, bool):
        return JSONResponse(content={'success': False, 'error': 'isPublic must be a boolean'}, status_code=400)
    
    try:
        # 장소별 리뷰에서 공개여부 업데이트
        place_review_ref = db.collection('places').document(content_id).collection('reviews').document(uid)
        place_review_doc = await asyncio.to_thread(place_review_ref.get)
        
        if place_review_doc.exists:
            # 기존 리뷰가 있으면 공개여부만 업데이트
            await asyncio.to_thread(
                place_review_ref.update,
                {
                    'isPublic': is_public,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
            )
        else:
            # 리뷰가 없으면 새로 생성 (기본값으로)
            await asyncio.to_thread(
                place_review_ref.set,
                {
                    'uid': uid,
                    'rating': 0,
                    'review': '',
                    'isPublic': is_public,
                    'createdAt': firestore.SERVER_TIMESTAMP,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
            )
        
        # 사용자별 리뷰도 업데이트
        user_review_ref = db.collection('users').document(uid).collection('reviews').document(content_id)
        await asyncio.to_thread(
            user_review_ref.set,
            {
                'contentId': content_id,  # placeId를 contentId로 변경
                'isPublic': is_public,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            },
            merge=True
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
        
        # 전체 리뷰 수 (places 컬렉션에서)
        places_docs = await asyncio.to_thread(lambda: list(db.collection('places').stream()))
        print(f"Places 컬렉션 문서 수: {len(places_docs)}")
        
        total_reviews = 0
        for place_doc in places_docs:
            print(f"장소 ID: {place_doc.id}")
            place_reviews = await asyncio.to_thread(
                lambda: list(db.collection('places').document(place_doc.id).collection('reviews').stream())
            )
            print(f"장소 {place_doc.id}의 리뷰 수: {len(place_reviews)}")
            total_reviews += len(place_reviews)
        
        print(f"총 리뷰 수: {total_reviews}")
        
        # 전체 북마크 수
        total_bookmarks = 0
        users = await asyncio.to_thread(lambda: list(db.collection('users').stream()))
        for user in users:
            bookmarks = await asyncio.to_thread(lambda: list(user.reference.collection('bookmarks').stream()))
            total_bookmarks += len(bookmarks)
        
        # 장소별 방문 통계 (사용자 북마크에서)
        place_stats = {}
        for user in users:
            bookmarks = await asyncio.to_thread(lambda: list(user.reference.collection('bookmarks').stream()))
            print(f"사용자 {user.id}의 북마크 수: {len(bookmarks)}")
            
            for bookmark in bookmarks:
                bookmark_data = bookmark.to_dict()
                content_id = bookmark.id  # 북마크 문서 ID가 contentId
                
                # 북마크 데이터에서 title 필드를 우선적으로 사용
                place_name = None
                
                # 1. 북마크 문서의 title 필드 확인 (가장 우선)
                if bookmark_data.get('title'):
                    place_name = bookmark_data.get('title')
                    print(f"북마크 title 필드에서 장소명 찾음: {place_name}")
                # 2. 북마크 데이터의 name 필드 확인
                elif bookmark_data.get('name') and bookmark_data.get('name') != '알 수 없는 장소':
                    place_name = bookmark_data.get('name')
                    print(f"북마크 name 필드에서 장소명 찾음: {place_name}")
                # 3. api_data에서 모든 지역을 검색하여 title 찾기
                else:
                    regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
                    
                    for region in regions:
                        try:
                            place_info_doc = await asyncio.to_thread(
                                db.collection('api_data').document('ko').collection(region).document(content_id).get
                            )
                            
                            if place_info_doc.exists:
                                place_info = place_info_doc.to_dict()
                                place_name = place_info.get('title')
                                if place_name:
                                    print(f"api_data에서 장소명 찾음: {place_name} (지역: {region})")
                                    break
                        except Exception as e:
                            continue
                
                # 장소명을 찾지 못한 경우 contentId 사용
                if not place_name:
                    place_name = f'장소_{content_id}'
                    print(f"장소명을 찾지 못해 contentId 사용: {place_name}")
                
                if place_name in place_stats:
                    place_stats[place_name] += 1
                else:
                    place_stats[place_name] = 1
                print(f"북마크 통계 추가: {place_name} (contentId: {content_id})")
        
        print(f"장소별 북마크 통계: {place_stats}")
        
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

@app.get("/api/get_public_reviews")
async def get_public_reviews():
    """공개된 모든 리뷰를 가져오는 API"""
    try:
        # print("공개 리뷰 조회 시작")
        
        # 모든 장소 문서 가져오기
        places_docs = await asyncio.to_thread(
            lambda: list(db.collection('places').stream())
        )
        # print(f"전체 장소 개수: {len(places_docs)}")
        
        # 장소 ID들 출력해서 확인
        # for place_doc in places_docs:
        #     print(f"장소 ID: '{place_doc.id}'")
        
        # 새로운 구조: 리뷰를 저장할 때 places 컬렉션에 장소 문서도 함께 생성
        # print("새로운 구조로 공개 리뷰 조회 시작")
        
        # 1. 먼저 places 컬렉션에서 장소들을 가져오기 시도
        try:
            places_docs = await asyncio.to_thread(
                lambda: list(db.collection('places').stream())
            )
            # print(f"places 컬렉션에서 조회한 장소 개수: {len(places_docs)}")
        except Exception as e:
            # print(f"places 컬렉션 조회 오류: {e}")
            places_docs = []
        
        # 2. places 컬렉션이 비어있으면, 리뷰에서 contentId를 추출
        if len(places_docs) == 0:
            # print("places 컬렉션이 비어있으므로 리뷰에서 contentId 추출")
            # 모든 사용자의 리뷰를 확인해서 contentId 추출
            all_users = await asyncio.to_thread(
                lambda: list(db.collection('users').stream())
            )
            
            content_ids = set()
            for user_doc in all_users:
                user_reviews = await asyncio.to_thread(
                    lambda: list(user_doc.reference.collection('reviews').stream())
                )
                for review_doc in user_reviews:
                    review_data = review_doc.to_dict()
                    content_id = review_data.get('contentId')
                    if content_id:
                        content_ids.add(content_id)
                        # print(f"사용자 리뷰에서 추출된 contentId: {content_id}")
            
            # print(f"추출된 고유 contentId 개수: {len(content_ids)}")
            
            # 추출된 contentId들을 places_docs 형태로 변환
            places_docs = []
            for content_id in content_ids:
                # 가상의 문서 객체 생성
                class MockDoc:
                    def __init__(self, doc_id):
                        self.id = doc_id
                places_docs.append(MockDoc(content_id))
        
        # 3. 각 장소에서 공개 리뷰 가져오기
        reviews = []
        for place_doc in places_docs:
            content_id = place_doc.id
            # print(f"처리 중인 장소: '{content_id}'")
            
            try:
                # 각 장소의 공개된 리뷰들 가져오기
                place_reviews = await asyncio.to_thread(
                    lambda: list(db.collection('places').document(content_id).collection('reviews').where('isPublic', '==', True).stream())
                )
                # print(f"장소 '{content_id}'의 공개 리뷰 개수: {len(place_reviews)}")
                
                for review_doc in place_reviews:
                    review_data = review_doc.to_dict()
                    review_data['id'] = content_id
                    review_data['contentId'] = content_id
                    reviews.append(review_data)
            except Exception as e:
                # print(f"장소 {content_id} 리뷰 조회 중 오류: {e}")
                pass
        
        # print(f"총 공개 리뷰 개수: {len(reviews)}")
        
        # 생성일 기준으로 정렬 (최신순)
        reviews.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        return {'success': True, 'reviews': reviews}
    except Exception as e:
        # print(f"공개 리뷰 조회 오류: {e}")
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/get_available_places_for_review")
async def get_available_places_for_review(request: Request):
    """사용자가 리뷰를 작성할 수 있는 장소들을 가져오는 API (북마크에 있지만 리뷰가 없는 장소)"""
    data = await request.json()
    uid = data.get('uid')
    
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    
    try:
        # 사용자의 북마크 가져오기
        user_bookmarks = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('bookmarks').where('bookmark', '==', True).stream())
        )
        
        # 사용자의 기존 리뷰 가져오기
        user_reviews = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('reviews').stream())
        )
        
        reviewed_places = {doc.id for doc in user_reviews}
        
        # 리뷰가 없는 북마크된 장소들만 필터링
        available_places = []
        for bookmark_doc in user_bookmarks:
            content_id = bookmark_doc.id
            
            if content_id not in reviewed_places:
                # 장소 정보 가져오기
                place_info_doc = await asyncio.to_thread(
                    db.collection('places').document(content_id).collection('info').document('details').get
                )
                
                if place_info_doc.exists:
                    place_info = place_info_doc.to_dict()
                    place_data = {
                        'name': place_info.get('name'),
                        'desc': place_info.get('desc'),
                        'image': place_info.get('image'),
                        'region': place_info.get('region', '전국')
                    }
                    available_places.append(place_data)
        
        print(f"리뷰 작성 가능한 장소 개수: {len(available_places)}")
        return {'success': True, 'places': available_places}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.post("/api/get_review_likes/{content_id}")
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

@app.get("/api/get_review_comments/{content_id}")
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

@app.post("/api/toggle_review_like")
async def toggle_review_like(request: Request):
    """리뷰 좋아요 토글 API"""
    data = await request.json()
    print("좋아요 토글 요청 데이터:", data)
    content_id = data.get('contentId')  # placeId를 contentId로 변경
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

@app.post("/api/add_review_comment")
async def add_review_comment(request: Request):
    """리뷰에 댓글 추가 API"""
    data = await request.json()
    print("댓글 추가 요청 데이터:", data)
    content_id = data.get('contentId')  # placeId를 contentId로 변경
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
        
        # 생성된 댓글 정보 반환 (SERVER_TIMESTAMP 대신 현재 시간 사용)
        import datetime
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

@app.post("/api/delete_review")
async def delete_review(request: Request):
    """리뷰 삭제 API - 사용자별 리뷰, places 리뷰, 북마크에서 함께 삭제"""
    data = await request.json()
    uid = data.get('uid')
    content_id = data.get('contentId')  # placeId를 contentId로 변경
    
    if not uid or not content_id:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    try:
        print(f"리뷰 삭제 요청: uid={uid}, content_id={content_id}")
        
        # 1. 사용자별 리뷰 삭제
        user_review_ref = db.collection('users').document(uid).collection('reviews').document(content_id)
        user_review_doc = await asyncio.to_thread(user_review_ref.get)
        
        if user_review_doc.exists:
            await asyncio.to_thread(user_review_ref.delete)
            print("사용자별 리뷰 삭제 완료")
        
        # 2. places 컬렉션에서 리뷰 삭제
        place_review_ref = db.collection('places').document(content_id).collection('reviews').document(uid)
        place_review_doc = await asyncio.to_thread(place_review_ref.get)
        
        if place_review_doc.exists:
            await asyncio.to_thread(place_review_ref.delete)
            print("places 리뷰 삭제 완료")
        
        # 3. 북마크에서 리뷰 정보 제거 (북마크 자체는 유지, 리뷰 관련 필드만 삭제)
        bookmark_ref = db.collection('users').document(uid).collection('bookmarks').document(str(content_id))
        bookmark_doc = await asyncio.to_thread(bookmark_ref.get)
        
        if bookmark_doc.exists:
            bookmark_data = bookmark_doc.to_dict()
            # 리뷰 관련 필드만 제거
            update_data = {}
            if 'review' in bookmark_data:
                update_data['review'] = None
            if 'rating' in bookmark_data:
                update_data['rating'] = 0
            if 'isPublic' in bookmark_data:
                update_data['isPublic'] = False
            
            if update_data:
                await asyncio.to_thread(bookmark_ref.update, update_data)
                print("북마크에서 리뷰 정보 제거 완료")
        
        # 4. 관련 댓글들 삭제
        comments = await asyncio.to_thread(
            lambda: list(db.collection('review_comments').where('reviewId', '==', review_id).stream())
        )
        for comment in comments:
            await asyncio.to_thread(comment.reference.delete)
        print(f"댓글 {len(comments)}개 삭제 완료")
        
        # 5. 관련 좋아요들 삭제
        likes = await asyncio.to_thread(
            lambda: list(db.collection('review_likes').where('reviewId', '==', review_id).stream())
        )
        for like in likes:
            await asyncio.to_thread(like.reference.delete)
        print(f"좋아요 {len(likes)}개 삭제 완료")
        
        print("리뷰 삭제 완료")
        return {'success': True}
        
    except Exception as e:
        print(f"리뷰 삭제 오류: {str(e)}")
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@app.get("/api/data")
async def get_data():
    return {'message': '안녕하세요, FastAPI에서 보낸 데이터입니다!'}

@app.get("/api/get_regions")
async def get_regions():
    try:
        # api_data/ko 컬렉션에서 지역 목록 가져오기
        regions_ref = db.collection('api_data').document('ko')
        regions_doc = regions_ref.get()
        
        if regions_doc.exists:
            # 하위 컬렉션 목록 가져오기
            collections = db.collection('api_data').document('ko').collections()
            regions = []
            for collection_ref in collections:
                regions.append(collection_ref.id)
            
            return JSONResponse(content={
                'success': True,
                'regions': regions
            })
        else:
            # 기본 지역 목록 반환
            default_regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
            return JSONResponse(content={
                'success': True,
                'regions': default_regions
            })
            
    except Exception as e:
        print(f"지역 로드 오류: {e}")
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

