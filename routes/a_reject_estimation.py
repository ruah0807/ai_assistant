import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import a_reject_enable.execute as rejection



router = APIRouter(
    tags=["거절 상표 판단"]
)

class EstimateRejection(BaseModel):
    brand_image_url: str



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
async def find_vienna_code(request: EstimateRejection):
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

