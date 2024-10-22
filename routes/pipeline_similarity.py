import routes.pipeline_common as p_common
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import time

class CombinedSearchRequest(BaseModel):
    brand_name: str
    brand_description: str 
    request_similarity_code: Optional[str] = None
    brand_image_url: str
    num_of_rows: int = 5
    only_null_vienna_search: bool = False
    filter: bool = False
    exclude_application_number: Optional[str] = ""
    exclude_registration_number: Optional[str] = ""
    application_date: Optional[str] = ""


# FastAPI 애플리케이션 생성
app = APIRouter()

# 라우터 설정
router = APIRouter(
    prefix="/pipeline",  # 엔드포인트 앞에 붙을 공통 URL
    tags=["유사도 전체 파이프라인"]
)


@router.post("/opinion", name="의견서 작성 전체 파이프라인", description="""

## 의견서 작성 파이프라인 로직        
1단계 : 비슷한 상표명 생성\n
2단계 : 유사코드 생성\n
3단계 : 비엔나 코드 생성\n
4단계 : 키프리스 검색\n
4.5단계 : 필터링 ( 제외가능 )\n
5단계 : 의견서 작성\n

## 요청 
- **brand_name**: "등록하고자하는 상표이름" 
- **brand_description**: "LLM의 주요부 판별을 위한 브랜드 설명"
- **request_similarity_code**: "유사코드 생성을 위한 request"
- **brand_image_url**: "준비되어있는 상표 이미지 URL"
- **num_of_rows**: (**int** : 5) 각 검색어당 받고자하는 결과 (0~?개) - 검색어가 몇개인가에 따라 달라집니다.
- **only_null_vienna_search**: (**bool**: false OR true) 비엔나코드가 null값인 것만 받고자 할때는 true (기본값 false)
- **filter**: (**bool**: false OR true) 검색결과가 너무 많다 판달될경우 쓰일 중간 필터
---
- **exclude_application_number**: "제외할 출원 번호"
- **exclude_registration_number**: "제외할 등록 번호"
- **application_date**:  "원하는 날짜 이전의 출원 등록 상표들만 도출"
             

## 참고사항                  
- only_null_vienna_search 을 true로 변경할 경우 : 비엔나코드를 생성하지 않음과 동시에 비엔나 코드가 null 값이 것들만 반환하여 의견서를 작성합니다. - 텍스트로만 이루어진 상표일경우 true로 변경
""")
async def similarity_opinion_api(request: CombinedSearchRequest):
    try:
        start_time = time.time()
        messages= await p_common.similarity_pipeline(request.brand_name, 
                                            request.brand_description,
                                            request.request_similarity_code,
                                            request.brand_image_url, 
                                            request.num_of_rows,
                                            request.only_null_vienna_search,
                                            request.filter,
                                            request.exclude_application_number, 
                                            request.exclude_registration_number, 
                                            request.application_date,
                                            format_type = "opinion")
        end_time = time.time()
        total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time)%60:.2f}초"
        print(total_duration)

        return {"results":messages, "total_duration": total_duration}
    except ValueError as e:
        print(f"Error : {str(e)}")
        raise HTTPException(status_code=500, detail = str(e))




@router.post("/report", name="유사도 보고서 작성 전체 파이프라인", description="""
             
## 유사 보고서 작성 파이프라인 로직        
1단계 : 비슷한 상표명 생성\n
2단계 : 유사코드 생성\n
3단계 : 비엔나 코드 생성\n
4단계 : 키프리스 검색\n
4.5단계 : 필터링 ( 제외가능 )\n
5단계 : 보고서 작성\n

## 요청 
- **brand_name**: "등록하고자하는 상표이름" 
- **brand_description**: "LLM의 주요부 판별을 위한 브랜드 설명"
- **request_similarity_code**: "유사코드 생성을 위한 request"
- **brand_image_url**: "준비되어있는 상표 이미지 URL"
- **num_of_rows**: (**int** : 5) 각 검색어당 받고자하는 결과 (0~?개) - 검색어가 몇개인가에 따라 달라집니다.
- **only_null_vienna_search**: (**bool**: false OR true) 비엔나코드가 null값인 것만 받고자 할때는 true (기본값 false)
- **filter**: (**bool**: false OR true) 검색결과가 너무 많다 판달될경우 쓰일 중간 필터
---
- **exclude_application_number**: "제외할 출원 번호"
- **exclude_registration_number**: "제외할 등록 번호"
- **application_date**:  "원하는 날짜 이전의 출원 등록 상표들만 도출"

## 참고사항                  
- only_null_vienna_search 을 true로 변경할 경우 : 비엔나코드를 생성하지 않음과 동시에 비엔나 코드가 null 값이 것들만 평가하여 보고서를 작성합니다. - 텍스트로만 이루어진 상표일경우 true로 변경
""")
async def similarity_report_api(request: CombinedSearchRequest):
    try:
        start_time = time.time()
        messages= await p_common.similarity_pipeline(request.brand_name, 
                                            request.brand_description,
                                            request.request_similarity_code,
                                            request.brand_image_url, 
                                            request.num_of_rows,
                                            request.only_null_vienna_search,
                                            request.filter,
                                            request.exclude_application_number, 
                                            request.exclude_registration_number, 
                                            request.application_date,
                                            format_type = "report")
        end_time = time.time()
        total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time)%60:.2f}초"
        print(total_duration)

        return {"results":messages, "total_duration": total_duration}
    except ValueError as e:
        print(f"Error : {str(e)}")
        raise HTTPException(status_code=500, detail = str(e))

