import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ass_id = 'asst_5AAVBLsDY7vpCx7g4nVGe67R'


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


def run_with_tools(ass_id, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools=  [{'type': 'file_search'}],
        instructions= """
        [ Context ]
        사용자가 올린 이미지가 어떤형태인지 도형의 모양이나 물체의 갯수, 모양을 추측하고  
        Vienna_code.md 문서를 참고하여
        비슷하다 판단되는 Vienna Code를 찾아 나열하세요

        [ instructions ]
        1. 사용자가 업로드한 이미지를 분석합니다.
        2. [vienna_code.md] 파일에서 분석한 이미지에 대응하는 information을 찾습니다.
        3. 찾은 information에 해당하는 Vienna Code를 반환이유와 함께 반환하세요.

        [Warning]
        - 도형코드는 1개가 아닐수도 있으니 끝까지 찾으세요.
        - 자신의 답이 문서 내에서 찾은 것이 맞는지 한번더 확인한 후 대답합니다.
        - 반드시 문서에서 vienn code를 찾아야합니다.
        
        
        응답 형식은 반드시 Json으로 표현합니다:

        {{
        [
            {
                shape: (도형 모양이나, 그외의 추측)
                vienna_code: (비엔나코드),
            },
            ...
        ]
        }}
        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input, image_path, image_url):
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input, image_path, image_url)
    run = run_with_tools(ass_id, thread)
    return thread, run

