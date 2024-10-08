import routes.pipeline_common as p_common
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

class CombinedSearchRequest(BaseModel):
    brand_name: str
    brand_image_url: str
    similarity_code: Optional[str] = None
    vienna_code: Optional[str] = None
    num_of_rows: int = 5
    only_null_vienna_search: bool = False
    filter: bool = False


# FastAPI 애플리케이션 생성
app = APIRouter()

# 라우터 설정
router = APIRouter(
    prefix="/pipeline",  # 엔드포인트 앞에 붙을 공통 URL
    tags=["Similarity Pipeline"]
)


@router.post("/opinion", name="의견서 작성 전체 파이프라인")
async def similarity_opinion_api(request: CombinedSearchRequest):
    try:
        messages= await p_common.similarity_pipeline(request.brand_name, 
                                            request.brand_image_url, 
                                            request.similarity_code,
                                            request.vienna_code,
                                            request.num_of_rows,
                                            request.only_null_vienna_search,
                                            request.filter, 
                                            format = "opinion")
        return messages
    except ValueError as e:
        print(f"Error : {str(e)}")
        raise HTTPException(status_code=500, detail = str(e))




@router.post("/report", name="유사도 보고서 작성 전체 파이프라인")
async def similarity_report_api(request: CombinedSearchRequest):
    try:
        messages= await p_common.similarity_pipeline(request.brand_name, 
                                            request.brand_image_url, 
                                            request.similarity_code,
                                            request.vienna_code,
                                            request.num_of_rows,
                                            request.only_null_vienna_search,
                                            request.filter,
                                            format = "report")
        return messages
    except ValueError as e:
        print(f"Error : {str(e)}")
        raise HTTPException(status_code=500, detail = str(e))

