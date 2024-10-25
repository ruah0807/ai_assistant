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
        문서를 참고하여 해당된다 판단되는 '유사코드'를 찾아 JSON형식으로 나열하세요.
       
        [ instructions ]
        1. 사용자가 업로드한 이미지를 분석합니다.
        2. 문서 trademark_class.md 파일에서 사용자의 브랜드 설명에 가장 어울리는 '류'를 찾습니다.(여러개일 수 있습니다.)
        3. 문서 trademark_item.md 파일에서 해당 류에 포함되는 상품 및 서비스를 참조하여, 각 trademark_class.md파일에서 찾은 '류'에 가장 어울리는 유사군을 각각 찾습니다. 비슷한 유사군이 없으면 그나마 가장 비슷한 유사군을 제시합니다.(여러개 일 수 있습니다.)
        4. 'NICE'분류 기준으로 해당 리스트를 작성하세요. 

        응답 형식(json): 

        {{
            "results":{
                "similarity": [
                    { 
                        "niceNum": (분류),
                        "similarity_code: (유사군코드),
                        "info": (포함되는 상품 및 서비스 설명)
                    },
                    ...
                ],
                "total_reason": (통합적인 이유 설명)
            }
        }}

        [Warning]
        - '유사군코드'는 여러개 일수 있습니다. 리스트로 나열하세요.
        - 비슷한 유사코드가 있다면 전부 리스트에 포함합니다.
        - 반드시 문서 한 행에 있는 '유사군코드'와 '분류'를 찾아주세요.
        - 만일 '분류'가 있다면 한 묶음 안에 info와 유사군 코드를 여러개 나열하세요.
        - '분류'가 다르게 검색되는 경우 또한 리스트에 포함합니다.
        
        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input)
    run = run_with_tools(ass_id, thread)
    return thread, run


