import file_handler, common
import a_vienna_code.mes as mes
from fastapi import HTTPException


async def process_vienna_code(brand_image_url: str):
    # brand_name = request.brand_name
    
    brand_image_path = file_handler.download_image(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    # 스래드 생성
    thread, run = mes.create_thread_and_run(
        f"""
        업로드한 이미지의 모양을 파악후 [vienna.md]문서에서 해당하는 '### 도형설명'의 해당부분을 찾아 여러개 나열해주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )

    messages = await common.handle_run_response_for_code(run,thread)

    file_handler.delete_downloaded_images(brand_image_path)

    return messages
