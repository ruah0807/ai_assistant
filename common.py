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
    


    # 모든 메시지를 처리
def print_json_from_assistant(response):
    for res in response.data:
        # res.content가 리스트일 수 있으므로, 이를 순차적으로 처리
        for content in res.content:
            if content.type == 'text':  # content의 타입이 'text'일 경우 처리
                try:
                    # JSON 스타일의 텍스트를 파싱
                    print(f"{content.text.value}\n")
                    parsed_json = extract_json_from_text(content.text.value.strip())
                    if not parsed_json:  # 만약 문자열이 비어 있으면 건너뜀
                        print("비어 있는 메시지 발견, 건너뜀.")
                        continue
                    
                    # 필요한 필드만 추출하여 저장
                    filtered_data = {
                        "title": parsed_json.get("title"),
                        "similar_image_url": parsed_json.get("similar_image_url"),
                        "similar_image_path": parsed_json.get("similar_image_path"),
                        "application_number": parsed_json.get("application_number"),
                        "classification_code": parsed_json.get("classification_code"),
                        "vienna_code": parsed_json.get("vienna_code"),
                        "similarity": parsed_json.get("similarity")
                    }

                    # 조건: similarity 가 True인 경우만 저장
                    if filtered_data.get("similarity") == True :
                        return filtered_data
                    else:
                        print(f"브랜드명 : {filtered_data.get('title')} - 둘 다 false.")
                        return None

                except Exception as e:
                    print(f"예상치 못한 오류 발생: {e} - {content.text.value}")
                    return None


#  텍스트에서 JSON 부분만 추출하여 반환하는 함수
def extract_json_from_text(text):
    try:
        # 응답 텍스트에서 JSON 부분을 찾기
        start = text.find('{')
        end = text.rfind('}') + 1
        # JSON 형식의 부분만 추출
        if start != -1 and end != -1:
            json_str = text[start:end]  # 중괄호 안의 내용만 추출
            return json.loads(json_str)  # JSON 파싱 시도
        else:
            print("JSON 형식의 데이터를 찾을 수 없습니다.")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 실패: {e}")
        return None
    

def print_json_from_code (response):
    parsed_results = []    
    for res in response.data:
        for content in res.content:
            if content.type =='text':
                try:
                    print(f"{content.text.value}\n")
                    parsed_json = extract_json_from_text(content.text.value.strip())
                    if not parsed_json:  # 만약 문자열이 비어 있으면 건너뜀
                        print("비어 있는 메시지 발견, 건너뜀.")
                        continue
                    
                    results = parsed_json.get("results")
                    
                    if isinstance(results, list):
                        for item in results:
                            if item.get("vienna_code"):
                                parsed_results.append({
                                    "vienna_code": item.get("vienna_code"),
                                    "description": item.get("description"),
                                    "reason": item.get("reason")
                                })
                        return parsed_results
                    elif isinstance(results, dict)and "refused" in results:
                        parsed_results.append({
                            "refused": results.get("refused"),
                            "reason": results.get("reason"),
                        })
                        return parsed_results
                    elif isinstance(results, dict):
                        similarity_list = results.get("similarity", []) 
                        for item in similarity_list:    
                            parsed_results.append({
                                "niceNum":item.get("niceNum"),
                                "similarity_code":item.get("similarity_code"),
                                "info":item.get("info")
                            })
                        total_reason = results.get("total_reason")
                        total_results = {"similarity": parsed_results, "total_reason":total_reason}
                        return total_results
                    print(f"parsed_results : {parsed_results}")
                   
                except Exception as e:
                    print(f"예상치 못한 오류 발생: {e} - {content.text.value}")
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




async def handle_run_response_for_code(run, thread):
    try:
        run = await wait_on_run(run, thread)
        response = client.beta.threads.messages.list(thread_id=thread.id)
        messages= print_json_from_code(response)
        return messages
    except Exception as e :
        print(f"Error while handling run response: {e}")
        return None


# assistant의 실행 결과를 기다리고, 결과 메시지를 처리하는 함수
async def handle_run_response(run, thread, expect_json=True):
    try:
        # 실행 완료 대기
        run = await wait_on_run(run, thread)
        # 응답 받아오기
        response = client.beta.threads.messages.list(thread_id=thread.id)

        
        # 응답 메시지를 json형식으로 파싱할경우와 일반답변을 얻을경우 조건문
        if expect_json:
            messages = print_json_from_assistant(response)
        else:
            messages = print_message(response)
        return messages
    
    except Exception as e:
        print(f"Error while handling run response: {e}")
        return None