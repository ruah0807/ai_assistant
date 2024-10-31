import file_handler, common
import a_reject_enable.mes as mes
from fastapi import HTTPException


async def estimate_reject_or_enable(brand_image_url: str):
    # brand_name = request.brand_name
    
    brand_image_path = file_handler.download_image(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    thread, run = mes.create_thread_and_run(
        f"""
        업로드한 이미지를 분석 후 상표심사기준에 따른 거절 사유가 있는지 없는 지를 판단해주세요.
        """, 
        image_path=brand_image_path,  
        image_url= brand_image_url
        )
    
    messages = await common.handle_run_response_for_code(run,thread)

    file_handler.delete_downloaded_images(brand_image_path)

    return messages