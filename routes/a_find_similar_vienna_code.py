import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import a_vienna_code.execute as vienna_ex
import a_reject_enable.execute as rejection
import a_similarity_code.execute as similarity_code




router = APIRouter(
    prefix="/individual",
    tags=["유사코드 찾기 & 비슷한 상표명 생성 & KIPRIS검색"]
)

class FindViennaCode(BaseModel):
    brand_image_url: str

class FindSimilarityCode(BaseModel):
    request_similarity_code: str



@router.post('/rejection', 
             name="등록 거절 상표 판단 Assistant ",
             description="""
# 상표의 거절 가능성 판단 Assistant 
```
이미지의 상표 등록 가능 여부를 판단
```
### 요 청 
- brand_image_url: 해당상표의 이미지 URL
### 응 답 
- **refused** : 거절 - true / 그렇지 않을 경우 - false
- **reason** : 문서를 검색하고 이유와 출처를 표시 
""" 
            )
async def find_vienna_code(request: FindViennaCode):
    try:
        start_time = time.time()
        
        messages = await rejection.estimate_reject_or_enable(request.brand_image_url)
        
        end_time = time.time()
        total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time)%60:.2f}초"
        print(total_duration)

        return {"results":messages, "total_duration": total_duration}
    except Exception as e:
            print(f"오류 발생: {str(e)}")
            raise HTTPException(status_code=500, detail="서버에서 처리 중 오류가 발생했습니다.")




@router.post('/vienna-code', 
             name="비엔나 코드 찾는 Assistant",
             description="""
# 비엔나 코드 Assistant
```
이미지의 도형 모양을 파악하는 AI Assistant.
```
### 요 청 
- brand_image_url: 해당상표의 이미지 URL
### 응 답 
- 해당 이미지의 도형으로 추정되는 비엔나코드를 찾아 응답. 
""" 
            )
async def find_vienna_code(request: FindViennaCode):
    try:
        start_time = time.time()
        
        messages = await vienna_ex.process_vienna_code(request.brand_image_url)
        
        end_time = time.time()
        total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time)%60:.2f}초"
        print(total_duration)

        return {"results":messages, "total_duration": total_duration}
    except Exception as e:
            print(f"오류 발생: {str(e)}")
            raise HTTPException(status_code=500, detail="서버에서 처리 중 오류가 발생했습니다.")



@router.post('/similarity-code', 
             name="유사군 코드 찾는 Assistant",
             description="""
# 유사군 코드 Assistant
```
문서를 기반으로하여 해당 유사코드를 추측하고 답변하는 similarityCode를 분석하는 OPEN AI Assistant.
```

### 현재 업로드된 문서
- trademark_class.md : 해당문서에서 분류를 찾습니다.
- trademark_item.md : class에서 찾은 분류로 유사한 유사군을 찾습니다.


### 요 청 
- request_similarity_code: 유사코드 추측을 위한 메세지

### 응 답 
- 해당 메세지의 유사군 코드로 추정되는 분류목록과 유사군코드를 응답하는 Assistant의 메세지 

### 참고 사항
- 반환 형식이 정해져있기때문에, 반드시 상품의 '류'와 '유사코드'를 함께 물어보아야 해당 json형식으로 반환합니다.
"""
             )
async def find_similarity_code(request: FindSimilarityCode):
    start_time = time.time()
   
    messages= await similarity_code.similarity_code_finding_logic(request.request_similarity_code)

    end_time = time.time()
    total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time) %60:.2f}초"
    print(total_duration)

    return {"results": messages, "total_duration": total_duration}
