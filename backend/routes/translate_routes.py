from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter(prefix="/api/translate", tags=["translate"])

@router.post("/")
async def translate_text(request: dict):
    """
    텍스트를 번역하는 API
    """
    try:
        text = request.get("text", "")
        source_lang = request.get("source_lang", "auto")
        target_language = request.get("target_language", "ko")
        uid = request.get("uid", "system")
        
        if not text:
            raise HTTPException(status_code=400, detail="텍스트가 필요합니다")
        
        # 번역 서비스 API 호출
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:5001/translate",
                json={
                    "text": text,
                    "source_lang": source_lang,
                    "target_lang": target_language,
                    "uid": uid
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "translated_text": result.get("translated_text", text)
                }
            else:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"번역 서비스 오류: {response.status_code}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="번역 서비스 응답 시간 초과")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="번역 서비스에 연결할 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"번역 중 오류 발생: {str(e)}")
