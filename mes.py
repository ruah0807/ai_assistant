import time
import os
from dotenv import load_dotenv
from init import ass_id, client
from ass import default_tools
load_dotenv()




def submit_message(ass_id, thread, user_message, image_path=None):

    content = [{'type': 'text', 'text': user_message}]

    if image_path:
        file = client.files.create(
            file = open(image_path, 'rb'),
            purpose='vision'    # 이미지 분석용도로 'vision'을 사용
        )
        content.append({
            'type': 'image_file',
            'image_file' : { 'file_id': file.id}
        })
        # 이미지가 있다면 도구를 사용하지 않도록 설정 (이미지 업로드 시 도구와함께 사용 불가)
        tools_setting = []
    else:
        tools_setting = default_tools

    #사용자 입력 메시지를 스레드에 추가
    client.beta.threads.messages.create(
        thread_id= thread.id,
        role = "user",
        content = content
    )

    #스레드에 메시지가 입력되었다면 실행 준비
    run= client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools = tools_setting
    )
    print(f'assistant_id : {ass_id}')
    print(f'thread_id : {thread.id}')
    print(f'run_id : {run.id}')

    return run



def get_response(thread):
    # 스레드에서 메세지 목록가져오기
    return client.beta.threads.messages.list(thread_id=thread.id, order='asc')


# 새로운 스레드 생성 및 메시지 제출 함수
def create_thread_and_run(user_input, image_path=None):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    run = submit_message(ass_id, thread, user_input, image_path=image_path)
    return thread, run

def send_message_in_same_thread(thread, user_message, image_path=None):
    # 메시지 전송
    run = submit_message(ass_id, thread, user_message, image_path=image_path)
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



# 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.
# thread1, run1 = create_thread_and_run("상표이름 '마인드셋'의 의견서를 제시해 주세요")
thread, run = create_thread_and_run("내 상표의 식별력, 그리고 내 상표와 유사한 상표가 있는지 알고싶어요.")

run= wait_on_run(run, thread)
print_message(get_response(thread))

run = send_message_in_same_thread(thread, "이게 나의 상표 입니다.", image_path='brand_img/starbings.png')

run= wait_on_run(run, thread)
print_message(get_response(thread))


run = send_message_in_same_thread(thread, "의견서를 문서형식으로 제시해 주세요")

run= wait_on_run(run, thread)
print_message(get_response(thread))

# 세 번째 스레드를 마친 후 감사 인사 전송
thread, run = submit_message(thread, '고마워요')  # run3이 완료된 후 메시지 전송

run = wait_on_run(run, thread)  # run4 완료될 때까지 대기
print_message(get_response(thread))