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
        문서 목록은 총 267개이며 아래와같은 분류로 1000개씩 배치 되어있습니다.

        1. 24년_지정상품고시목록(출처포함) .md
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
        4. 'NICE'분류 기준으로 해당 리스트를 작성하세요. 
        5. similarity_code는 ','가 아닌 '|' 로 구분합니다.


        응답 형식에는 이유와 함께 반드시 json 형식의 답변을 포함합니다.:

        - 이유 : (코드반환 이유 설명)

        {{
        [
            info: (지정상품(한글): 여러개 가능)
            niceNum: (NICE분류)
            similarity_code: (유사군코드 여러개 가능),
        ],
        ...
        }}

        
        [Warning]
        - '유사군코드'는 여러개 일수 있습니다. 끝까지 찾아본후 각 다른 10개 이하의 행을 리스트로 나열하세요.
        - 자신의 답이 문서 내에서 찾은 것이 맞는지 한번더 확인한 후 대답합니다.
        - 반드시 문서 한 행에 있는 '유사군코드'와 'NICE분류'를 찾아주세요.
        - 만일 'NICE분류'가 있다면 한 묶음 안에 info와 유사군 코드를 여러개 나열하세요.
        - 'NICE분류'가 다르게 검색되는 경우 또한 리스트에 포함합니다.

        Json 응답 예시 : 
        {{
            {
                "info": "교육 또는 연예오락에 관한 대회조 직업 등",
                "niceNum": 41,
                "similarity_code": "S110101|S120906|S121002"
            },
            {
                "info": " 연예오락 정보제공업 등",
                "niceNum": 41,
                "similarity_code": "S110101|S121002"
            },
            {
                "info": "오락 또는 문화목적의 사용자 리뷰제공업 등",
                "niceNum": 41,
                "similarity_code": "S110101|S120902|S121002|S121003"
            },
            {
                "info": "내려받기 불가능한 소프트웨어 온라인제공업",
                "niceNum": 42,
                "similarity_code": "S123301|G390802"
            },
            {
                "info": "내려받기 가능한 이동통신 애플리케이션 수단에 의해 접근 가능한 온라인 소셜 네트워킹 서비스업, 온라인 소셜 네트워킹 서비스업",
                "niceNum": 43,
                "similarity_code": "S0601|S123301|S174599"
            },
            ...
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

