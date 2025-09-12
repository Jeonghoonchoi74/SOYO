from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter(prefix="/api/recommend", tags=["recommend"])

@router.post("/search")
async def search_recommendations(request: dict):
    """
    추천 검색 API
    """
    try:
        uid = request.get("uid")
        query = request.get("query", "")
        region = request.get("region")
        category = request.get("category")
        
        if not uid:
            raise HTTPException(status_code=400, detail="사용자 ID가 필요합니다")
        
        if not query:
            raise HTTPException(status_code=400, detail="검색 쿼리가 필요합니다")
        
        # 추천 서비스 API 호출
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:5002/search",
                json={
                    "uid": uid,
                    "query": query,
                    "region": region,
                    "category": category
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "data": result
                }
            else:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"추천 서비스 오류: {response.status_code}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="추천 서비스 응답 시간 초과")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="추천 서비스에 연결할 수 없습니다")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 검색 중 오류 발생: {str(e)}")
