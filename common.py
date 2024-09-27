import os, sys, time, json, asyncio
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
                message_data['content'].append({content.text.value})
                print(f"{content.text.value}\n")
            # 이미지 파일일 경우
            elif content.type == 'image_file':
                print(f"식별력 평가 대상 이미지 파일 ID: {content.image_file.file_id}\n")
        messages.append(message_data)
        print("-" * 60)

        return messages
    
def print_json_from_assistant(response):
    # 첫 번째 메시지 처리
    res = response.data[0]  # response 리스트의 첫 번째 항목
    
    # res.content가 리스트일 수 있으므로, 이를 순차적으로 처리
    for content in res.content:
        if content.type == 'text':  # content의 타입이 'text'일 경우 처리
            try:
                # JSON 스타일의 텍스트를 파싱
                parsed_json = json.loads(content.text.value)
                
                # 필요한 필드만 추출하여 저장
                filtered_data = {
                    "title": parsed_json.get("title"),
                    "similar_image_url": parsed_json.get("similar_image_url"),
                    "application_number": parsed_json.get("application_number"),
                    "classification_code": parsed_json.get("classification_code"),
                    "vienna_code": parsed_json.get("vienna_code"),
                    "text_similarity_score": parsed_json.get("text_similarity_score"),
                    "image_similarity_score": parsed_json.get("image_similarity_score"),
                }
                
                # 필터된 데이터를 반환
                return filtered_data
            
            except json.JSONDecodeError as e:
                # 만약 JSON 파싱이 실패하면 오류 로그를 출력
                print(f"JSON 파싱 실패: {e}")
                print(f"오류 발생한 내용: {content.text.value}")
                return None
        
    else:
        print("텍스트 콘텐츠를 찾을 수 없습니다.")
        return None


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
        messages = print_json_from_assistant(response)
        
        return messages
    
    except Exception as e:
        print(f"Error while handling run response: {e}")
        return None