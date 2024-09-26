import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ass_id = 'asst_t6EJ7fG2GebmCD7PNg3o8M5d'

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
        tools=  [{'type': 'file_search'}],
        instructions= """
        유사도 평가 방법에 대한 정보는 다음과 같은 기준을 적용할 수 있습니다:
        반드시 [상표심사기준202405.pdf]문서를 참고하여 [상표유사여부보고서형식(예시).md]형식으로 대답하세요(출처를 밝혀야합니다)
        상표의 유사 여부에 대한 최종 검토의견을 1000자 이내로 설명하세요.
        
        다음과 같은 형식으로 작성해주세요 :

        < 상표 유사여부 보고서 >
        
        ### 이 사건 등록 상표 : 
        ![](original_image_url)
        ### 선등록상표 : 
        ![](similar_image_url)
        **출원번호** : (applicationNumber)
        
        #### 검토의견
        **외관 비교**:
            상표의 디자인, 색상, 글자체, 도안 등을 기반으로 두 상표가 시각적으로 얼마나 유사한지 분석해주세요. 특히 상표의 글자 모양, 배치, 색상과 같은 시각적 요소를 중심으로 구체적으로 설명해주세요.
        **관념 비교**:
            상표가 전달하는 의미나 개념을 비교해주세요. 상표가 특정한 의미가 있는지, 아니면 **조어(임의로 만든 단어)**인지를 명확히 분석하고, 의미적 차이를 설명해주세요.
        **호칭 비교**:
            두 상표가 발음될 때 음절별로 어떻게 발음되는지 비교해주세요. 각 상표의 발음법, 첫 음절과 마지막 음절의 차이점을 분석하고, 발음 시 느껴지는 청각적 유사성 또는 차이를 명확히 설명해주세요.
        **최종의견** :
            (상표심사기준을 참고한 출처포함 종합의견 작성)
        ---
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