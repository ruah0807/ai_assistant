import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import a_vienna.mes as vienna
import file_handler, common



router = APIRouter(
    prefix="/find",
    tags=["Vienna Code"]
)

class FindViennaCode(BaseModel):
    # brand_name: str 
    brand_image_url: str


@router.post('/vienna_code', name="비엔나 코드 찾는 assistant")
async def discernment_trademark(request: FindViennaCode):
    start_time = time.time()
    # brand_name = request.brand_name
    brand_image_url = request.brand_image_url
    
    brand_image_path = file_handler.download_image(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    # 스래드 생성
    thread, run = vienna.create_thread_and_run(
        f"""
        업로드한 이미지의 비엔나코드를 찾아주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )

    messages = await common.handle_run_response(run,thread, expect_json=False)

    file_handler.delete_downloaded_images(brand_image_path)
    
    end_time = time.time()
    total_duration = end_time - start_time
    total_duration = f"전체 처리 시간: {int(total_duration // 60)}분 {total_duration %60:.2f}초"
    print(total_duration)

    return {"messages": messages, "ducation": total_duration}