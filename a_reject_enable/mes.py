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
        사용자는 해당 상표(이미지)를 등록하기 위해 법원 의견서를 재출하기 이전에
        해당 상표가 "상표심사기준202405.pdf" 기준 중에서 거절사유가 될만한 것이 있는지를 미리 판단 합니다.
       
        [ instructions ]
        1. 사용자가 요청한 상표의 이미지를 분석합니다.
        2. 분석한 이미지에 거절될만한 사유가 있을지를 분석합니다.
        3. 거절 혹은 그렇지 않은 사유를 검색합니다.
        4. 아래 Json 형식으로 응답합니다.
            - "refused" : Boolean 
                - 등록이 거절될 가능성이 판단될 경우 : true
                - 등록이 가능하다 판단될 경우: false
            - "reference" : String
                - "상표법 제 ?조 ?항 ?호"
            - "reason" : String 
                - 문서 내에서 구체적인 내용과 출처를 찾아 제공합니다.
                예1 ) "refused"가 'true'일 경우 ->  "(등록 불가 판단 이유)"
                예2 ) "refused"가 'false'일 경우 -> "(등록 가능하다 판단 이유)"

        응답 형식(json): 

        {{
            "results":{
                "refused": (bool : true or false),
                "reference": (찾은 해당 상표 조항)
                "reason" : "(이유 - 한국어로 작성합니다.)"
            }
        }}

        [ Warning ]
        - 당신의 지식과 문서에서 존재하는 상표는 거절 사유로 판단하세요.
        - 식별력은 판단하지 마세요.
        - 상표가 존재 할수도 있다는 애매한 판단보다는, 확실히 존재하는 상표만을 거절 사유로 판단하세요.
        - 반드시 한국어로 응답하고, json 포멧 안에서만 대답하세요.
        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input, image_path, image_url):
    print("1")
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input, image_path, image_url)
    run = run_with_tools(ASSISTANT_ID, thread)
    return thread, run

