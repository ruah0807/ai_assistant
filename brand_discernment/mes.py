import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ass_id = 'asst_mD9MAguey0mzXs0wKEJmG4lV'

def submit_message_with_image(thread, user_message, image_path, image_url):
    content = [{'type': 'text', 'text': user_message}]

    print(f"Opening image file: {image_path}")  # 각 이미지 경로를 출력하여 확인
    try:
        with open(image_path, 'rb') as image_file:
            file = client.files.create(file=image_file, purpose='vision')  # 이미지 분석을 위한 용도
            # 이미지 파일과 함께 라벨을 텍스트로 추가
            content.append({'type': 'image_file', 'image_file': {'file_id': file.id}})
            content.append({'type': 'text', 'text': f'등록하려는 상표 URL: {image_url}'})  # 원본 이미지 URL 라벨링
    except FileNotFoundError as e:
        print(f"Error: 파일을 찾을 수 없습니다. 경로: {image_path}. 에러: {str(e)}")

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
        - [상표심사기준202405.pdf]문서를 참고하여 법률 자문을 주세요(반드시 페이지 출처를 밝혀야합니다)
        - 서술형으로 작성하여야합니다.
        - 다음과 같은 형식으로 작성해주세요 :

        < 상표 식별력 평가 >
        ### 대상 상표: 
        ![](original_image_url)
       
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
def discernment_create_thread_and_run(user_input, image_path, image_url):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    submit_message_with_image(thread, user_input, image_path, image_url)
    run = run_with_tools(ass_id, thread)
    
    return thread, run



# from kipris_api import updated_search_results_for_image
# from similar import generate_similar_barnd_names
# from save_file import download_image

# 메시지들을 Markdown 파일로 저장하는 함수
# def save_messages_to_md(responses, filename='assistant_response.md'):
#     """
#     responses : get_response 함수로부터 받은 메시지 리스트
#     filename : 저장할 md 파일명
#     """
#     with open(filename, 'w', encoding='utf-8') as f:
#         for res in responses:
#             # assistant의 응답만을 저장
#             if res.role == 'assistant':
#                 for content in res.content:
#                     if content.type == 'text':
#                         f.write(f"{content.text.value}")
#                 f.write("\n\n---\n\n")
#     print(f"Assistant의 응답이 {filename} 파일에 저장되었습니다.")




# ######################## 유저 인풋 ##########################

# brand_name = 'crople'
# brand_image_url = 'https://kipris.s3.ap-northeast-2.amazonaws.com/crople.png'

# #대상상표의 이미지 다운로드 및 경로 담기
# brand_image_path = download_image(brand_image_url)


# ########################## 실행 ############################

# # 스래드 생성
# thread, run = create_thread_and_run(
#     f"""
#     업로드한 이미지 상표 '{brand_name}'의 상표 식별력을 평가해주세요.
#     """, 
#     image_path=brand_image_path, 
#     image_url= brand_image_url
#     )

# run= wait_on_run(run, thread)
# print_message(get_response(thread))


