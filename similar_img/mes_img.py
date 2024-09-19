import os, sys, time, requests
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from ass_img import ass_id
from init import client
from kipris_api import updated_search_results_for_image
from similar import generate_similar_barnd_names


def submit_message(ass_id, thread, user_message, image_path):
    content = [{'type': 'text', 'text': user_message}]

    # 디버깅용: image_path를 출력하여 확인
    print(f"Received image_path: {image_path}")  # 여기서 image_path 값 확인
    
    # 메시지 전송
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )
    
    # 이미지 파일 전송 처리
    MAX_CONTENT_LENGTH = 10  # 한 번에 전송할 수 있는 최대 content 개수
    for i in range(0, len(image_path), MAX_CONTENT_LENGTH - 1):
        batch = image_path[i:i + MAX_CONTENT_LENGTH - 1]  # 최대 9개의 이미지로 나눔
        content = []

        for image in batch:
            print(f"Opening image file: {image}")  # 각 이미지 경로를 출력하여 확인
            try:
                with open(image, 'rb') as image_file:
                    file = client.files.create(
                        file=image_file,
                        purpose='vision'  # 이미지 분석을 위한 용도
                    )
                    content.append({
                        'type': 'image_file',
                        'image_file': {'file_id': file.id}
                    })
            except FileNotFoundError as e:
                print(f"Error: 파일을 찾을 수 없습니다. 경로: {image}. 에러: {str(e)}")


        # 이미지 파일 전송
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=content
        )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools=[],
        instructions= """
         응답 형식:
            - 대상 상표 : 
                (사용자가 업로드한 상표 이미지 묘사)
            - 검토의견: 상표의 유사성을 각각 평가.
                상표이미지: (image_url) - url
                출원/등록번호 : (application_number)
                상품류 : (classification_code)
                유사도 : (O,△,X 로 판단)
                검토의견 : [해당 이미지는 어떤 외관을 가지고 있는지 설명 후 사용자가 등록하고자 하는 이미지와의 유사성을 비교합니다.]
            - 종합의견 : [제시한(이미지 유사도 평가 방법)에 따라 각 이미지들을 비교하며 유사성을 상세히 설명하세요]
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
def create_thread_and_run(user_input, image_path):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    run = submit_message(ass_id, thread, user_input, image_path)
    return thread, run



def send_message_in_same_thread(thread, user_message, image_path):
    # 메시지 전송
    run = submit_message(ass_id, thread, user_message, image_path)
    return run



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
                print(f"이미지 파일 ID: {content.image_file.file_id}\n")

        print("-" * 60)


#반복문에서 대기하는 함수
def wait_on_run(run, thread, timeout=500):
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


# 이미지 파일 삭제
def delete_downloaded_images(downloaded_image_paths):
    for image in downloaded_image_paths:
        try:
            os.remove(image)
            print(f"로컬에 저장된 이미지가 삭제되었습니다. : {image}")
        except OSError as e :
            print(f"이미지 삭제 실패 : {image}. 에러:{e}")


######################## 유저 인풋 ##########################

brand_name = '온보더즈' #<==입력을 받는다고 가정
similarity_code = 'S0101'
brand_image_path = ['/Users/ainomis_dev/Desktop/ainomis/ai_assistant/img/brand_img/[추천]온보더즈.png']
searched_image_paths = []




########################## 실행 ############################

# 유사이미지 검색 및 다운로드 처리
download_image_paths = []

#비슷한 단어 찾기
similar_words = generate_similar_barnd_names(brand_name)
# 분류코드와 비슷한단어로 상표 검색
result_data= updated_search_results_for_image(similar_words['words'], similarity_code)


# 등록 이미지와 유사 이미지를 비교하는 메시지 전송 (총 10번 반복)
for idx, result in enumerate(result_data):
    if idx >= 10:
        break  # 10개의 메시지만 생성

    # result_data는 이미지 정보와 경로를 포함하므로, 여기서 추출
    similar_image_path = result['image_path'] #유사 이미지 경로
    application_number = result['application_number'] # 출원번호
    classification_code = result['classification_code']
    image_url = result['image_url']

    #다운로드 이미지 경로 저장
    download_image_paths.append(similar_image_path)

    image_pair = [brand_image_path[0], similar_image_path]  # 등록하려는 이미지와 유사 이미지 묶기

    # 메시지를 생성 및 전송
    user_message = f"등록하고자 하는 이미지 '{brand_name}'와(과) 유사성이 있을지 모르는 이미지 {idx + 1}입니다. \n 다음 정보는 등록되어있는 유사한 이미지의 정보입니다:\n출원번호:{application_number}, 분류코드:{classification_code}, 이미지URL: {image_url}\n 두 이미지를 비교하여 유사도를 분석하여 법적 자문을 주세요."
    thread, run = create_thread_and_run(user_message, image_pair)

    # 기다리는 로직 추가
    run = wait_on_run(run, thread)
    print_message(get_response(thread))

    delete_downloaded_images(download_image_paths)

