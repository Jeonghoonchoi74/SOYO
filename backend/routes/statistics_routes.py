from fastapi import APIRouter
from fastapi.responses import JSONResponse
import asyncio
from config.database import get_db

router = APIRouter(prefix="/api", tags=["statistics"])
db = get_db()

@router.get("/get_statistics")
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

@router.get("/get_regions")
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

@router.get("/data")
async def get_data():
    return {'message': '안녕하세요, FastAPI에서 보낸 데이터입니다!'}