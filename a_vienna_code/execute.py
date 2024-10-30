import file_handler, common
import a_vienna_code.mes as mes
from fastapi import HTTPException


async def process_vienna_code(brand_image_url: str):
    # brand_name = request.brand_name
    
    brand_image_path = file_handler.download_image(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    thread, run = mes.create_thread_and_run(
        f"""
        업로드한 이미지의 모양을 파악후 해당하는 비엔나코드를 찾아 여러개 나열해주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )
    
    messages = await common.handle_run_response_for_code(run,thread)

    if isinstance(messages, list):
        combined_vienna_code = "|".join(
            item['vienna_code'] for item in messages if 'vienna_code' in item
        ) 
        # combined_vienna_code = "|".join(
        #     # "2.7.1"와 같이 점이 두개 포함되어있는 비엔나코드의 점을 분리하고, 앞에 0을 추가.
        #    format_vienna_code(item['vienna_code']) 
        #     for item in messages if 'vienna_code' in item and format_vienna_code(item['vienna_code']) is not None
        # ) 
        messages = {
            'combined_vienna_code': combined_vienna_code,
            'messages': messages
        }

    file_handler.delete_downloaded_images(brand_image_path)

    return messages


# # 점이 두개 포함되어있는 비엔나코드의 점을 분리하고, 앞에 0을 추가.
# def format_vienna_code(vienna_code):
#     # 점(.)을 제거하고 숫자가 한자리일 경우 앞에 0을 추가
#     parts = vienna_code.split('.')
#     formatted_parts = [part.zfill(2) for part in parts]
#     print(formatted_parts)
#     code = ''.join(formatted_parts)
#     if len(code) == 6:
#         return code
#     else:
#         return None
    

# vienna_code = ["2.4.7", "2.7", "23.4.1", "22.33.88" ]


# # None 값을 처리하면서 join
# combined_vienna_code = "|".join(
#     format_vienna_code(code) for code in vienna_code if format_vienna_code(code) is not None
# )

# print(combined_vienna_code)