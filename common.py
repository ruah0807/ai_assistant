import os, sys, time, requests, asyncio
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

# 메시지 출력용 함수
def print_message(response):
    messages = []
    for res in response:
        message_data = {"role": res.role.upper(), "content":[]}
        print(f'[{res.role.upper()}]')

        # res.content 안의 각 항목을 처리
        for content in res.content:
            # 텍스트일 경우
            if content.type == 'text':
                message_data['content'].append({"type":"text", "value":content.text.value})
                print(f"{content.text.value}\n")
            # 이미지 파일일 경우
            elif content.type == 'image_file':
                print(f"식별력 평가 대상 이미지 파일 ID: {content.image_file.file_id}\n")
        messages.append(message_data)
        print("-" * 60)

        return messages


# 실행 완료까지 대기하는 함수
async def wait_on_run(run, thread, timeout=500):
    start_time = time.time()
    while run.status == 'queued' or run.status == 'in_progress':
        # 상태를 출력하여 디버깅
        print(f"현재 run 상태: {run.status}")
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        # 일정 시간이 지나면 타임아웃 발생
        if time.time() - start_time > timeout:
            raise TimeoutError("Run이 지정된 시간 안에 완료되지 않았습니다.")
        await asyncio.sleep(1)
    return run



async def handle_run_response(run, thread):
    """
    assistant의 실행 결과를 기다리고, 결과 메시지를 처리하는 함수
    """
    try:
        # 실행 완료 대기
        run = await wait_on_run(run, thread)
        
        # 응답 받아오기
        response = client.beta.threads.messages.list(thread_id=thread.id)
        
        # 응답 메시지 출력
        messages = print_message(response)
        
        return messages
    
    except Exception as e:
        print(f"Error while handling run response: {e}")
        return None