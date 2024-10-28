import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ASSISTANT_ID = 'asst_W8YP62HfQPvHsKFavgndRJ1T'


def submit_message_with_image(thread, user_message):
    content = [{'type': 'text', 'text': user_message}]

    if content:
        # 이미지 파일 전송
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    else:
        print(f"Error : 이미지 파일 전송 실패 ")

    print(f"thread_id : {thread.id}")


def run_with_tools(ASSISTANT_ID, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        tools=  [{'type': 'file_search'}],
        instructions= """
        [ Context ]
        사용자가 요청한 상표가 어떤 유사군에 가까운지 유사코드를 찾아야합니다.
        문서를 참고하여 해당된다 판단되는 '유사코드'를 찾아 JSON형식으로 나열하세요.
       
        [ instructions 1. ]
        1. 사용자가 요청한 상표의 유사군을 분석한 후 문서를 검색합니다.
        2. 문서 trademark_class.md 파일에서 사용자의 브랜드 설명에 가장 어울리는 '류'를 찾습니다.(여러개일 수 있습니다.)
            - 사용자가 직접적인 '류'를 입력하는 경우 : 해당 '류' 안에서만 유사코드를 찾아주세요.
        3. 문서 trademark_item.md 파일에서 해당 류에 포함되는 상품 및 서비스를 참조하여, 각 trademark_class.md파일에서 찾은 '류'에 가장 어울리는 유사군을 각각 찾습니다. 비슷한 유사군이 없으면 그나마 가장 비슷한 유사군을 제시합니다.(여러개 일 수 있습니다.)
        4. 'NICE'분류 기준으로 해당 리스트를 작성하세요. 

        
        응답 형식(json): 

        {{
            "results":{
                "similarity": [
                    { 
                        "niceNum": (분류 예시 : 33),
                        "similarity_code: (유사군코드 예시: "G1234, G2345, G9999"),
                        "info": (포함되는 상품 및 서비스 설명)
                    },
                    ...
                ],
                "total_reason": (통합적인 이유 설명)
            }
        }}

        [Warning]
        - '유사군코드'는 여러개 일수 있습니다. 
        - 해당 요청과 관련있는 '류'와 '유사코드'만 나열하세요
        - 사용자가 직접적인 '류'를 입력하는 경우에는 해당 '류' 안에서만 유사코드를 찾아주세요.
        
        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input)
    run = run_with_tools(ASSISTANT_ID, thread)
    return thread, run


