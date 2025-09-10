from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
import os

router = APIRouter(prefix="/api/firebase", tags=["firebase"])

@router.post("/get-user-language")
async def get_user_language(request: dict):
    """
    사용자 언어 설정 조회
    """
    try:
        uid = request.get("uid")
        
        if not uid:
            raise HTTPException(status_code=400, detail="사용자 ID가 필요합니다")
        
        db = firestore.client()
        user_doc = db.collection('users').document(uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            user_language = user_data.get('lang', 'ko')
            return {
                "success": True,
                "language": user_language
            }
        else:
            return {
                "success": True,
                "language": "ko"  # 기본값
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 언어 조회 중 오류 발생: {str(e)}")

@router.post("/get-firebase-data")
async def get_firebase_data(request: dict):
    """
    Firebase에서 상세 데이터 가져오기
    """
    try:
        content_id = request.get("contentId")
        region = request.get("region")
        category = request.get("category")
        user_language = request.get("userLanguage", "ko")
        
        if not all([content_id, region, category]):
            raise HTTPException(status_code=400, detail="필수 파라미터가 누락되었습니다")
        
        db = firestore.client()
        
        # 모든 카테고리에서 사용자 언어로 조회
        search_lang = user_language
        
        # 1. 적절한 언어로 먼저 시도
        doc_ref = db.collection('api_data').document(search_lang).collection(region).document(category).collection('items')
        query = doc_ref.where('contentid', '==', content_id)
        docs = query.get()
        
        if docs:
            doc = docs[0]
            data = doc.to_dict()
            
            # DB 경로 생성
            db_path = f"api_data/{search_lang}/{region}/{category}/items/{content_id}"
            
            # 언어별 필드 매핑
            mapped_data = map_language_fields(data, user_language, db_path)
            
            return {
                "success": True,
                "data": mapped_data
            }
        else:
            # 2. 한국어로 폴백 시도
            if search_lang != 'ko':
                doc_ref = db.collection('api_data').document('ko').collection(region).document(category).collection('items')
                query = doc_ref.where('contentid', '==', content_id)
                docs = query.get()
                
                if docs:
                    doc = docs[0]
                    data = doc.to_dict()
                    
                    db_path = f"api_data/ko/{region}/{category}/items/{content_id}"
                    mapped_data = map_language_fields(data, 'ko', db_path)
                    
                    return {
                        "success": True,
                        "data": mapped_data
                    }
            
            # 3. 크로스 카테고리 검색 제거됨 - 모든 카테고리에서 사용자 언어별 DB 구축 완료
            
            # 데이터가 없는 경우 기본 정보 반환
            return {
                "success": True,
                "data": {
                    "contentid": content_id,
                    "displayTitle": f"장소 {content_id}",
                    "displayAddress": f"{region} {category}",
                    "displaySummary": "상세 정보를 불러올 수 없습니다.",
                    "title": f"장소 {content_id}",
                    "addr1": f"{region} {category}",
                    "overview": "상세 정보를 불러올 수 없습니다.",
                    "keywords": [],
                    "dbReference": f"api_data/ko/{region}/{category}/items/{content_id}"
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase 데이터 조회 중 오류 발생: {str(e)}")

@router.post("/get-recommend-places")
async def get_recommend_places(request: dict):
    """
    Firebase에서 추천 장소 데이터 가져오기
    """
    try:
        region = request.get("region")
        category = request.get("category")
        user_language = request.get("userLanguage", "ko")
        
        if not all([region, category]):
            raise HTTPException(status_code=400, detail="지역과 카테고리가 필요합니다")
        
        db = firestore.client()
        
        # 모든 카테고리에서 사용자 언어로 조회
        search_lang = user_language
        
        # Firebase에서 해당 지역의 데이터 가져오기
        collection_ref = db.collection('api_data').document(search_lang).collection(region).document(category).collection('items')
        docs = collection_ref.get()
        
        places = []
        for doc in docs:
            data = doc.to_dict()
            # DB 경로 생성
            db_path = f"api_data/{search_lang}/{region}/{category}/items/{doc.id}"
            # 언어별 필드 매핑 적용
            mapped_data = map_language_fields(data, user_language, db_path)
            places.append(mapped_data)
        
        return {
            "success": True,
            "data": places
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 장소 데이터 조회 중 오류 발생: {str(e)}")

def map_language_fields(data, lang, db_path=""):
    """
    언어별 필드 매핑 함수
    """
    if lang == 'ko':
        # 한국어: 기본 필드 사용
        return {
            **data,
            "displayTitle": data.get("title", ""),
            "displayAddress": data.get("addr1", ""),
            "displaySummary": data.get("overview", ""),
            "keywords": data.get("keywords", []),
            "dbReference": db_path
        }
    else:
        # 다국어: 번역된 필드 사용 (번역된 가게명과 원본 제목 포함)
        return {
            **data,
            "displayTitle": data.get("title", ""),  # 번역된 제목 (title 필드가 번역된 내용으로 대체됨)
            "original_title": data.get("original_title", ""),  # 원본 제목
            "displayAddress": data.get("translated_addr") or data.get("addr1", ""),
            "displaySummary": data.get("translated_summary") or data.get("overview", ""),
            # 번역된 메뉴 정보들
            "firstmenu": data.get("translated_firstmenu") or data.get("firstmenu", ""),
            "treatmenu": data.get("translated_treatmenu") or data.get("treatmenu", ""),
            "opentimefood": data.get("translated_opentimefood") or data.get("opentimefood", ""),
            "restdatefood": data.get("translated_restdatefood") or data.get("restdatefood", ""),
            "usetime": data.get("translated_usetime") or data.get("usetime", ""),
            "restdate": data.get("translated_restdate") or data.get("restdate", ""),
            "infocenter": data.get("translated_infocenter") or data.get("infocenter", ""),
            "tel": data.get("translated_tel") or data.get("tel", ""),
            "addr1": data.get("translated_addr") or data.get("addr1", ""),
            "addr2": data.get("translated_addr2") or data.get("addr2", ""),
            "keywords": data.get("keywords", []),
            "dbReference": db_path
        }
