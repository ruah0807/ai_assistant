import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import a_vienna_code.execute as vienna_ex
import a_similarity_code.execute as similarity_code




router = APIRouter(
    prefix="/individual",
    tags=["유사코드 찾기 & 비슷한 상표명 생성 & KIPRIS검색"]
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
이미지의 도형 모양을 파악하는 AI Assistant.
```


### 요 청 
- brand_image_url: 해당상표의 이미지

### 응 답 
- 해당 이미지의 도형으로 추정되는 도형 설명을 찾아 응답. (Json 파싱 필요) 

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

    return {"results":messages, "total_duration": total_duration}



@router.post('/similarity-code', 
             name="유사군 코드 찾는 Assistant",
             description="""
# 유사군 코드 Assistant
```
문서를 기반으로하여 해당 유사코드를 추측하고 답변하는 similarityCode를 분석하는 OPEN AI Assistant.
```

### 현재 업로드된 문서
- trademark_class.md

### 요 청 
- user_input: 유저 메세지

### 응 답 
- 해당 메세지의 유사군 코드로 추정되는 분류목록과 유사군코드를 응답하는 Assistant의 메세지 

### 참고 사항
- 키워드 검색 방향으로 전환해야할 가능성이 있습니다.
"""
             )
async def find_similarity_code(request: FindSimilarityCode):
    start_time = time.time()
   
    messages= await similarity_code.similarity_code_finding_logic(request.user_input)

    end_time = time.time()
    total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time) %60:.2f}초"
    print(total_duration)

    return {"results": messages, "total_duration": total_duration}