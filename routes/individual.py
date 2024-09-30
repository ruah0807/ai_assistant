from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import kipris_control, similar


router = APIRouter(
    prefix="/individual",
    tags=["SimilarWords & KIPRIS"]
)

class SearchKipris(BaseModel):
    words : List[str] = [""]
    similarity_code: Optional[str] = None
    vienna_code: Optional[str] = None
    num_of_rows: int = 5
    only_null_vienna_search: bool = False  # 비엔나값이 null 값인 것만 추가하고 싶을때 True로 변경한다. 


@router.post("/similar-words", name="비슷한 상표명 찾기")
async def get_similar_words(brand_name: str):
    if not brand_name :
        raise HTTPException(status_code=400, detail="상표명을 입력하세요")
    
    # LLM 유사 단어 목록 만들기
    similar_words = similar.generate_similar_barnd_names(brand_name)

    if not similar_words:
        raise HTTPException(status_code=404, detail="비슷한 단어를 찾을 수 없습니다.")
    
    return similar_words


@router.post("/search-kipris", name="KIPRIS 유사 상표 찾기", description="찾고자 하는 유사상표명(List)와 유사코드, 비엔나 코드 각 상표명마다 받고싶은 검색 수를 입력하세요")
async def search_kipris(request: SearchKipris):
    if not request.words:
        raise HTTPException(status_code=400, detail="검색할 단어 목록을 입력하세요")
    
    # KIPRIS 검색 수행
    result_data = await kipris_control.search_and_save_all_results(request.words, request.similarity_code, request.vienna_code, request.num_of_rows, request.only_null_vienna_search)

    if not result_data:
        raise HTTPException(status_code=404, detail ="검색된 데이터가 없습니다.")

    return result_data

