from fastapi import APIRouter, HTTPException
import google.generativeai as genai
import dotenv
import os
import firebase_admin
from firebase_admin import firestore

# .env 파일 로드 - 여러 경로 시도
env_paths = [
    os.path.join(os.path.dirname(__file__), '..', '.env'),
]

for env_path in env_paths:
    if os.path.exists(env_path):
        dotenv.load_dotenv(env_path)
        print(f"LOG: .env 파일 로드됨: {env_path}")
        break
else:
    print("LOG: .env 파일을 찾을 수 없습니다. 환경 변수를 직접 설정해주세요.")

router = APIRouter(prefix="/api/gemini", tags=["gemini"])

@router.post("/translate")
async def translate_with_gemini(request: dict):
    """
    Gemini를 사용하여 텍스트를 번역하는 API
    """
    try:
        text = request.get("text", "")
        source_lang = request.get("source_lang", "ko")
        target_lang = request.get("target_lang", "en")
        
        if not text:
            raise HTTPException(status_code=400, detail="텍스트가 필요합니다")
        
        # Gemini API 키 설정
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # 환경 변수에서 가져오지 못한 경우 직접 설정
        if not gemini_api_key:
            gemini_api_key = "not use anymore"
            print("LOG: 환경 변수에서 API 키를 가져오지 못해 직접 설정된 키를 사용합니다.")
        
        print(f"LOG: Gemini API 키 확인: {'설정됨' if gemini_api_key else '설정되지 않음'}")
        
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="Gemini API 키가 설정되지 않았습니다")
        
        print(f"LOG: 번역 요청 - 원문: {text[:50]}..., 소스: {source_lang}, 타겟: {target_lang}")
        
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("LOG: Gemini 모델 초기화 성공")
        except Exception as e:
            print(f"LOG: Gemini 모델 초기화 실패: {e}")
            raise HTTPException(status_code=500, detail=f"Gemini 모델 초기화 실패: {str(e)}")
        
        # 언어 코드를 언어명으로 변환
        lang_map = {
            "ko": "한국어",
            "en": "영어", 
            "ja": "일본어",
            "zh": "중국어"
        }
        
        source_lang_name = lang_map.get(source_lang, source_lang)
        target_lang_name = lang_map.get(target_lang, target_lang)
        
        # 번역 프롬프트 생성
        prompt = f"""
        다음 {source_lang_name} 텍스트를 {target_lang_name}로 번역해주세요.
        HTML 태그나 마크다운 형식은 그대로 유지하고, 내용만 번역해주세요.
        번역된 텍스트만 반환해주세요.
        
        원문: {text}
        """
        
        print(f"LOG: 번역 요청 - 원문 길이: {len(text)}, 대상 언어: {target_lang_name}")
        
        try:
            response = model.generate_content(prompt)
            translated_text = response.text.strip()
            print(f"LOG: 번역 성공 - 번역된 텍스트 길이: {len(translated_text)}")
        except Exception as e:
            print(f"LOG: Gemini 번역 요청 실패: {e}")
            raise HTTPException(status_code=500, detail=f"Gemini 번역 요청 실패: {str(e)}")
        
        return {
            "success": True,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
    except Exception as e:
        print(f"LOG: 전체 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini 번역 중 오류 발생: {str(e)}")

@router.post("/save-translation")
async def save_translation(request: dict):
    """번역 결과를 기존 장소 데이터에 추가로 저장"""
    try:
        uid = request.get("uid")
        content_id = request.get("content_id")
        translated_content = request.get("translated_content", {})
        target_lang = request.get("target_lang", "en")
        region = request.get("region")
        category = request.get("category")
        
        if not all([uid, content_id, region, category]):
            raise HTTPException(status_code=400, detail="uid, content_id, region, category가 필요합니다")
        
        db = firestore.client()
        
        # 기존 장소 데이터 경로
        doc_ref = db.collection('api_data').document(target_lang).collection(region).document(category).collection('items').document(content_id)
        
        # 기존 데이터 조회
        doc = doc_ref.get()
        
        if doc.exists:
            # 기존 데이터 가져오기
            existing_data = doc.to_dict()
            
            # 번역된 내용을 기존 필드에 매핑하여 업데이트
            update_data = {
                "isTranslated": True,
                "translatedAt": firestore.SERVER_TIMESTAMP
            }
            
            # 번역된 내용을 기존 필드명에 매핑 (가게명 제외)
            field_mapping = {
                # 'title': 'title',  # 가게명은 번역하지 않음
                'address': 'addr1', 
                'summary': 'description',
                'detailInfo': 'description',  # 상세정보는 description 필드에
                'representativeMenu': 'firstmenu',
                'menu': 'treatmenu',
                'openingHours': 'opentimefood',
                'closedDays': 'restdatefood',
                'usageTime': 'opentimefood',  # 이용시간도 opentimefood에
                'restDate': 'restdatefood',
                'inquiry': 'infocenterfood',
                'contact': 'tel',
                'detailAddress': 'addr2'
            }
            
            # 번역된 내용을 기존 필드에 매핑하여 업데이트
            for translation_key, db_field in field_mapping.items():
                if translation_key in translated_content and translated_content[translation_key]:
                    update_data[db_field] = translated_content[translation_key]
            
            # 기존 데이터와 번역 데이터 병합
            doc_ref.update(update_data)
            
            print(f"LOG: 번역 결과 저장 완료 - content_id: {content_id}, target_lang: {target_lang}, region: {region}, category: {category}")
            
            return {"success": True, "message": "번역 결과가 저장되었습니다"}
        else:
            # 해당 언어로 데이터가 없는 경우 한국어 데이터를 복사하고 번역 추가
            ko_doc_ref = db.collection('api_data').document('ko').collection(region).document(category).collection('items').document(content_id)
            ko_doc = ko_doc_ref.get()
            
            if ko_doc.exists:
                ko_data = ko_doc.to_dict()
                
                # 한국어 데이터를 복사하고 번역 내용을 기존 필드에 매핑
                new_data = {
                    **ko_data,  # 기존 한국어 데이터
                    "isTranslated": True,
                    "translatedAt": firestore.SERVER_TIMESTAMP
                }
                
                # 번역된 내용을 기존 필드명에 매핑 (가게명 제외)
                field_mapping = {
                    # 'title': 'title',  # 가게명은 번역하지 않음
                    'address': 'addr1', 
                    'summary': 'description',
                    'detailInfo': 'description',
                    'representativeMenu': 'firstmenu',
                    'menu': 'treatmenu',
                    'openingHours': 'opentimefood',
                    'closedDays': 'restdatefood',
                    'usageTime': 'opentimefood',
                    'restDate': 'restdatefood',
                    'inquiry': 'infocenterfood',
                    'contact': 'tel',
                    'detailAddress': 'addr2'
                }
                
                # 번역된 내용을 기존 필드에 매핑하여 업데이트
                for translation_key, db_field in field_mapping.items():
                    if translation_key in translated_content and translated_content[translation_key]:
                        new_data[db_field] = translated_content[translation_key]
                
                doc_ref.set(new_data)
                
                print(f"LOG: 한국어 데이터 복사 후 번역 결과 저장 완료 - content_id: {content_id}, target_lang: {target_lang}")
                
                return {"success": True, "message": "번역 결과가 저장되었습니다"}
            else:
                raise HTTPException(status_code=404, detail="원본 데이터를 찾을 수 없습니다")
        
    except Exception as e:
        print(f"LOG: 번역 저장 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"번역 저장 중 오류 발생: {str(e)}")

@router.post("/get-translation-status")
async def get_translation_status(request: dict):
    """기존 장소 데이터에서 번역 상태 조회"""
    try:
        content_id = request.get("content_id")
        target_lang = request.get("target_lang", "en")
        region = request.get("region")
        category = request.get("category")
        
        if not all([content_id, region, category]):
            raise HTTPException(status_code=400, detail="content_id, region, category가 필요합니다")
        
        db = firestore.client()
        
        # 기존 장소 데이터에서 번역 상태 조회
        doc_ref = db.collection('api_data').document(target_lang).collection(region).document(category).collection('items').document(content_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            is_translated = data.get("isTranslated", False)
            
            # 번역된 내용 추출 (기존 필드에서)
            translated_content = {}
            if is_translated:
                # 기존 필드에서 번역된 내용 추출 (가게명 제외)
                field_mapping = {
                    # 'title': 'title',  # 가게명은 번역하지 않음
                    'address': 'addr1', 
                    'summary': 'description',
                    'detailInfo': 'description',
                    'representativeMenu': 'firstmenu',
                    'menu': 'treatmenu',
                    'openingHours': 'opentimefood',
                    'closedDays': 'restdatefood',
                    'usageTime': 'opentimefood',
                    'restDate': 'restdatefood',
                    'inquiry': 'infocenterfood',
                    'contact': 'tel',
                    'detailAddress': 'addr2'
                }
                
                # 기존 필드에서 번역된 내용 추출
                for translation_key, db_field in field_mapping.items():
                    if db_field in data and data[db_field]:
                        translated_content[translation_key] = data[db_field]
            
            return {
                "success": True,
                "isTranslated": is_translated,
                "translated_content": translated_content,
                "target_lang": target_lang
            }
        else:
            return {
                "success": True,
                "isTranslated": False,
                "translated_content": {},
                "target_lang": target_lang
            }
            
    except Exception as e:
        print(f"LOG: 번역 상태 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"번역 상태 조회 중 오류 발생: {str(e)}")
