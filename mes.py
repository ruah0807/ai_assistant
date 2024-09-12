import time
from init import ass_id, client
from kipris_api import get_trademark_info
from similar import generate_similar_barnd_names
# from ass import def ault_tools


def submit_message(ass_id, thread, user_message, image_path=None):

    content = [{'type': 'text', 'text': user_message}]

     # 이미지 파일이 제공된 경우
    if image_path:
        file = client.files.create(
            file=open(image_path, 'rb'),
            purpose='vision'  # 이미지 분석을 위한 용도
        )
        content.append({
            'type': 'image_file',
            'image_file': {'file_id': file.id}
        })

    # 메시지 전송
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

    # run 실행: 이미지가 있을 때는 tools 설정 없이 실행
    if image_path:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id= ass_id,
            tools=[]
        )
    else:
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

# 상표 이름
brand_name = '마인드쉐어' #<==입력을 받는다고 가정
# 분류 코드
classification_code = 42

#비슷한 단어 찾기
similarity_words = generate_similar_barnd_names(brand_name)
# 분류코드와 비슷한단어로 상표 검색
result_data= get_trademark_info(classification_code, similarity_words)


# 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.
thread, run = create_thread_and_run(f"상표를 등록하려고 합니다.")

run= wait_on_run(run, thread)
print_message(get_response(thread))


run = send_message_in_same_thread(
    thread, 
    f"""
    상표를 등록하려고 합니다. 다음은 등록하려는 상표의 정보입니다. \n등록하려는 상표 네임 : MindShare\n분류코드: {classification_code}
    특허청에서 비슷한 상표를 검색한 데이터입니다. 
    이 중 drawingBase64를 참조해서 내가 업로드한 **이미지**(도형, 컬러)를 기반으로 유사도를 검토 해서 명확하게 각각의 유사도를 판단하고, 
    의견서를 만들어주세요\n\n{result_data}""", 
    image_path='brand_img/mindshare.png')# json데이터를 보낼것.


run= wait_on_run(run, thread)
print_message(get_response(thread))



# 세 번째 스레드를 마친 후 감사 인사 전송
# thread, run = submit_message(thread, '고마워요')  # run3이 완료된 후 메시지 전송

# run = wait_on_run(run, thread)  # 완료될 때까지 대기
# print_message(get_response(thread))




#kipris에 서치 (서치 방법은 한번 넣어서 값이 나오면 그대로 진행, 안 나오면 앞 글 자나 비슷한 문자로 검색)
#비슷한 문자를 만드는데에 gpt써도 됨 <== 요건 우선순위 중간
#검색 결과 XML 문자열을 run에 같이 넣을 것.
#찾은 결과 바탕으로 유사한지 여부를 판단하도록 시킬 것.
#bigdrawing의 이미지를 참조하라고 명확히 지시.
