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
        업로드한 이미지의 모양을 파악후 [vienna_code_eu.pdf]문서에서 해당하는 비엔나코드를 찾아 여러개 나열해주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )
    
    messages = await common.handle_run_response_for_code(run,thread)

    print(f"messages : {messages}")

    if isinstance(messages, list):
        combined_vienna_code = "|".join(
            item['vienna_code'] for item in messages if 'vienna_code' in item
        ) 
        print(f"\nCombined Vienna Code : {combined_vienna_code}\n")
        messages = {
            'combined_vienna_code': combined_vienna_code,
            'messages': messages
        }

    file_handler.delete_downloaded_images(brand_image_path)

    return messages

