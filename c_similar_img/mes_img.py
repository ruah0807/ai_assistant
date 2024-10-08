import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ass_id = 'asst_FY8Yfek8H3CrJKSLX2OyWFB1'

async def submit_message_with_image(thread, user_message, image_path, image_url):
    content = [{'type': 'text', 'text': user_message}]

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
    
    
async def run_with_tools(ass_id, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools=[{'type':'file_search'}],
        instructions= """
            모든 텍스틀간의 검토가 끝난 후 
            반드시 문서에 있는 예시를 참고하여 상세한 종합의견을 내세요. 

            응답 형식 :     
            < 이미지 유사도 의견서 >    
            - 대상 상표 : 
                ![](original_image_url)
                (사용자가 업로드한 상표 이미지 묘사)
            - 선등록상표와 유사도 검토 의견: 
                상표이미지: ![](similar_image_url)
                출원/등록번호 : (application_number)
                상품류 : (classification_code)
                비엔나 코드 : (vienna_code)
                유사도 : (O - 유사, △ - 중간유사, X - 비유사 로 판단)
                검토의견 : [해당 이미지는 어떤 외관을 가지고 있는지 설명 후 사용자가 등록하고자 하는 이미지와의 유사성을 비교합니다.]
            - 종합의견 : [제시한(이미지 유사도 평가 방법)에 따라 각 이미지들을 비교하며 유사성을 1000자 이내로 설명하세요]
        """
    )
    print(f'assistant_id : {ass_id}, thread_id : {thread.id}, run_id : {run.id}')

    return run


# 새로운 스레드 생성 및 메시지 제출 함수
async def create_thread_and_run(user_input, image_path, image_url):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    await submit_message_with_image(thread, user_input, image_path, image_url)
    run = await run_with_tools(ass_id, thread)
    
    return thread, run



####################################################################################################


# brand_name = '온보더즈'
# similarity_code = 'S123101'
# vienna_code = ''
# brand_image_url = 'https://kipris.s3.ap-northeast-2.amazonaws.com/crople.png'
# brand_image_path = []
# # 유사이미지 검색 및 다운로드 처리
# download_image_paths = []
# all_responses = []

# ########################## 실행 ############################
# brand_image_path = save_file.download_image(brand_image_url)

# if brand_name:
#     # 비슷한 단어 찾기
#     similar_words = generate_similar_barnd_names(brand_name)
#     search_words = similar_words['words']
# else:
#     # brand_name이 없으면 기본 빈 리스트로 설정
#     search_words = []
    
# print(f"검색어: {search_words}, 유사성 코드: {similarity_code}, 비엔나 코드: {vienna_code}")
# # 분류코드와 비엔나 코드를 기반으로 상표 검색
# result_data = updated_search_results_for_image(search_words, similarity_code, vienna_code)

# # 등록 이미지와 유사 이미지를 비교하는 메시지 전송 (총 10번 반복)
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
#     image_url_pair = [brand_image_url, similar_image_url]

#     # 메시지를 생성 및 전송
#     user_message = f"등록하고자 하는 이미지 '{brand_name}'와(과) 유사성이 있을지 모르는 이미지 {idx + 1}입니다. \n 다음 정보는 등록되어있는 유사한 이미지의 정보입니다:\n출원번호:{application_number}, 분류코드:{classification_code}, 비엔나코드: {vienna_code}, 이미지URL: {similar_image_url}\n 두 이미지를 비교하여 유사도를 분석하여 법적 자문을 주세요."
#     thread, run = create_thread_and_run(user_message, image_pair, image_url_pair)

#     # 기다리는 로직 추가
#     run = wait_on_run(run, thread)
#     response = client.beta.threads.messages.list(thread_id=thread.id)
#     print_message(response)
#     all_responses.extend(response)

#     delete_downloaded_images(download_image_paths)

# save_messages_to_md(all_responses)