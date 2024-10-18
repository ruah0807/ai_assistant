from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import a_create_names.create_names as create_names
import kipris.kipris_control as kipris_control



router = APIRouter(
    prefix="/individual",
    tags=["유사코드 찾기 & 비슷한 상표명 생성 & KIPRIS검색"]
)

class SearchKipris(BaseModel):
    words : List[str] = [""]
    similarity_code: Optional[str] = ""
    vienna_code: Optional[str] = ""
    num_of_rows: int = 5
    exclude_application_number: Optional[str] = "" # 예외처리 할 출원번호
    exclude_registration_number: Optional[str] = "" #예외처리 할 등록 번호
    application_date: Optional[str] = "" # 예외처리할 출원일 형식(YYYYMMDD)
    only_null_vienna_search: bool = False  # 비엔나값이 null 값인 것만 추가하고 싶을때 True로 변경한다. 


@router.post("/similar-words", name="비슷한 상표명 찾기",
             description="""
# 비슷한 상표명을 찾아주는 LLM
```
KIPRIS 검색 전, 상표명의 비슷한 검색어를 찾아주는 API
```
### 요 청 
- brand_name: 해당상표의 이미지
- asign_product_description : 지정상품 주요부 판단을위한 유사군 설명
### 응 답 (Json 파싱) 
- description_word :지정상품 유사군으로 추정되는 "일반 명사" - 해당부분을 나눈 이유는 LLM이 일반명사와 아닌것을 한번 더 확실히 구분하게 하기 위함입니다. 
- words : 해당 상표명과 비슷한 상표명들
### 참고 사항
- LLM 특성상 검색을 할때마다 다른결과를 가져오기 때문에 여러번 검색이 가능합니다.
- 한번에 마음에 드는 결과를 얻을수 없는 경우 여러번 검색하여 답을 얻습니다.
- 한 글자 검색은 검색어에 포함하지 않도록 하였습니다.
- 영어와 한글을 번갈아가며 검색어에 추가하도록 하였습니다.
            """ 
             )
async def get_similar_words(brand_name: str, asign_product_description: str):
    if not brand_name :
        raise HTTPException(status_code=400, detail="상표명을 입력하세요")
    elif not asign_product_description :
        raise HTTPException(status_code=400, detail="지정상품 주요부 판별을 위해 유사군을 입력하세요")
    
    # LLM 유사 단어 목록 만들기
    similar_words = create_names.generate_similar_barnd_names(brand_name, asign_product_description)

    if not similar_words:
        raise HTTPException(status_code=404, detail="비슷한 단어를 찾을 수 없습니다.")
    
    return similar_words




@router.post("/search-kipris", name="KIPRIS 유사 상표 찾기",
             description="""
# KIPRIS 유사 상표 찾기
```
비슷한 상표명을 찾은 이후, 원하는 검색어를 골라 similar_words에 입력합니다.
이미지의 도형 모양을 파악하고, 비엔나 코드관련 문서를 검색하여 비엔나코드를 찾아주는 OPEN AI Assistant.
```
### 요 청 
- **words** : 비슷한 상표명 검색어 (LIST or 단일 or "")
- **similarity_code** : 해당 유사코드
- **vienna_code** : 비엔나코드("" 가능)
- **num_of_rows** : 각 상표명마다 받고 싶은 검색 수(기본값: 5) 
- **only_null_vienna_search** : 텍스트 위주의 상표명(예: mindshare, 시민언론시선) 일때, 비엔나코드가 null 값인 것만 검색하고 싶다면 true로 변경합니다.(기본값: false)
### 테스트를 위한 요청 
- **exclude_application_number** : 제외하고 싶은 출원번호 (str)
- **exclude_registration_number** : 제외하고 싶은 등록번호 (str)
- **application_date** : 원하는 날짜 이전에 등록된 상표들만 출력 (str) 
### 응 답 
- 검색된 키프리스의 응답을 **title, classification_code, similar_image_url, application_number, vienna_code** 로 필터링되어 LIST로 반환됩니다.
### 참고 사항
- 유사코드를 제외한 각 검색은 상표명, 비엔나코드는 빈값이 검색가능합니다.
- only_null_vienna_search : true - 텍스트위주의 상표일경우 vienna_code가 null 값인것만 선택적으로 받을수 있습니다.
- only_null_vienna_search : false - 도형위주의 상표이거나, 텍스트위주라도 도형관계없이 받고싶다면 false로 검색합니다.
            """ 
             )
async def search_kipris(request: SearchKipris):
    if not request.words:
        raise HTTPException(status_code=400, detail="검색할 단어 목록을 입력하세요")
    
    # KIPRIS 검색 수행
    result_data = await kipris_control.search_and_save_all_results(
        request.words, request.similarity_code, request.vienna_code, request.num_of_rows, request.only_null_vienna_search,
        request.exclude_application_number, request.exclude_registration_number, request.application_date)

    if not result_data:
        raise HTTPException(status_code=404, detail ="검색된 데이터가 없습니다.")

    return {"kipris_data":result_data}

