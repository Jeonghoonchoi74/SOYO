from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from firebase_admin import firestore
import asyncio
import datetime
from config.database import get_db

router = APIRouter(prefix="/api", tags=["reviews"])
db = get_db()

@router.post("/save_review")
async def save_review(request: Request):
    data = await request.json()
    print("리뷰 저장 요청 데이터:", data)
    
    uid = data.get('uid')
    content_id = data.get('contentId')
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
            'contentId': content_id,
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
        
        # 사용자별 리뷰 저장
        user_review_data = {
            'contentId': content_id,
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

@router.post("/get_user_reviews")
async def get_user_reviews(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
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
                    'contentId': content_id,
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

@router.get("/get_all_reviews")
async def get_all_reviews():
    try:
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
        
        reviews.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        return {'success': True, 'reviews': reviews}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.get("/get_public_reviews")
async def get_public_reviews():
    """공개된 모든 리뷰를 가져오는 API"""
    try:
        places_docs = await asyncio.to_thread(
            lambda: list(db.collection('places').stream())
        )
        
        if len(places_docs) == 0:
            # places 컬렉션이 비어있으면, 리뷰에서 contentId를 추출
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
            
            # 추출된 contentId들을 places_docs 형태로 변환
            places_docs = []
            for content_id in content_ids:
                class MockDoc:
                    def __init__(self, doc_id):
                        self.id = doc_id
                places_docs.append(MockDoc(content_id))
        
        # 각 장소에서 공개 리뷰 가져오기
        reviews = []
        for place_doc in places_docs:
            content_id = place_doc.id
            
            try:
                place_reviews = await asyncio.to_thread(
                    lambda: list(db.collection('places').document(content_id).collection('reviews').where('isPublic', '==', True).stream())
                )
                
                for review_doc in place_reviews:
                    review_data = review_doc.to_dict()
                    review_data['id'] = content_id
                    review_data['contentId'] = content_id
                    reviews.append(review_data)
            except Exception as e:
                pass
        
        reviews.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        return {'success': True, 'reviews': reviews}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/delete_review")
async def delete_review(request: Request):
    """리뷰 삭제 API - 사용자별 리뷰, places 리뷰, 북마크에서 함께 삭제"""
    data = await request.json()
    uid = data.get('uid')
    content_id = data.get('contentId')
    
    if not uid or not content_id:
        return JSONResponse(content={'success': False, 'error': 'Missing required fields'}, status_code=400)
    
    try:
        print(f"리뷰 삭제 요청: uid={uid}, content_id={content_id}")
        
        # 1. 사용자별 리뷰 삭제
        user_review_ref = db.collection('users').document(uid).collection('reviews').document(content_id)
        user_review_doc = await asyncio.to_thread(user_review_ref.get)
        
        if user_review_doc.exists:
            print(f"삭제할 사용자별 리뷰 데이터: {user_review_doc.to_dict()}")
            await asyncio.to_thread(user_review_ref.delete)
            print("사용자별 리뷰 삭제 완료")
        else:
            print("삭제할 사용자별 리뷰가 존재하지 않습니다")
        
        # 2. places 컬렉션에서 리뷰 삭제
        place_review_ref = db.collection('places').document(content_id).collection('reviews').document(uid)
        place_review_doc = await asyncio.to_thread(place_review_ref.get)
        
        if place_review_doc.exists:
            print(f"삭제할 places 리뷰 데이터: {place_review_doc.to_dict()}")
            await asyncio.to_thread(place_review_ref.delete)
            print("places 리뷰 삭제 완료")
        else:
            print("삭제할 places 리뷰가 존재하지 않습니다")
        
        # 3. 북마크 완전 삭제
        bookmark_ref = db.collection('users').document(uid).collection('bookmarks').document(str(content_id))
        bookmark_doc = await asyncio.to_thread(bookmark_ref.get)
        
        if bookmark_doc.exists:
            print(f"삭제할 북마크 데이터: {bookmark_doc.to_dict()}")
            await asyncio.to_thread(bookmark_ref.delete)
            print("북마크 삭제 완료")
        else:
            print("삭제할 북마크가 존재하지 않습니다")
        
        # 4. 관련 댓글들 삭제
        comments = await asyncio.to_thread(
            lambda: list(db.collection('places').document(content_id).collection('comments').stream())
        )
        for comment in comments:
            comment_data = comment.to_dict()
            if comment_data.get('uid') == uid:
                await asyncio.to_thread(comment.reference.delete)
        print(f"사용자 댓글 삭제 완료")
        
        # 5. 관련 좋아요들 삭제
        likes = await asyncio.to_thread(
            lambda: list(db.collection('places').document(content_id).collection('likes').stream())
        )
        for like in likes:
            like_data = like.to_dict()
            if like_data.get('uid') == uid:
                await asyncio.to_thread(like.reference.delete)
        print(f"사용자 좋아요 삭제 완료")
        
        # 6. 해당 장소에 다른 리뷰가 남아있는지 확인
        remaining_reviews = await asyncio.to_thread(
            lambda: list(db.collection('places').document(content_id).collection('reviews').stream())
        )
        
        # 7. 다른 사용자의 북마크가 남아있는지 확인
        all_users = await asyncio.to_thread(lambda: list(db.collection('users').stream()))
        has_other_bookmarks = False
        
        for user in all_users:
            if user.id != uid:
                other_bookmark = await asyncio.to_thread(
                    db.collection('users').document(user.id).collection('bookmarks').document(str(content_id)).get
                )
                if other_bookmark.exists:
                    has_other_bookmarks = True
                    break
        
        # 8. 리뷰도 없고 다른 북마크도 없으면 장소 정보도 삭제
        if len(remaining_reviews) == 0 and not has_other_bookmarks:
            # info 서브컬렉션 삭제
            info_docs = await asyncio.to_thread(
                lambda: list(db.collection('places').document(content_id).collection('info').stream())
            )
            for info_doc in info_docs:
                await asyncio.to_thread(info_doc.reference.delete)
            
            # places 문서 자체도 삭제
            place_doc = await asyncio.to_thread(
                db.collection('places').document(content_id).get
            )
            if place_doc.exists:
                await asyncio.to_thread(place_doc.reference.delete)
            
            print(f"장소 {content_id}의 모든 데이터 삭제 완료 (다른 사용자 데이터 없음)")
        else:
            print(f"장소 {content_id}에 다른 데이터가 남아있어 info는 유지됩니다 (리뷰: {len(remaining_reviews)}개, 다른 북마크: {has_other_bookmarks})")
        
        print("리뷰 삭제 완료")
        return {'success': True}
        
    except Exception as e:
        print(f"리뷰 삭제 오류: {str(e)}")
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/get_place_reviews")
async def get_place_reviews(request: Request):
    """특정 장소의 모든 리뷰를 가져오는 API"""
    data = await request.json()
    content_id = data.get('contentId')
    
    if not content_id:
        return JSONResponse(content={'success': False, 'error': 'Missing contentId'}, status_code=400)
    
    try:
        # 해당 장소의 공개된 리뷰만 가져오기
        place_reviews = await asyncio.to_thread(
            lambda: list(db.collection('places').document(content_id).collection('reviews').where('isPublic', '==', True).stream())
        )
        
        reviews = []
        for review_doc in place_reviews:
            review_data = review_doc.to_dict()
            # 필요한 정보만 추출 (uid 제외)
            filtered_review = {
                'userName': review_data.get('userName', '익명'),
                'review': review_data.get('review', ''),
                'rating': review_data.get('rating', 0),
                'createdAt': review_data.get('createdAt')
            }
            reviews.append(filtered_review)
        
        # 생성일 기준으로 최신순 정렬
        reviews.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        print(f"장소 {content_id}의 공개 리뷰 {len(reviews)}개 조회 완료")
        return {'success': True, 'reviews': reviews}
        
    except Exception as e:
        print(f"장소 리뷰 조회 오류: {str(e)}")
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/get_available_places_for_review")
async def get_available_places_for_review(request: Request):
    """사용자가 리뷰를 작성할 수 있는 장소들을 가져오는 API"""
    data = await request.json()
    uid = data.get('uid')
    
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    
    try:
        user_bookmarks = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('bookmarks').where('bookmark', '==', True).stream())
        )
        
        user_reviews = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('reviews').stream())
        )
        
        # 리뷰를 작성한 장소 ID들을 문자열로 변환하여 저장
        reviewed_places = {str(doc.id) for doc in user_reviews}
        print(f"사용자 {uid}가 리뷰를 작성한 장소들: {reviewed_places}")
        
        available_places = []
        for bookmark_doc in user_bookmarks:
            content_id = str(bookmark_doc.id)  # 문자열로 변환
            
            if content_id not in reviewed_places:
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