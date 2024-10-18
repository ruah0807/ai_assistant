import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import c_brand_discernment.mes as discernment
import c_brand_similarity.execute as similarity
import file_handler, common


router = APIRouter(
    prefix="/assistant",
    tags=["식별력 평가"]
)

class DiscernmentEvaluation(BaseModel):
    brand_name: str 
    brand_image_url: str
    asign_product_description : str
    
    
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
- **asign_product_description**: 지정상품의 주요부 판단을 위한 인풋

### 응 답 
- 보통명칭여부, 성질표시 상표, 관용상표, 간단하고 흔히 있는 표장에 따른 식별력 설명 후 종합의견.

"""
             )
async def discernment_trademark(request: DiscernmentEvaluation):

    start_time = time.time()
    brand_image_path = file_handler.download_image(request.brand_name)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    # 스래드 생성
    thread, run = discernment.discernment_create_thread_and_run(
        f"""
        업로드한 이미지 상표와 지정상품설명으로 상표의 주요부를 판단하여 상표 식별력을 평가해주세요 
        브랜드명 : {request.brand_name}
        지정상품설명 : {request.asign_product_description}
        """, 
        image_path=brand_image_path, 
        image_url= request.brand_image_url
        )

    messages = await common.handle_run_response(run,thread, expect_json=False)

    file_handler.delete_downloaded_images(brand_image_path)
    
    end_time = time.time()
    total_duration = f"전체 처리 시간: {int((end_time - start_time) // 60)}분 {(end_time - start_time) %60:.2f}초"
    print(total_duration)

    return {"messages": messages, "ducation": total_duration}

