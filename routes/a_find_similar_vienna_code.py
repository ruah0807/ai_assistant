import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import a_vienna_code.execute as vienna_ex
import a_similarity_code.execute as similarity_code



router = APIRouter(
    prefix="/find",
    tags=["Similarity Code & Vienna Code"]
)

class FindViennaCode(BaseModel):
    # brand_name: str 
    brand_image_url: str

class FindSimilarityCode(BaseModel):
    user_input: str

@router.post('/vienna_code', 
             name="비엔나 코드 찾는 Assistant",
             description="""
# 비엔나 코드 Assistant
```
이미지의 도형 모양을 파악 후, 비엔나 코드관련 문서를 검색하여 비엔나코드를 찾아주는 OPEN AI Assistant.
```
### 현재 업로드된 테스트 비엔나 코드

- 01 : 천체, 자연현상, 지도 
    - 0101** : 별, 해성
    - 0103** : 태양 
    - 0105** : 지구,지구본, 행성

### 요 청 
- brand_image_url: 해당상표의 이미지

### 응 답 
- 해당 이미지의 코드로 추정되는 비엔나 코드를 추천하는 Assistant의 메세지 (Json 파싱 필요) 

### 참고 사항
- 현존하는 데이터에 한해서는 검색 결과가 잘나오지만 
- 아직 비엔나코드의 모든 데이터가 들어와 있지 않은 상황이기때문에 명확한 답을 준다 표현하기 어렵습니다. 

            """ 
            )
async def find_vienna_code(request: FindViennaCode):
    start_time = time.time()
    
    messages = await vienna_ex.process_vienna_code(request.brand_image_url)
    
    end_time = time.time()
    total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time)%60:.2f}초"
    print(total_duration)

    return {"messages": messages, "ducation": total_duration}



@router.post('/similarity_code', 
             name="유사군 코드 찾는 Assistant",
             description="""
# 유사군 코드 Assistant
```
2024년 상품의명칭과류구분에관한고시(특허청고시제2023-26호)_전체목록_최종_시스템(출처표시) 문서를 기반으로하여 해당 유사코드를 추측하고 답변하는 similarityCode를 분석하는 OPEN AI Assistant.
```

### 현재 업로드된 테스트 비엔나 코드
- 2024년 상품의명칭과류구분에관한고시(특허청고시제2023-26호)_전체목록_최종_시스템(출처표시)
    - 24년 지정상품 고시목록(출처포함).md
    - 35-도매업.md
    - 35-소매업.md
    - 35-중개업.md
    - 35-판매대행업.md
    - 35-판매알선업.md

### 요 청 
- user_input: 유저 메세지

### 응 답 
- 해당 메세지의 유사군 코드로 추정되는 분류목록과 유사군코드를 응답하는 Assistant의 메세지 (json 파싱필요)

### 참고 사항
- 유사군코드의 목록이 한 파일당 약 5000개 이내이므로 총 35,000개의 목록을 전부 파악하지는 못하는듯합니다.
- 키워드 검색 방향으로 전환해야할 가능성이 있습니다.
"""
             )
async def find_similarity_code(request: FindSimilarityCode):
    start_time = time.time()
   
    messages = await similarity_code.similarity_code_finding_logic(request.user_input)

    end_time = time.time()
    total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time) %60:.2f}초"
    print(total_duration)

    return {"messages": messages, "ducation": total_duration}