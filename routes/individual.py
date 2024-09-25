import json, time
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from brand_discernment.mes import discernment_create_thread_and_run
from brand_similarity.mes import similarity_create_thread_and_run
from similar_img import mes_img
from similar_text import mes_text
import kipris_api, similar, save_file, init, common


router = APIRouter(
    prefix="/individual",
    tags=["파이프라인 분리"]
)

class SearchKipris(BaseModel):
    similar_words : List[str] = [""]
    similarity_code: str = ""
    vienna_code: str = ""
    num_of_rows: int = 5

@router.post("/similar-words", name="비슷한 상표명 찾기")
async def get_similar_words(brand_name: str, brand_image_url: str):
    if not brand_name and brand_image_url:
        raise HTTPException(status_code=400, detail="상표명을 입력하세요")
    
    # LLM 유사 단어 목록 만들기
    similar_words = similar.generate_similar_barnd_names(brand_name)

    if not similar_words:
        raise HTTPException(status_code=404, detail="비슷한 단어를 찾을 수 없습니다.")
    
    return {"similar_words": similar_words}


@router.post("/search-kipris", name="KIPRIS 유사 상표 찾기", description="찾고자 하는 유사상표명(List)와 유사코드, 비엔나 코드를 입력하세요")
async def search_kipris(request: SearchKipris):
    if not request.similar_words:
        raise HTTPException(status_code=400, detail="검색할 단어 목록을 입력하세요")
    
    # KIPRIS 검색 수행
    result_data = await kipris_api.search_and_save_all_results(request.similar_words, request.similarity_code, request.vienna_code, request.num_of_rows)

    return {"result_data" : result_data}
