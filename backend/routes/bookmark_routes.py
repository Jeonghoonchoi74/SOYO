from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from firebase_admin import firestore
import asyncio
from config.database import get_db

router = APIRouter(prefix="/api", tags=["bookmarks"])
db = get_db()

@router.post("/save_bookmark")
async def save_bookmark(request: Request):
    data = await request.json()
    print("북마크 저장 요청 데이터:", data)
    print("전체 데이터 키들:", list(data.keys()))
    print("상세 정보 확인:")
    print(f"  address: {data.get('address')}")
    print(f"  detailAddress: {data.get('detailAddress')}")
    print(f"  contact: {data.get('contact')}")
    print(f"  openingHours: {data.get('openingHours')}")
    print(f"  restDay: {data.get('restDay')}")
    print(f"  representativeMenu: {data.get('representativeMenu')}")
    print(f"  menu: {data.get('menu')}")
    print(f"  eventStartDate: {data.get('eventStartDate')}")
    print(f"  eventEndDate: {data.get('eventEndDate')}")
    print(f"  eventIntro: {data.get('eventIntro')}")
    print(f"  eventContent: {data.get('eventContent')}")
    print(f"  inquiry: {data.get('inquiry')}")
    print(f"  usageTime: {data.get('usageTime')}")
    print(f"  performanceTime: {data.get('performanceTime')}")
    print(f"  duration: {data.get('duration')}")
    print(f"  ageLimit: {data.get('ageLimit')}")
    print(f"  bookingPlace: {data.get('bookingPlace')}")
    print(f"  discountInfo: {data.get('discountInfo')}")
    print(f"  eventGrade: {data.get('eventGrade')}")
    print(f"  status: {data.get('status')}")
    print(f"  category: {data.get('category')}")
    
    uid = data.get('uid')
    content_id = data.get('contentId')
    bookmark = data.get('bookmark')
    name = data.get('name')
    desc = data.get('desc')
    image = data.get('image')
    region = data.get('region', '전국')
    
    # 상세 정보 추가
    address = data.get('address')
    detail_address = data.get('detailAddress')
    contact = data.get('contact')
    opening_hours = data.get('openingHours')
    rest_day = data.get('restDay')
    representative_menu = data.get('representativeMenu')
    menu = data.get('menu')
    event_start_date = data.get('eventStartDate')
    event_end_date = data.get('eventEndDate')
    event_intro = data.get('eventIntro')
    event_content = data.get('eventContent')
    inquiry = data.get('inquiry')
    usage_time = data.get('usageTime')
    performance_time = data.get('performanceTime')
    duration = data.get('duration')
    age_limit = data.get('ageLimit')
    booking_place = data.get('bookingPlace')
    discount_info = data.get('discountInfo')
    event_grade = data.get('eventGrade')
    status = data.get('status')
    category = data.get('category')
    
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
            'createdAt': firestore.SERVER_TIMESTAMP,
            # 상세 정보 추가
            'address': address,
            'detailAddress': detail_address,
            'contact': contact,
            'openingHours': opening_hours,
            'restDay': rest_day,
            'representativeMenu': representative_menu,
            'menu': menu,
            'eventStartDate': event_start_date,
            'eventEndDate': event_end_date,
            'eventIntro': event_intro,
            'eventContent': event_content,
            'inquiry': inquiry,
            'usageTime': usage_time,
            'performanceTime': performance_time,
            'duration': duration,
            'ageLimit': age_limit,
            'bookingPlace': booking_place,
            'discountInfo': discount_info,
            'eventGrade': event_grade,
            'status': status,
            'category': category
        }
        
        await asyncio.to_thread(
            db.collection('places').document(content_id).collection('info').document('details').set,
            place_info,
            merge=True
        )
        
        # 2. 사용자별 북마크 저장 (모든 상세 정보 포함)
        user_bookmark_data = {
            'bookmark': bookmark,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'title': name,
            'contentid': content_id,
            # 상세 정보 추가
            'name': name,
            'desc': desc,
            'image': image,
            'region': region,
            'address': address,
            'detailAddress': detail_address,
            'contact': contact,
            'openingHours': opening_hours,
            'restDay': rest_day,
            'representativeMenu': representative_menu,
            'menu': menu,
            'eventStartDate': event_start_date,
            'eventEndDate': event_end_date,
            'eventIntro': event_intro,
            'eventContent': event_content,
            'inquiry': inquiry,
            'usageTime': usage_time,
            'performanceTime': performance_time,
            'duration': duration,
            'ageLimit': age_limit,
            'bookingPlace': booking_place,
            'discountInfo': discount_info,
            'eventGrade': event_grade,
            'status': status,
            'category': category
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

@router.post("/get_user_bookmarks")
async def get_user_bookmarks(request: Request):
    data = await request.json()
    uid = data.get('uid')
    if not uid:
        return JSONResponse(content={'success': False, 'error': 'Missing uid'}, status_code=400)
    try:
        user_bookmarks = await asyncio.to_thread(
            lambda: list(db.collection('users').document(uid).collection('bookmarks').where('bookmark', '==', True).stream())
        )
        
        bookmarks = []
        for bookmark_doc in user_bookmarks:
            content_id = bookmark_doc.id
            print(f"북마크 처리 중: content_id={content_id}")
            
            # 북마크 문서에서 직접 정보 가져오기
            bookmark_data = bookmark_doc.to_dict()
            print(f"북마크 데이터: {bookmark_data}")
            
            # 사용자의 리뷰 정보 가져오기
            user_review_doc = await asyncio.to_thread(
                db.collection('places').document(content_id).collection('reviews').document(uid).get
            )
            
            bookmark_info = {
                'contentId': content_id,
                'name': bookmark_data.get('name'),
                'desc': bookmark_data.get('desc'),
                'image': bookmark_data.get('image'),
                'region': bookmark_data.get('region', '전국'),
                'bookmark': True,
                'createdAt': bookmark_data.get('createdAt'),
                # 상세 정보 추가
                'address': bookmark_data.get('address'),
                'detailAddress': bookmark_data.get('detailAddress'),
                'contact': bookmark_data.get('contact'),
                'openingHours': bookmark_data.get('openingHours'),
                'restDay': bookmark_data.get('restDay'),
                'representativeMenu': bookmark_data.get('representativeMenu'),
                'menu': bookmark_data.get('menu'),
                'eventStartDate': bookmark_data.get('eventStartDate'),
                'eventEndDate': bookmark_data.get('eventEndDate'),
                'eventIntro': bookmark_data.get('eventIntro'),
                'eventContent': bookmark_data.get('eventContent'),
                'inquiry': bookmark_data.get('inquiry'),
                'usageTime': bookmark_data.get('usageTime'),
                'performanceTime': bookmark_data.get('performanceTime'),
                'duration': bookmark_data.get('duration'),
                'ageLimit': bookmark_data.get('ageLimit'),
                'bookingPlace': bookmark_data.get('bookingPlace'),
                'discountInfo': bookmark_data.get('discountInfo'),
                'eventGrade': bookmark_data.get('eventGrade'),
                'status': bookmark_data.get('status'),
                'category': bookmark_data.get('category')
            }
            
            # 리뷰 정보가 있으면 추가
            if user_review_doc.exists:
                review_data = user_review_doc.to_dict()
                bookmark_info.update({
                    'rating': review_data.get('rating', 0),
                    'review': review_data.get('review', ''),
                    'isPublic': review_data.get('isPublic', False)
                })
            else:
                bookmark_info.update({
                    'rating': 0,
                    'review': '',
                    'isPublic': False
                })
            
            bookmarks.append(bookmark_info)
        
        print(f"최종 북마크 개수: {len(bookmarks)}")
        return {'success': True, 'bookmarks': bookmarks}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/delete_user_bookmark")
async def delete_user_bookmark(request: Request):
    data = await request.json()
    uid = data.get('uid')
    content_id = data.get('contentId')
    if not uid or not content_id:
        return JSONResponse(content={'success': False, 'error': 'Missing uid or contentId'}, status_code=400)
    try:
        print(f"북마크 삭제 요청: uid={uid}, content_id={content_id}")
        
        # 1. 북마크 문서 가져오기
        bookmark_ref = db.collection('users').document(uid).collection('bookmarks').document(str(content_id))
        bookmark_doc = await asyncio.to_thread(bookmark_ref.get)
        
        if bookmark_doc.exists:
            bookmark_data = bookmark_doc.to_dict()
            print(f"북마크 데이터: {bookmark_data}")
            
            # 2. 북마크 완전 삭제
            await asyncio.to_thread(bookmark_ref.delete)
            print("북마크 삭제 완료")
        else:
            print("북마크 문서가 존재하지 않습니다")
            return JSONResponse(content={'success': False, 'error': 'Bookmark not found'}, status_code=404)
        
        # 3. 사용자별 리뷰 삭제
        user_review_ref = db.collection('users').document(uid).collection('reviews').document(content_id)
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
                if comment_data.get('uid') == uid:
                    await asyncio.to_thread(comment.reference.delete)
            print(f"사용자 댓글 삭제 완료")
            
            # 6. 관련 좋아요들 삭제
            likes = await asyncio.to_thread(
                lambda: list(db.collection('places').document(content_id).collection('likes').stream())
            )
            for like in likes:
                like_data = like.to_dict()
                if like_data.get('uid') == uid:
                    await asyncio.to_thread(like.reference.delete)
            print(f"사용자 좋아요 삭제 완료")
        else:
            print("삭제할 places 리뷰가 없습니다")
        
        print("북마크 및 관련 데이터 삭제 완료")
        return {'success': True}
    except Exception as e:
        print(f"북마크 삭제 오류: {str(e)}")
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/update_bookmark_rating")
async def update_bookmark_rating(request: Request):
    data = await request.json()
    uid = data.get('uid')
    content_id = data.get('contentId')
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
            await asyncio.to_thread(
                place_review_ref.update,
                {
                    'rating': rating,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
            )
        else:
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
                'contentId': content_id,
                'rating': rating,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            },
            merge=True
        )
        
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.post("/update_bookmark_visibility")
async def update_bookmark_visibility(request: Request):
    data = await request.json()
    uid = data.get('uid')
    content_id = data.get('contentId')
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
            await asyncio.to_thread(
                place_review_ref.update,
                {
                    'isPublic': is_public,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
            )
        else:
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
                'contentId': content_id,
                'isPublic': is_public,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            },
            merge=True
        )
        
        return {'success': True}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)

@router.get("/get_public_bookmarks")
async def get_public_bookmarks():
    """모든 사용자의 공개된 북마크들을 가져오는 API"""
    try:
        public_bookmarks = []
        
        users = await asyncio.to_thread(lambda: list(db.collection('users').stream()))
        
        for user in users:
            user_data = user.to_dict()
            user_name = user_data.get('name', 'Unknown')
            
            bookmarks = await asyncio.to_thread(
                lambda: list(user.reference.collection('bookmarks').where('isPublic', '==', True).stream())
            )
            
            for bookmark in bookmarks:
                bookmark_data = bookmark.to_dict()
                bookmark_data['userName'] = user_name
                bookmark_data['userId'] = user.id
                public_bookmarks.append(bookmark_data)
        
        public_bookmarks.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return {'success': True, 'bookmarks': public_bookmarks}
    except Exception as e:
        return JSONResponse(content={'success': False, 'error': str(e)}, status_code=500)