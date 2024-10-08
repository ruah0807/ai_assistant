import time, asyncio, os
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import c_brand_discernment.mes as discernment
import c_brand_similarity.execute as similarity
import kipris_control, file_handler, common

router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"]
)

class DiscernmentEvaluation(BaseModel):
    brand_name: str 
    brand_image_url: str
    

class LabeledKiprisItems(BaseModel):
    title: Optional[str] = None
    similar_image_url: Optional[str] = None
    similar_image_path: str = None
    application_number: Optional[str] = None
    classification_code: Optional[str] = None
    vienna_code : Optional[str] = None

class SimilarityEvaluationRequest(BaseModel):
    brand_name: Optional[str] = ""
    brand_image_url: str
    brand_image_path: Optional[str] = None
    kipris_data: List[LabeledKiprisItems]
    
    
@router.post('/discernment', name="식별력 평가 Assistant",
            description="""

# 식별력 평가 Assistant
```
등록을 원하는 상표의 상표명과 미리 생성해놓은 이미지 URL로 Assistant에게 식별력 평가를 요청합니다.
```

### 참고 문서
- 상표심사기준 202405.pdf

### 요 청 
- **brand_name**: 등록대상 상표명 
- **brand_image_url**: 등록대상상표이미지 url

### 응 답 
- 보통명칭여부, 성질표시 상표, 관용상표, 간단하고 흔히 있는 표장에 따른 식별력 설명 후 종합의견.

"""
             )
async def discernment_trademark(request: DiscernmentEvaluation):
    start_time = time.time()
    brand_name = request.brand_name
    brand_image_url = request.brand_image_url
    
    brand_image_path = file_handler.download_image(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    # 스래드 생성
    thread, run = discernment.discernment_create_thread_and_run(
        f"""
        업로드한 이미지 상표 '{brand_name}'의 상표 식별력을 평가해주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )

    messages = await common.handle_run_response(run,thread, expect_json=False)

    file_handler.delete_downloaded_images(brand_image_path)
    
    end_time = time.time()
    total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time) %60:.2f}초"
    print(total_duration)

    return {"messages": messages, "ducation": total_duration}


@router.post("/evaluate-similarity", name="상표유사여부보고서(별책).pdf를 참고한 형식의 유사도 평가(IMAGE포함)",
             description="""
# 유사도 평가 Assistant
```
등록을 원하는 상표의 상표명과 미리 생성해놓은 이미지 URL로 Assistant에게 유사도 평가를 요청합니다.
```

### 참고 문서
- 상표심사기준 202405.pdf
- 상표유사여부보고서(별책).pdf

### 요 청 
- **brand_name** : 등록 상표명
- **brand_image_url** : 등록상표이미지 URL
- **kipris_data** : 키프리스 데이터

- (**brand_image_path** : 전처리 필터를 이용했다면 경로 포함)
- (**kipris_data.similar_image_path** : 전처리 필터를 이용했다면 경로 포함)

### 응 답 
- 유사여부보고서 형식의 유사도 평가.

### 참고사항
- 유사도 판단 중간필터링을 거쳤다면 brand_image_path와 similar_image_path가 포함이 되어있을것이고, 그렇지 않다면 포함이 되어있지않을 것이다. 
"""
             )
async def evaluate_similarity(request:SimilarityEvaluationRequest):
    try:    
        start_time = time.time()
        # 브랜드 이미지 경로 확인 또는 다운로드
        brand_image_path = request.brand_image_path if request.brand_image_path and os.path.exists(request.brand_image_path) else None

        if not brand_image_path:
            # brand_image_path가 없거나 유효하지 않은 경우 다운로드 시도
            brand_image_path = file_handler.download_image(request.brand_image_url)
            if not brand_image_path:
                # 다운로드 실패 시 예외 처리
                raise HTTPException(status_code=400, detail="브랜드 이미지 다운로드 실패")
        else:
            print(f"브랜드 이미지 경로(제공된 경로): {brand_image_path}")
        
        # Kipris 데이터의 similar_image_path 확인 및 다운로드
        download_needed = False
        for item in request.kipris_data:
            # similar_image_path 확인: 경로가 없거나 파일이 존재하지 않으면 다운로드 필요
            if not item.similar_image_path or not os.path.exists(item.similar_image_path):
                download_needed = True
                break  # 다운로드가 필요하면 바로 종료
        
        # 다운로드가 필요한 경우에만 다운로드 진행
        if download_needed:
            print("Kipris 데이터 이미지 다운로드 중...")
            result_data = await kipris_control.download_and_add_image_path(request.kipris_data)
        else:
            print("Kipris 데이터 이미지가 모두 존재합니다.")
            result_data = request.kipris_data  # 기존 데이터 사용

        # kipris 데이터 이미지 다운로드 및 경로 추가
        all_responses = []
        download_image_paths = [brand_image_path] 

        tasks = []
        for idx, result in enumerate(result_data):
            task = similarity.handle_single_result(result, idx, request, brand_image_path, all_responses, download_image_paths)
            tasks.append(task)
        # 비동기적으로 병렬 처리
        await asyncio.gather(*tasks)

        end_time = time.time()
        total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time) %60:.2f}초"
        print(total_duration)

        file_handler.delete_downloaded_images(download_image_paths)

        return{"message": all_responses, "processing_time": total_duration}
    
    except Exception as e :
        raise HTTPException(status_code=500, detail = f"서버오류발생: {str(e)}")
    



