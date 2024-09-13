import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from ass_text import ass_id
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
def wait_on_run(run, thread, timeout=300, retries=3):
    start_time = time.time()
    attempts = 0
    while attempts < retries:
        while run.status == 'queued' or run.status == 'in_progress':
            print(f"현재 run 상태: {run.status}")
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if time.time() - start_time > timeout:
                attempts += 1
                print(f"타임아웃 발생. {attempts}/{retries}회 재시도 중...")
                if attempts >= retries:
                    raise TimeoutError("Run이 지정된 시간 안에 완료되지 않았습니다.")
                else:
                    time.sleep(1)  # 재시도 전 잠시 대기
                    start_time = time.time()  # 타이머 재설정
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


def check_last_message(thread):
    messages = get_response(thread)
    last_message = messages[-1].content[0].text.value
    # 답변이 완료되었는지 확인
    if "고마워요" not in last_message:  # 기대한 답변을 기준으로 조건을 설정
        print("답변이 완료되지 않았습니다. 다시 질문을 보냅니다.")
        send_message_in_same_thread(thread, "마지막 질문에 답변해 주세요.")
    else:
        print("답변이 완료되었습니다.")


# 상표 이름
brand_name = '시민언론시선' #<==입력을 받는다고 가정
classification_code = 38

#비슷한 단어 찾기
similar_words = generate_similar_barnd_names(brand_name)
# 분류코드와 비슷한단어로 상표 검색
result_data= updated_search_results_for_text(similar_words['words'], classification_code)


# 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.
thread, run = create_thread_and_run(f"상표를 등록하려고 합니다.")

run= wait_on_run(run, thread)
print_message(get_response(thread))


run = send_message_in_same_thread(
    thread, 
    f"""
    제가 등록하고 싶은 상표명입니다.
    \n상표명 : {brand_name}\n상품류/유사군:{classification_code}
    아래는 특허청에서 비슷한 상표를 검색한 데이터입니다. 상표명(텍스트)를 각 기준으로 하여 제가 업로드한 상표명의 이름을 기반으로 유사도를 검토 해서 가장 비슷하다고 생각하는 5가지를 각각을 명확하게 판단하고, 어떤부분이 어떻게 다른지 혹은 같은지를 각각 설명하세요.\n\n{result_data}""", 
    )# json데이터를 보낼것.

try:
    run = wait_on_run(run, thread)
    print_message(get_response(thread))
except TimeoutError:
    print("시간 내에 답변을 받지 못했습니다. 다시 시도합니다.")
    run = send_message_in_same_thread(thread, "이전 질문에 대한 답변을 받지 못했습니다. 다시 한번 확인해 주세요.")
    run = wait_on_run(run, thread)
    print_message(get_response(thread))


# 세 번째 스레드를 마친 후 감사 인사 전송
# thread, run = submit_message(thread, '고마워요')  # run3이 완료된 후 메시지 전송

# run = wait_on_run(run, thread)  # 완료될 때까지 대기
# print_message(get_response(thread))


