import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ass_id = 'asst_W8YP62HfQPvHsKFavgndRJ1T'


def submit_message_with_image(thread, user_message):
    content = [{'type': 'text', 'text': user_message}]

    if content:
        # 이미지 파일 전송
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    else:
        print(f"Error : 이미지 파일 전송 실패 ")

    print(f"thread_id : {thread.id}")


def run_with_tools(ass_id, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools=  [{'type': 'file_search'}],
        instructions= """
        [ Context ]
        사용자가 올린 이미지가 어떤 유사군에 가까운지 유사코드를 찾아야합니다.
        문서들을 참고하여 해당된다 판단되는 '유사군코드'를 찾아 나열하세요
        문서 목록은 총 4가지이며

        1. 24년_지정상품고시목록(출처포함)-표1.md
        2. 35-구매대행업-표1.md
        3. 35-도매업-표1.md
        4. 35-소매업-표1.md
        5. 35-중개업-표1.md
        6. 35-판매대행업-표1.md
        7. 35-판매알선업-표1.md

        위 파일안에서 유사군 코드를 찾아야합니다.

        [ instructions ]
        1. 사용자가 업로드한 이미지를 분석합니다.
        2. 사용자의 브랜드 설명에 대응하는 '지정상품(국문)' or '지정상품(영문)'에서 찾습니다.
        3. 찾은 '지정상품'에 해당하는 행의 '유사군코드'와 'NICE분류' 번호를 반환하세요.

        응답 형식에는 이유와 함께 반드시 json 형식의 답변을 포함합니다.:

        - 이유 : (코드반환 이유 설명)

        {{
        [
            info: (지정상품(한글))
            niceNum: (NICE분류)
            similarity_code: (유사군코드),
        ],
        ...
        }}

        
        [Warning]
        - '유사군코드'는 여러개 일수 있습니다. 끝까지 찾아본후 각 다른 10개 이하의 행을 리스트로 나열하세요.
        - 자신의 답이 문서 내에서 찾은 것이 맞는지 한번더 확인한 후 대답합니다.
        - 반드시 문서 한 행에 있는 '유사군코드'와 'NICE분류'를 찾아주세요.
        - 만일 중복되는 '유사군코드'와 'NICE분류'가 있다면 한 묶음 안에 info를 여러개 나열하세요.
        Json 응답 예시 : 
        {{
            [
                {
                    info: (지정상품(한글) 예시: 금속제 스테이플 도매업, 금속제 쐐기 도매업, 금속제 스테이플 소매업, 금속제 쐐기 소매업)
                    niceNum: (NICE분류 예시: 35)
                    similarity_code : (유사군코드 예시: S2023)
                },
                {
                    info : (지정상품(한글)),
                    niceNum: (NICE분류),
                    similarity_code : (유사군코드)
                }
                ...
            ]
        }}

        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input)
    run = run_with_tools(ass_id, thread)
    return thread, run

