import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ass_id = 'asst_JQfJwI5N6CdoPMqQyAtTUptv'


async def submit_message_with_image(thread, user_message, image_path, image_url):
    content = [{'type': 'text', 'text': user_message}]

    #ThreadPoolExecutor를 사용하여 이미지 파일을 병렬로 업로드
    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, upload_image, local_image_path, original_image_url)
            for local_image_path, original_image_url in zip(image_path, image_url)
        ]
  
        uploaded_files = await asyncio.gather(*tasks)

    #업로드 완료된 파일을 메시지에 추가
    for file, original_image_url in uploaded_files:
        if file:
            content.append({'type': 'image_file', 'image_file': {'file_id': file.id}})
            content.append({'type': 'text', 'text': f'등록하려는 상표 URL: {original_image_url}'})  # 원본 이미지 URL 라벨링

    if content:
        # 이미지 파일 전송
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    else:
        print(f"Error : 이미지 파일 전송 실패 ")
    print(f"이미지 업로드 완료 . thread_id : {thread.id}")


def upload_image(local_image_path, original_image_url):
    print(f"Opening image file: {local_image_path}")  # 각 이미지 경로를 출력하여 확인
    try:
        with open(local_image_path, 'rb') as image_file:
            file =  client.files.create(file=image_file, purpose='vision') # 이미지 분석을 위한 용도
            return file, original_image_url
    except FileNotFoundError as e:
        print(f"Error: 파일을 찾을 수 없습니다. 경로: {local_image_path}. 에러: {str(e)}")
        return None, original_image_url   
    

async def run_with_tools(ass_id, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools=[{'type':'file_search'}],
        instructions= f"""
        '등록대상상표'는 한개이고. 유사검색된 '선등록상표'들은 한개에서 여러개가 될수있습니다. 각각의 기준을 세워비슷한 이미지를 찾아 json 형식으로 반환하세요.

        [평가 점수 기준]
        - 1점: 전혀 유사하지 않음
        - 2점: 거의 유사하지 않음
        - 3점: 약간의 유사성
        - 4점: 몇가지 유사성
        - 5점: 일부 유사성 있음
        - 6점: 꽤 유사
        - 7점: 전반적으로 유사
        - 8점: 거의 동일한 디자인
        - 9점: 매우 유사
        - 10점: 거의 동일하거나 구별이 어려움
        
        [ Context ]
            text_similarity_score : (텍스트 유사 점수 1점부터 10점 사이 판단) 
            image_similarity_score : (도형 유사 점수 1점부터 10점 사이 판단)

        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
async def similarity_create_thread_and_run(user_input, image_paths, image_urls):
    thread = await asyncio.to_thread(client.beta.threads.create)
    await submit_message_with_image(thread, user_input, image_paths, image_urls)
    run = await run_with_tools(ass_id, thread)
    return thread, run


######################## 유저 인풋 ##########################

# brand_name = ''
# similarity_code = 'S121002|S121001|S110101'
# vienna_code = '260301'
# brand_image_url = 'https://kipris.s3.ap-northeast-2.amazonaws.com/crople.png'
# # 유사이미지 검색 및 다운로드 처리
# download_image_paths = []
# all_responses = []

# ########################## 실행 ############################

# brand_image_path = download_image(brand_image_url)

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
#     thread, run = similarity_create_thread_and_run(user_message, image_pair, image_url_pair)

#     # 기다리는 로직 추가
#     run = common.wait_on_run(run, thread)
#     response = client.beta.threads.messages.list(thread_id=thread.id)
#     common.print_message(response)
#     all_responses.extend(response)

#     delete_downloaded_images(download_image_paths)

# save_messages_to_md(all_responses)