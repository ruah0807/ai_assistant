from fastapi import APIRouter, HTTPException
import time, asyncio
from typing import List, Optional
from pydantic import BaseModel
import file_handler, common
import b_similar_posibility_image.execute as similarity
import kipris.kipris_control as kipris_control

router = APIRouter(
    prefix="/assistant",
    tags=["중간 필터"]
)

class LabeledKiprisItems(BaseModel):
    title: Optional[str] = None
    classification_code: Optional[str] = None
    similar_image_url: Optional[str] = None
    application_number: Optional[str] = None
    vienna_code : Optional[str] = None

class SimilarityEvaluationRequest(BaseModel):
    brand_name: Optional[str] = None
    brand_image_url: str
    kipris_data: List[LabeledKiprisItems]
    
    

@router.post("/comepare-brands", name="상표 보고서 작성 전 이미지 유사 데이터 필터링(kipris 검색결과가 너무 많을경우 사용)", 
             description="""
# 상표 보고서 작성 전 이미지를 기준으로 한 데이터 필터링
```
상표 보고서 작성 전 Kipris에서 검색한 리스트가 너무 많을경우 상표리스트를 상표 이미지를 기반으로 하여 필터링합니다.
또한, 해당 이미지는 viennaCode가 null값인것도 이미지 속 텍스트의 배치를 판단하고 필터링합니다.

만일 필터링이 필요없다 판단되면 건너뛰어도 무방합니다.

```
### 요 청
- brand_name : 해당 등록 상표 
- brand_image_url :해당 등록 상표의 URL
- kipris_data : 키프리스에서 검색한 리스트

### 응 답
- 리스트에 similarity 항목이 추가
- "similarity" : True 인 항목들만을 반환.

### 참고 사항 
- 판단 후 하나라도 True가 들어가있다면 값을 반환
- 각 상표 이미지의 업로드 시간이 걸릴수 있습니다.
    * 30개의 검색어 : 총소요시간 1분 27.21초 
    * 45개의 검색어 : 총소요시간 1분 59.56초
             """)
async def compare_brand(request:SimilarityEvaluationRequest):
    try:    
        start_time = time.time()
        # 1. 브랜드 이미지 다운로드
        brand_image_path = file_handler.download_image(request.brand_image_url)

        if not brand_image_path:
            raise HTTPException(status_code=400, detail="이미지 파일 다운로드 실패")
        print(f"브랜드 이미지 경로: {brand_image_path}")

        # 2. kipris 데이터 이미지 다운로드 및 경로 추가
        result_data = await kipris_control.download_and_add_image_path(request.kipris_data)

        all_responses = []
        download_image_paths = [brand_image_path]

        tasks = []
        for idx, result in enumerate(result_data):
            task = similarity.score_result(result, idx, request, brand_image_path, all_responses, download_image_paths)
            tasks.append(task)

        # 비동기적으로 병렬 처리
        await asyncio.gather(*tasks)

        end_time = time.time()
        total_duration = f"상표 유사도 평가 Assistant 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time) %60:.2f}초"
        print(total_duration)
        
        # 유효한 응답의 개수 카운트
        similar_count = f"유사판단 상표 갯수 : {sum(1 for response in all_responses if response)} 개"
        print(similar_count)

        return{
            "brand_name": request.brand_name,
            "brand_image_url": request.brand_image_url,
            "brand_image_path": brand_image_path,
            "kipris_data": all_responses, 
            "processing_time": total_duration, 
            "similar_count":similar_count
            }
    
    except Exception as e :
        raise HTTPException(status_code=500, detail = f"서버오류발생: {str(e)}")
    

