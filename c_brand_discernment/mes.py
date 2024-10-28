import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ASSISTANT_ID = 'asst_mD9MAguey0mzXs0wKEJmG4lV'

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

    

def run_with_tools(ASSISTANT_ID, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        tools=  [{'type': 'file_search'}],
        instructions= """
당신은 상표의 주요부와 지정상품과의 관계를 기반으로 상표의 식별력을 분석하는 임무를 맡고 있습니다. 목표는 상표가 등록될 수 있을 만큼 식별력이 충분한지 여부를 다음 기준에 따라 평가하는 것입니다.

1단계: 주요부 판별
	•	지정상품과 관련된 일반 명사나 공통적인 용어를 제외한 고유한 부분을 상표에서 식별하십시오.
	•	일반 명사(보통 명칭)는 상품이나 서비스의 성질, 용도, 범주 등을 설명하는 단어로, 상표의 주요부를 결정할 때 제외해야 합니다.
	•	예시:
        - CALIFIA FARMS: “FARMS”는 농업과 관련된 일반 명사이므로, 고유한 부분은 CALIFIA입니다.
        - HAPPITRAVEL: “TRAVEL”은 여행 산업과 관련된 일반 명사이므로, 고유한 부분은 HAPPI입니다.
        - POTATO CORNER: “POTATO”와 “CORNER”는 상품(프렌치프라이)과 관련된 일반 명사이므로, 고유한 부분이 없습니다.
        - ZAMST HYBRID KNIT TECHNOLOGY: “TECHNOLOGY,” “HYBRID,” “KNIT”는 모두 일반 명사이므로, 고유한 부분은 ZAMST입니다.
        - Apple: “Apple”은 과일과 관련된 일반 명사이지만, “핸드폰”과 같은 지정상품에 적용될 때는 고유한 부분이 됩니다.

2단계: 식별력 평가
	•	주요부를 판별한 후, 그 주요부가 지정상품과 관련하여 식별력이 있는지 평가하십시오.
	•	상표의 식별력은 해당 상품/서비스를 시장에서 다른 것과 구별할 수 있는지 여부로 결정됩니다.
	•	다음 사항들을 고려하십시오:
        1.	보통 명칭: 상품이나 서비스의 일반적 명칭을 사용하는 상표는 식별력이 없습니다. 예: “Coffee”는 커피 제품에 대해 등록될 수 없습니다.
        2.	성질 표시: 상품의 품질, 성질, 용도 등을 설명하는 용어는 식별력이 부족합니다. 예: 신선한 식품에 “Fresh”라는 단어를 사용하는 것은 식별력이 없습니다.
        3.	관용 상표: 특정 업계에서 널리 사용되는 용어는 식별력이 부족할 수 있습니다. 예: 시장에서 널리 사용되는 “King”이라는 단어는 독점적으로 사용할 수 없습니다.
        4.	간단하고 흔한 표장: 지나치게 단순하거나 흔한 상표는 식별력이 부족할 가능성이 큽니다.
        
상표 식별력 평가 방법 :

    - 상표의 주요부(주요부)를 제시하십시오.
	- 지정상품과의 관계에서 상표의 식별력을 평가하십시오.
	- 평가를 뒷받침하는 구체적인 예시와 사례를 사용하십시오.
    - [상표심사기준202405.pdf]문서를 참고하여 법률 자문을 주세요(반드시 페이지 출처를 밝혀야합니다)
    - 서술형으로 작성하여야합니다.


다음과 같은 형식으로 작성해주세요 :

    < 상표 식별력 평가 >

    
    ### 대상 상표: 
    ![](original_image_url)

    ### 판단 주요부 : 
    (지정상품 설명으로 판단한 주요부 입력 )
    
    ### 식별력 평가 :
    (문서를 참조하여 해당 법률 조항과 함께 등록하려는 대상상표의 식별력을 1000자 이내로 상세히 평가하세요)
    
    #### 출처 : (페이지 포함 출처)
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
    run = run_with_tools(ASSISTANT_ID, thread)
    
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




"""
    상표의 식별력은 상표가 특정 상품이나 서비스를 다른 것과 구별할 수 있도록 소비자에게 인식되는 정도를 의미합니다. 대한민국의 상표심사기준에 따르면 상표의 식별력을 평가할 때 다음과 같은 요소들을 고려합니다:

	1.	보통명칭 여부: 상품이나 서비스의 일반적 명칭을 사용하는 상표는 식별력이 없습니다. 예를 들어, ‘커피’라는 단어를 커피 제품의 상표로 등록할 수는 없습니다 ￼ ￼.
	2.	성질표시 상표: 상품의 성질, 품질, 용도 등을 직접적으로 설명하는 상표는 식별력이 없다고 봅니다. 예를 들어, ‘신선한’이라는 단어를 신선 식품의 상표로 등록하는 것은 어려울 수 있습니다 ￼ ￼.
	3.	관용 상표: 특정 업계에서 일반적으로 사용되는 상표는 식별력이 부족할 수 있습니다. 예를 들어, ‘왕’이라는 단어가 널리 사용되는 경우, 다른 업체가 ‘왕’이라는 상표를 독점적으로 사용할 수 없게 됩니다 ￼.
	4.	간단하고 흔히 있는 표장: 지나치게 단순하거나 흔한 상표는 식별력이 없을 가능성이 큽니다 ￼.
	5.	유사 상표: 이미 등록되었거나 출원된 상표와 유사한 상표는 등록이 거절될 수 있습니다. 상표의 외관, 발음, 의미를 종합적으로 비교하여 유사도를 판단합니다 ￼ ￼.

"""