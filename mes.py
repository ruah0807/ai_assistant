from init import client,ASSISTANT_ID
import time



def submit_message(assistant_id, thread, user_message):
    #사용자 입력 메시지를 스레드에 추가
    client.beta.threads.messages.create(
        thread_id= thread.id,
        role = "user",
        content = user_message
    )

    #스레드에 메시지가 입력되었다면 실행 준비
    run= client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    return run

def wait_on_run(run,thread):
    start_time = time.time()    #시간 시작 기록
    # run이 완료될대까지 기다림 : polling 하며 대기 (polling: 서버와 응답을 주고받음)
    while run.status == 'queued' or run.status == 'in_progress':
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(0.5)
        end_time = time.time()  # 끝난 시간 기록
        duration = end_time - start_time # 응답시간 계산
        print(f"응답까지의 시간 : {duration:.2f} 초")
    return run, duration
    

def get_response(thread):
    # 스레드에서 메세지 목록가져오기
    return client.beta.threads.messages.list(thread_id=thread.id, order='asc')


# 새로운 스레드 생성 및 메시지 제출 함수
def create_thread_and_run(user_input):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    run = submit_message(ASSISTANT_ID, thread, user_input)
    return thread, run



# 메시지 출력용 함수
def print_message(response):
    for res in response:
        print(f'[{res.role.upper()}]\n{res.content[0].text.value}\n')
    print("-" * 60)

#반복문에서 대기하는 함수
def wait_on_run(run, thread):
    while run.status == 'queued' or run.status == 'in_progress':
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id = run.id
        )
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



# 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.
# thread1, run1 = create_thread_and_run('상품 심사기준의 각 조항에 대해 문서를 기반으로 하여 간단하게 설명해줘')
# thread2, run2 = create_thread_and_run('어떤기준이 가장 중요한가요?')
thread3, run3 = create_thread_and_run('24 * 17 - 2 = ?')



# run1= wait_on_run(run1, thread1)
# print_message(get_response(thread1))


# run2= wait_on_run(run2, thread2)
# print_message(get_response(thread2))

run3= wait_on_run(run3, thread3)
print_message(get_response(thread3))

# 세번째 스래드를 마치면 감사인사 전하고 종료
run4 = submit_message(ASSISTANT_ID, thread3,'고마워요')
run4 = wait_on_run(run4, thread3)
print_message(get_response(thread3))