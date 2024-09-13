import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from ass_similar import ass_id
from init import client
from kipris_api import updated_search_results_for_text
from similar import generate_similar_barnd_names


def submit_message(ass_id, thread, user_message):

    content = [{'type': 'text', 'text': user_message}]

    # 메시지 전송
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content

    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        instructions= """
         [ Context ]
            •	업로드된 문서기반으로 상표의 텍스트 유사성을 평가.
            •	관련 법률 조항을 통해 유사성이 얼마나 있는지를 법률기반으로 상세히 설명.

        [ dialog flow ]
            1.	상표 입력 요청:
                - 사용자가 상표의 텍스트를 입력합니다.
            2.	상표 분석
            3.	상표심사기준 적용:
                - vectorstore에 업로드된 [상표심사기준202405.pdf]을 기준으로 각각 상표의 유사성을 평가하고 설명합니다.
            각각의 상표 텍스트를 비교하여 얼마나 비슷한지를 아래와 같이 평가합니다.:
                
                    - 검토의견: 상표의 유사성을 각각 평가.
                        상표명 : (title)
                        상품류: (claasificationCode)
                        상표이미지: (bigDrawing)
                        출원/등록일 : (applicationDate)
                        출원인/등록권자: (applicantName)
                        유사도 : (O,△,X 로 판단)
                        검토의견 : [어떤 부분이 비슷한지 아닌지 판단]
                    - 종합의견 : [(상표심사기준202405.pdf) 문서에 포함되어있는 법률 기반의 신뢰성 있는 답변- 법률의 몇조 몇항인지 소스를 밝히며 설명해야합니다.]


        [ Constraints ]
            •	영어발음을 그대로 쓴것과, 영어의 번역 버전을 한국어로 쓴것은 다르다고 판단합니다.
        """
    )
    print(f'assistant_id : {ass_id}')
    print(f'thread_id : {thread.id}')
    print(f'run_id : {run.id}')

    return run



def get_response(thread):
    # 스레드에서 메세지 목록가져오기
    return client.beta.threads.messages.list(thread_id=thread.id, order='asc')


# 새로운 스레드 생성 및 메시지 제출 함수
def create_thread_and_run(user_input):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    run = submit_message(ass_id, thread, user_input)
    return thread, run

def send_message_in_same_thread(thread, user_message):
    # 메시지 전송
    run = submit_message(ass_id, thread, user_message)
    return run



# 메시지 출력용 함수
def print_message(response):
    for res in response:
        print(f'[{res.role.upper()}]\n{res.content[0].text.value}\n')
    print("-" * 60)

#반복문에서 대기하는 함수
def wait_on_run(run, thread, timeout=120):
    start_time = time.time()
    while run.status == 'queued' or run.status == 'in_progress':
        # 상태를 출력하여 디버깅
        print(f"현재 run 상태: {run.status}")
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id = run.id
        )
        # 일정 시간이 지나면 타임아웃 발생
        if time.time() - start_time > timeout:
            raise TimeoutError("Run이 지정된 시간 안에 완료되지 않았습니다.")
        time.sleep(0.5)
    return run

def check_run_step(thread_id, run_id):
    #실행된 모든 단계를 조회하여 도구 사용 여부 확인
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread_id,
        run_id=run_id,
        order='asc'
    )
    for step in run_steps:
        print(step)



# 상표 이름
brand_name = '시민언론시선' #<==입력을 받는다고 가정
classification_code = 38

#비슷한 단어 찾기
similar_words = generate_similar_barnd_names(brand_name)
# 분류코드와 비슷한단어로 상표 검색
result_data= updated_search_results_for_text(similar_words['words'], classification_code)


# 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.

thread, run = create_thread_and_run(
    f"""
    제가 등록하고 싶은 상표명입니다.
    \n상표명 : {brand_name}\n상품류/유사군:{classification_code}
    아래는 특허청에서 비슷한 상표를 검색한 데이터입니다. 업로드되어있는 문서를 기반으로 하여 상표명의 유사도를 명확하게 판단하고, 어떤부분이 어떻게 다른지 혹은 같은지를 각각 설명해주세요.\n\n{result_data}""", 
    )# json데이터를 보낼것.

run = wait_on_run(run, thread)
print_message(get_response(thread))



# 세 번째 스레드를 마친 후 감사 인사 전송
# thread, run = submit_message(thread, '고마워요')  # run3이 완료된 후 메시지 전송

# run = wait_on_run(run, thread)  # 완료될 때까지 대기
# print_message(get_response(thread))


