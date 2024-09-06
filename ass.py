import time
from init import client

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
    # run이 완료될대까지 기다림 : polling 하며 대기 (polling: 서버와 응답을 주고받음)
    while run.status == 'queued' or run.status == 'in_progress':
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(0.5)
    return run

def get_response(thread):
    # 스레드에서 메세지 목록가져오기
    return client.beta.threads.messages.list(thread_id=thread.id, order='asc') 




