import os, sys, time, requests
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from ass_similar import ass_id
from init import client
from kipris_api import updated_search_results_for_image
from similar import generate_similar_barnd_names
from io import BytesIO
from PIL import Image



# 이미지 url로부터 다운로드하고 파일로 저장하는 함수
def download_image_with_application_number(image_url, application_number):
    # 이미지 url 내에서 이미지 다운로드
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # 디렉토리 경로 설정 (상대 경로를 절대 경로로 변환)
    save_dir = os.path.abspath('../similar_img')
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"디렉토리 생성됨: {save_dir}")
    
    # 파일 경로 설정
    image_filename = os.path.join(save_dir, f'출원번호_{application_number}.png')
    
    # 이미지 저장
    img.save(image_filename)
    print(f'이미지가 {image_filename}으로 저장되었습니다.')
    return image_filename



def submit_message(ass_id, thread, user_message, image_path):
    content = [{'type': 'text', 'text': user_message}]

    # 디버깅용: image_path를 출력하여 확인
    print(f"Received image_path: {image_path}")  # 여기서 image_path 값 확인
    
    # 메시지 전송

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
         [ Role ]
          당신은 상표등록을 위한 '이미지 유사도 분석가' 입니다. 텍스트는 평가 하지 않습니다.

         [ Context ]
            •	[이미지 유사도 평가 방법]을 참고하여 상표 이미지의 유사성을 평가.
            •	관련 법률 조항을 통해 유사성이 얼마나 있는지를 법률기반으로 상세히 설명.

        [ 이미지 유사도 평가 방법 ]
            이미지 유사도 평가 방법에 대한 정보는 다음과 같은 기준을 적용할 수 있습니다:

            1.	외관의 유사성:
            •	외관상의 형상을 시각적으로 관찰하여 서로 오인·혼동을 일으킬 염려가 있는지 여부로 판단합니다. 특히 직관적으로 관찰하여 유사성을 판단하는 것이 원칙입니다.
            •	주로 기호, 도형, 입체적 형상, 그리고 색채를 결합한 상표에 적용되며, 문자의 구성과 형태도 고려하여 외관의 유사성을 평가합니다 .
            2.	위치상표의 유사성:
            •	위치상표의 경우, 표시된 위치, 표장의 모양, 각도 등의 유사성을 고려하여 출처의 오인 또는 혼동 가능성이 있는지 여부로 판단합니다 .

        이 기준들은 이미지 유사성을 판단할 때, 시각적으로 나타나는 형상과 모양, 위치, 각도 등 다양한 외관적 요소들을 중심으로 평가하는 방법입니다.

        [ dialog flow ]
            1.	상표 이미지 업로드 1개 :
                - 사용자가 등록하고자 하는 1개의 이미지를 분석합니다. (잘 기억해두어야합니다.)
            2.	유사한 10개의 이미지들 업로드 : 
                - 유사성이 있는 10개의 이미지들을 사용자가 처음으로 올린 이미지와 대조해가며 유사성을 분석합니다.
            3.	상표심사기준 적용:
                - 사용자가 등록하고자 하는 상표 이미지와, 두번째로 올린 유사한 이미지들울 비교 분석합니다.
            각각의 상표 이미지를 사용자가 등록하고자하는 이미지와 비교하여 유사성을 평가합니다:
                    - 대상 상표 : 
                        (사용자가 업로드한 상표 이미지 묘사)
                    - 검토의견: 상표의 유사성을 각각 평가.
                        상품류: (claasificationCode)
                        상표이미지: (bigDrawing) - url
                        출원/등록번호 : (applicationNumber)
                        유사도 : (O,△,X 로 판단)
                        검토의견 : [해당 이미지는 어떤 외관을 가지고 있는지 설명 후 사용자가 등록하고자 하는 이미지와의 유사성을 비교합니다.]
                    - 종합의견 : [제시한(이미지 유사도 평가 방법)에 따라 각 이미지들을 비교하며 유사성을 상세히 설명하세요]


        [ Constraints ]
            •	상표명(텍스트)는 평가하지 않고, 상표의 이미지 유사도만 평가합니다.
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





######################## 유저 인풋 ##########################

brand_name = '시민언론시선' #<==입력을 받는다고 가정
similarity_code = 'S0601'
brand_image_path = ['/Users/ainomis_dev/Desktop/ainomis/ai_assistant/brand_img/[비추천]시민언론시선_38.png']
searched_image_paths = []




########################## 실행 ############################

#비슷한 단어 찾기
similar_words = generate_similar_barnd_names(brand_name)
# 분류코드와 비슷한단어로 상표 검색
result_data= updated_search_results_for_image(similar_words['words'], similarity_code)

# 검색된 이미지 url로부터 이미지를 다운로드하여 저장
for result in result_data:
    image_url= result[0].get('상표이미지')
    application_number = result[0].get('출원/등록번호')
    if image_url and application_number:
        # 이미지 다운로드 및 저장 후 경로를 배열에 추가
        filename = download_image_with_application_number(image_url, application_number)
        searched_image_paths.append(filename)



# 등록 이미지와 유사 이미지를 비교하는 메시지 전송 (총 10번 반복)
for idx, similar_image in enumerate(searched_image_paths):
    if idx >= 10:
        break  # 10개의 메시지만 생성

    image_pair = [brand_image_path[0], similar_image]  # 등록하려는 이미지와 유사 이미지 묶기

    # 메시지를 생성 및 전송
    user_message = f"등록하고자 하는 이미지 '{brand_name}'와 유사성이 있을지 모르는 이미지 {idx + 1}입니다. 두 이미지를 비교하여 유사도를 분석해 주세요."
    thread, run = create_thread_and_run(user_message, image_pair)

    # 기다리는 로직 추가
    run = wait_on_run(run, thread)
    print_message(get_response(thread))




# 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.

# thread, run = create_thread_and_run(
#     f"""
#     제가 등록하고 싶은 {brand_name}라는 이름의 상표 이미지입니다. 상표 등록을 위해 사용할 이미지인데 어떤가요?
    
#     """, image_path=brand_image_path
#     )# json데이터를 보낼것.

# run = wait_on_run(run, thread)
# print_message(get_response(thread))


# run = send_message_in_same_thread(
#     thread, 
#     f"""
#     이것들은 특허청에서 비슷한 상표를 검색한 이미지들입니다. 각이미지의 제목은 출원번호 이고, 각각의 이미지를 분석하고 사용자가 등록하려는 상표 이미지와의 유사도를 instructions에 따라 전문가처럼 디테일하게 설명합니다\n\n{result_data} .
#     """, image_path=searched_image_paths
# )

# run = wait_on_run(run, thread)
# print_message(get_response(thread))

# 세 번째 스레드를 마친 후 감사 인사 전송
# thread, run = submit_message(thread, '고마워요')  # run3이 완료된 후 메시지 전송

# run = wait_on_run(run, thread)  # 완료될 때까지 대기
# print_message(get_response(thread))


