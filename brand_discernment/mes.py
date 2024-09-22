import os, sys, time, requests
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from brand_similarity.ass import ass_id
from init import client
from kipris_api import updated_search_results_for_image
from similar import generate_similar_barnd_names
from save_file import download_image_from_url


def submit_message_with_image(thread, user_message, image_path, image_url):
    content = [{'type': 'text', 'text': user_message}]

    # 메시지 전송
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    
    # 이미지 파일 전송 처리
    content = []

    for local_image_path, original_image_url in zip(image_path, image_url):
        print(f"Opening image file: {local_image_path}")  # 각 이미지 경로를 출력하여 확인
        try:
            with open(local_image_path, 'rb') as image_file:
                file = client.files.create(file=image_file, purpose='vision')  # 이미지 분석을 위한 용도
                # 이미지 파일과 함께 라벨을 텍스트로 추가
                content.append({'type': 'image_file', 'image_file': {'file_id': file.id}})
                content.append({'type': 'text', 'text': f'등록하려는 상표 URL: {original_image_url}'})  # 원본 이미지 URL 라벨링
        except FileNotFoundError as e:
            print(f"Error: 파일을 찾을 수 없습니다. 경로: {local_image_path}. 에러: {str(e)}")

    if content:
        # 이미지 파일 전송
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    else:
        print(f"Error : 이미지 파일 전송 실패 ")

    print(f"이미지 업로드 완료 . thread_id : {thread.id}")

    

def run_with_tools(ass_id, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools=  [{'type': 'file_search'}],
        instructions= """
        
        [ 상표 식별력 평가 방법 ]
        이미지 식별력 평가 방법에 대한 정보는 다음과 같은 기준을 적용할 수 있습니다:
        반드시 [상표심사기준202405.pdf]문서를 참고하여 법률 자문을 주세요(페이지 출처를 밝혀야합니다)
        
        다음과 같은 형식으로 작성해주세요 :

        ### 대상 상표: 
        ![이미지](original_image_url)
       
        ### 식별력 평가 :
        (문서를 참조하여 해당 법률 조항과 함께 등록하려는 대상상표의 식별력을 1000자 이내로 평가하세요)
        
        #### 출처 : 
        ---
        """
    )
    return run



def get_response(thread):
    # 스레드에서 메세지 목록가져오기
    return client.beta.threads.messages.list(thread_id=thread.id, order='asc')


# 새로운 스레드 생성 및 메시지 제출 함수
def create_thread_and_run(user_input, image_path, image_url):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    submit_message_with_image(thread, user_input, image_path, image_url)

    run = run_with_tools(ass_id, thread)
    
    return thread, run


# 메시지 출력용 함수
def print_message(response):
    for res in response:
        print(f'[{res.role.upper()}]')

        # res.content 안의 각 항목을 처리
        for content in res.content:
            # 텍스트일 경우
            if content.type == 'text':
                print(f"{content.text.value}\n")
            # 이미지 파일일 경우
            elif content.type == 'image_file':
                print(f"식별력 평가 대상 이미지 파일 ID: {content.image_file.file_id}\n")
        print("-" * 60)


# 실행 완료까지 대기하는 함수
def wait_on_run(run, thread, timeout=500):
    start_time = time.time()
    while run.status == 'queued' or run.status == 'in_progress':
        # 상태를 출력하여 디버깅
        print(f"현재 run 상태: {run.status}")
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id = run.id)
        # 일정 시간이 지나면 타임아웃 발생
        if time.time() - start_time > timeout:
            raise TimeoutError("Run이 지정된 시간 안에 완료되지 않았습니다.")
        time.sleep(0.5)
    return run



# 메시지들을 Markdown 파일로 저장하는 함수
def save_messages_to_md(responses, filename='assistant_response.md'):
    """
    responses : get_response 함수로부터 받은 메시지 리스트
    filename : 저장할 md 파일명
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for res in responses:
            # assistant의 응답만을 저장
            if res.role == 'assistant':
                for content in res.content:
                    if content.type == 'text':
                        f.write(f"{content.text.value}")
                f.write("\n\n---\n\n")
    print(f"Assistant의 응답이 {filename} 파일에 저장되었습니다.")


# 이미지 파일 삭제
def delete_downloaded_images(downloaded_image_paths):
    for image in downloaded_image_paths:
        try:
            os.remove(image)
            print(f"로컬에 저장된 이미지가 삭제되었습니다. : {image}")
        except OSError as e :
            print(f"이미지 삭제 실패 : {image}. 에러:{e}")
    


######################## 유저 인풋 ##########################

brand_name = ''
similarity_code = ''
vienna_code = ''
brand_image_url = 'https://kipris.s3.ap-northeast-2.amazonaws.com/crople.png'
# 유사이미지 검색 및 다운로드 처리
all_responses = []

########################## 실행 ############################

#대상상표의 이미지 다운로드 및 경로 담기
brand_image_path = download_image_from_url(brand_image_url)


# 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.
thread, run = create_thread_and_run(f"""
    업로드한 상표 이미지의 식별력을 평가해주세요.
    """, 
    image_path=brand_image_path)

run= wait_on_run(run, thread)
print_message(get_response(thread))



# # 등록 이미지와 유사 이미지를 비교하는 메시지 전송
# for idx, result in enumerate(result_data):

#     # result_data는 이미지 정보와 경로를 포함하므로, 여기서 추출
#     similar_image_path = result['image_path'] #유사 이미지 경로
#     similar_image_url = result['similar_image_url']
#     application_number = result['application_number'] # 출원번호
#     classification_code = result['classification_code']
#     vienna_code = result['vienna_code']

#     #다운로드 이미지 경로 저장
#     download_image_paths.append(similar_image_path)

#     image_pair = [brand_image_path, similar_image_path]  # 등록하려는 이미지와 유사 이미지 묶기
#     image_url_pair = [brand_image_url, similar_image_url]  # 원본 이미지 URL과 유사 이미지 URL
    
    
#     # 메시지를 생성 및 전송
#     user_message = f"등록하고자 하는 이미지와(과) 유사성이 있을지 모르는 이미지 {idx + 1}입니다.\n 이 정보는 이사건 등록상표 입니다.: {brand_image_url} \n 다음 정보는 등록되어있는 유사한 이미지의 정보입니다:\n출원번호:{application_number}, 분류코드:{classification_code}, 비엔나코드: {vienna_code}, 이미지URL: {similar_image_url}\n 두 이미지를 비교하여 유사도를 분석하여 법적 자문을 주세요."
#     thread, run = create_thread_and_run(user_message, image_pair, image_url_pair)

#     # 기다리는 로직 추가
#     run = wait_on_run(run, thread)
#     response = client.beta.threads.messages.list(thread_id=thread.id)
#     print_message(response)
#     all_responses.extend(response)

#     delete_downloaded_images(download_image_paths)

# save_messages_to_md(all_responses)