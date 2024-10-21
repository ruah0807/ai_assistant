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
- brand_image_url: 해당상표의 이미지 URL
### 응 답 
- 해당 이미지의 도형으로 추정되는 도형 설명을 찾아 응답. 
### 참고 사항
- 비엔나코드 자체를 찾는것은 현재 존재하는 문서로서는 불가능합니다.
- 반환된 "shape"의 value값으로 [KIPRIS웹사이트](http://www.kipris.or.kr/kdtj/code1000a.do?method=search&recvField=)에서 직접 비엔나코드를 찾습니다.
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
