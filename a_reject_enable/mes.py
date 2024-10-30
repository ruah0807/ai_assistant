import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ASSISTANT_ID = 'asst_6u1FKB9vGykwBY71ATTZQUIe'

def submit_message_with_image(thread, user_message, image_path, image_url):
    content = [{'type': 'text', 'text': user_message}]

    print(f"Opening image file: {image_path}")  # 각 이미지 경로를 출력하여 확인
    try:
        with open(image_path, 'rb') as image_file:
            file = client.files.create(file=image_file, purpose='vision')  # 이미지 분석을 위한 용도
            # 이미지 파일과 함께 라벨을 텍스트로 추가
            content.append({'type': 'image_file', 'image_file': {'file_id': file.id}})
            content.append({'type': 'text', 'text': f'등록하려는 상표 URL: {image_url}'})  # 원본 이미지 URL 라벨링
    except FileNotFoundError as e:
        print(f"Error: 파일을 찾을 수 없습니다. 경로: {image_path}. 에러: {str(e)}")

    if content:
        # 이미지 파일 전송
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    else:
        print(f"Error : 이미지 파일 전송 실패 ")

    print(f"이미지 업로드 완료 . thread_id : {thread.id}")



def run_with_tools(ASSISTANT_ID, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        tools=  [{'type': 'file_search'}],
        instructions= """
        [ Context ]
        해당 "상표심사기준202405.pdf"의 거절사유가 되는지 아닌지를 판단합니다.
       
        [ instructions ]
        1. 사용자가 요청한 상표의 이미지를 분석합니다.
        2. 문서 내의 거절 혹은 그렇지 않은 사유를 검색합니다.
        3. Json 형식으로 응답합니다.
        
        응답 형식(json): 

        {{
            "results":{
                "refused": (bool : true or false),
                "reason" : "(reason from the document in Korean)"
            }
        }}

        [Warning]
        - "refused"는 Boolean 타입으로 true 혹은 false만 반환합니다.
            - 거절 가능성이 판단될경우 : true
            - 거절되지 않을 가능성이 판단될 경우 : false
        - "reason"은 문서 내에서 구체적인 내용과 출처를 찾아 제공합니다.
        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input, image_path, image_url):
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input, image_path, image_url)
    run = run_with_tools(ASSISTANT_ID, thread)
    return thread, run

