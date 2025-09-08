from fastapi import APIRouter, HTTPException
import requests
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

router = APIRouter(prefix="/api/finetuned-ai", tags=["finetuned-ai"])

# Finetuned AI 서버 설정
FINETUNED_AI_BASE_URL = "http://localhost:5001"

@router.post("/translate")
async def translate_with_finetuned_ai(request: dict):
    """
    Finetuned AI를 사용하여 텍스트를 번역하는 API
    """
    try:
        text = request.get("text", "")
        source_lang = request.get("source_lang", "ko")
        target_lang = request.get("target_lang", "en")
        uid = request.get("uid", "test_user")  # 5001 포트 서버에서 요구하는 uid 필드
        
        print(f"LOG: [FINETUNED AI] 번역 요청 수신")
        print(f"LOG: [FINETUNED AI] 요청 데이터: {request}")
        print(f"LOG: [FINETUNED AI] 원문 길이: {len(text)}, 소스 언어: {source_lang}, 타겟 언어: {target_lang}")
        print(f"LOG: [FINETUNED AI] 원문 내용: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"LOG: [FINETUNED AI] 사용자 ID: {uid}")
        
        if not text:
            print("LOG: [FINETUNED AI] 오류: 텍스트가 비어있음")
            raise HTTPException(status_code=400, detail="텍스트가 필요합니다")
        
        # Finetuned AI 서버로 요청 (5001 포트 서버 스펙에 맞게 uid 포함)
        payload = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "uid": uid
        }
        
        print(f"LOG: [FINETUNED AI] 5001 포트 서버로 요청 전송: {FINETUNED_AI_BASE_URL}/translate")
        print(f"LOG: [FINETUNED AI] 요청 페이로드: {payload}")
        
        try:
            response = requests.post(
                f"{FINETUNED_AI_BASE_URL}/translate",
                json=payload,
                timeout=30
            )
            
            print(f"LOG: [FINETUNED AI] 서버 응답 상태 코드: {response.status_code}")
            print(f"LOG: [FINETUNED AI] 서버 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            
            result = response.json()
            translated_text = result.get("translated_text", "")
            
            print(f"LOG: [FINETUNED AI] 서버 응답 데이터: {result}")
            print(f"LOG: [FINETUNED AI] 번역 성공 - 번역된 텍스트 길이: {len(translated_text)}")
            print(f"LOG: [FINETUNED AI] 번역 결과: {translated_text[:100]}{'...' if len(translated_text) > 100 else ''}")
            
        except requests.exceptions.ConnectionError:
            print("LOG: [FINETUNED AI] 서버 연결 실패 - 5001 포트 서버가 실행 중인지 확인하세요")
            raise HTTPException(status_code=503, detail="Finetuned AI 서버에 연결할 수 없습니다. 5001 포트 서버가 실행 중인지 확인하세요.")
        except requests.exceptions.Timeout:
            print("LOG: [FINETUNED AI] 서버 응답 시간 초과 (30초)")
            raise HTTPException(status_code=504, detail="Finetuned AI 서버 응답 시간이 초과되었습니다")
        except requests.exceptions.HTTPError as e:
            print(f"LOG: [FINETUNED AI] 서버 HTTP 오류: {e}")
            print(f"LOG: [FINETUNED AI] 응답 내용: {response.text if 'response' in locals() else '응답 없음'}")
            raise HTTPException(status_code=502, detail=f"Finetuned AI 서버 오류: {str(e)}")
        except Exception as e:
            print(f"LOG: [FINETUNED AI] 요청 실패: {e}")
            raise HTTPException(status_code=500, detail=f"Finetuned AI 요청 실패: {str(e)}")
        
        print(f"LOG: [FINETUNED AI] 번역 완료 - 최종 응답 반환")
        return {
            "success": True,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
    except Exception as e:
        print(f"LOG: [FINETUNED AI] 전체 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Finetuned AI 번역 중 오류 발생: {str(e)}")

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
        
        print(f"LOG: [FINETUNED AI] 번역 저장 요청 수신")
        print(f"LOG: [FINETUNED AI] 요청 데이터: {request}")
        print(f"LOG: [FINETUNED AI] 저장 대상 - content_id: {content_id}, target_lang: {target_lang}, region: {region}, category: {category}")
        print(f"LOG: [FINETUNED AI] 번역된 내용 필드 수: {len(translated_content)}")
        
        if not all([uid, content_id, region, category]):
            print(f"LOG: [FINETUNED AI] 오류: 필수 파라미터 누락 - uid: {uid}, content_id: {content_id}, region: {region}, category: {category}")
            raise HTTPException(status_code=400, detail="uid, content_id, region, category가 필요합니다")
        
        db = firestore.client()
        
        # 기존 장소 데이터 경로
        doc_ref = db.collection('api_data').document(target_lang).collection(region).document(category).collection('items').document(content_id)
        
        print(f"LOG: [FINETUNED AI] Firebase 문서 경로: api_data/{target_lang}/{region}/{category}/items/{content_id}")
        
        # 기존 데이터 조회
        doc = doc_ref.get()
        
        if doc.exists:
            print(f"LOG: [FINETUNED AI] 기존 문서 발견 - 업데이트 모드")
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
            
            print(f"LOG: [FINETUNED AI] 번역 결과 저장 완료 - content_id: {content_id}, target_lang: {target_lang}, region: {region}, category: {category}")
            print(f"LOG: [FINETUNED AI] 업데이트된 필드 수: {len(update_data)}")
            
            return {"success": True, "message": "번역 결과가 저장되었습니다"}
        else:
            print(f"LOG: [FINETUNED AI] 기존 문서 없음 - 한국어 데이터 복사 모드")
            # 해당 언어로 데이터가 없는 경우 한국어 데이터를 복사하고 번역 추가
            ko_doc_ref = db.collection('api_data').document('ko').collection(region).document(category).collection('items').document(content_id)
            ko_doc = ko_doc_ref.get()
            
            if ko_doc.exists:
                print(f"LOG: [FINETUNED AI] 한국어 원본 데이터 발견 - 복사 후 번역 적용")
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
        print(f"LOG: [FINETUNED AI] 번역 저장 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"번역 저장 중 오류 발생: {str(e)}")

@router.post("/get-translation-status")
async def get_translation_status(request: dict):
    """기존 장소 데이터에서 번역 상태 조회"""
    try:
        content_id = request.get("content_id")
        target_lang = request.get("target_lang", "en")
        region = request.get("region")
        category = request.get("category")
        
        print(f"LOG: [FINETUNED AI] 번역 상태 조회 요청 수신")
        print(f"LOG: [FINETUNED AI] 요청 데이터: {request}")
        print(f"LOG: [FINETUNED AI] 조회 대상 - content_id: {content_id}, target_lang: {target_lang}, region: {region}, category: {category}")
        
        if not all([content_id, region, category]):
            print(f"LOG: [FINETUNED AI] 오류: 필수 파라미터 누락 - content_id: {content_id}, region: {region}, category: {category}")
            raise HTTPException(status_code=400, detail="content_id, region, category가 필요합니다")
        
        db = firestore.client()
        
        # 기존 장소 데이터에서 번역 상태 조회
        doc_ref = db.collection('api_data').document(target_lang).collection(region).document(category).collection('items').document(content_id)
        
        print(f"LOG: [FINETUNED AI] Firebase 문서 경로: api_data/{target_lang}/{region}/{category}/items/{content_id}")
        
        doc = doc_ref.get()
        
        if doc.exists:
            print(f"LOG: [FINETUNED AI] 문서 발견 - 번역 상태 확인")
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
            
            print(f"LOG: [FINETUNED AI] 번역 상태 조회 완료 - isTranslated: {is_translated}, 번역된 필드 수: {len(translated_content)}")
            
            return {
                "success": True,
                "isTranslated": is_translated,
                "translated_content": translated_content,
                "target_lang": target_lang
            }
        else:
            print(f"LOG: [FINETUNED AI] 문서 없음 - 번역되지 않음")
            return {
                "success": True,
                "isTranslated": False,
                "translated_content": {},
                "target_lang": target_lang
            }
            
    except Exception as e:
        print(f"LOG: [FINETUNED AI] 번역 상태 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"번역 상태 조회 중 오류 발생: {str(e)}")

@router.get("/health")
async def health_check():
    """Finetuned AI 서버 상태 확인"""
    try:
        print(f"LOG: [FINETUNED AI] Health Check 요청 수신")
        print(f"LOG: [FINETUNED AI] 5001 포트 서버 상태 확인: {FINETUNED_AI_BASE_URL}/health")
        
        response = requests.get(f"{FINETUNED_AI_BASE_URL}/health", timeout=5)
        
        print(f"LOG: [FINETUNED AI] Health Check 응답 상태 코드: {response.status_code}")
        print(f"LOG: [FINETUNED AI] Health Check 응답 헤더: {dict(response.headers)}")
        
        response.raise_for_status()
        
        response_data = response.json()
        print(f"LOG: [FINETUNED AI] Health Check 응답 데이터: {response_data}")
        print(f"LOG: [FINETUNED AI] 서버 상태: 정상")
        
        return {
            "success": True,
            "message": "Finetuned AI 서버가 정상적으로 실행 중입니다",
            "status": "healthy"
        }
    except requests.exceptions.ConnectionError:
        print(f"LOG: [FINETUNED AI] Health Check 실패: 서버 연결 불가")
        print(f"LOG: [FINETUNED AI] 5001 포트 서버가 실행 중인지 확인하세요")
        return {
            "success": False,
            "message": "Finetuned AI 서버에 연결할 수 없습니다. 5001 포트 서버가 실행 중인지 확인하세요.",
            "status": "unhealthy"
        }
    except Exception as e:
        print(f"LOG: [FINETUNED AI] Health Check 오류: {str(e)}")
        return {
            "success": False,
            "message": f"Finetuned AI 서버 상태 확인 중 오류: {str(e)}",
            "status": "error"
        }
