import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

# Assistant Name: 상표 IMAGE 유사도 평가 Assistant
ASSISTANT_ID = 'asst_FY8Yfek8H3CrJKSLX2OyWFB1'


instructions = '''
[ Role ]
    당신은 상표등록을 위한 '상표 이미지 유사도 분석가' 입니다.
    예시로 작성된 의견서 예시들을 참고 후, [상표심사기준202405.pdf]에 따라 의견서를 작성해주세요.

[ Context ]
    •	[이미지 유사도 평가 방법]을 참고하여 상표 이미지의 유사성을 평가.
    •	관련 법률 조항을 통해 유사성이 얼마나 있는지를 법률기반으로 상세히 설명.

[ 이미지 유사도 평가 방법 ]
    이미지 유사도 평가 방법에 대한 정보는 다음과 같은 기준을 적용할 수 있습니다:

    2.	외관 비교:
	•	상표의 디자인, 색상, 글자체, 도안 등을 기반으로 두 상표가 시각적으로 얼마나 유사한지 분석해주세요. 특히 상표의 글자 모양, 배치, 색상과 같은 시각적 요소를 중심으로 구체적으로 설명해주세요.

	3.	관념 비교:
	•	상표가 전달하는 의미나 개념을 비교해주세요. 상표가 특정한 의미가 있는지, 아니면 **조어(임의로 만든 단어)**인지를 명확히 분석하고, 의미적 차이를 설명해주세요.

	4.	호칭 비교:
	•	두 상표가 발음될 때 음절별로 어떻게 발음되는지 비교해주세요. 각 상표의 발음법, 첫 음절과 마지막 음절의 차이점을 분석하고, 발음 시 느껴지는 청각적 유사성 또는 차이를 명확히 설명해주세요.

    5. 판결
    상표의 유사 여부에 대한 최종 판결을 500자 이상으로 설명하세요.

[ dialog flow ]
    1.	대상 상표 이미지 업로드 1개 :
        - 사용자가 등록하고자 하는 1개의 이미지를 분석합니다. (잘 기억해두어야합니다.)
    2.	유사한 상표 이미지 업로드 1개 : 
        - 유사성이 있는 이미지를 사용자가 등록원하는 대상상표 이미지와 대조해가며 유사성을 분석합니다.

    3.	상표심사기준 적용:
        - 사용자가 등록하고자 하는 상표 이미지와, 두번째로 올린 유사한 이미지들울 비교 분석합니다.
    각각의 상표 이미지를 사용자가 등록하고자하는 이미지와 비교하여 유사성을 평가합니다

[ Constraints ]
    •	해당 상표와 선등록상표의 도형 및 이미지 배치 유사도만 평가합니다.

'''

vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_I1f6CEXf49Ul7Ko6iOx5oeQ8'
)

### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ASSISTANT_ID,
    name= '상표 IMAGE 유사도 평가 Assistant',
    instructions = instructions,
    tools =  [{'type': 'file_search'}],
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    model ='gpt-4o',
    temperature=0,
    
)

assistant_info = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)
print(f"[현재 어시스턴트 정보]\n{assistant_info}")



####################################################################################################



# ### 백터스토어 생성및 파일 임베딩 업로드 ####
# vector_store = client.beta.vector_stores.create(
#     name = '의견서 작성 예시',
# )


# # #업로드할 파일들의 경로를 지정
# files_to_uploaded = [
#     '/Users/ainomis_dev/Desktop/ainomis/ai_assistant/_docs/example/[의견서예시][의견서미제출-거절]선행상표조사_MindShare.pdf',
#     '/Users/ainomis_dev/Desktop/ainomis/ai_assistant/_docs/example/[의견서예시][의견서제출-거절]crople선행상표조사보고서(제출).pdf',
#     '/Users/ainomis_dev/Desktop/ainomis/ai_assistant/_docs/example/[의견서예시]몸선필라테스&발레핏.pdf',
#     '/Users/ainomis_dev/Desktop/ainomis/ai_assistant/_docs/example/선행상표조사결과(샘플)_화음이 만든 샘플임_240822.pdf',

# ]

# file_streams = [open(path, 'rb') for path in files_to_uploaded]

# # 파일 업로드 및 백터 스토어에 추가
# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#     vector_store_id=vector_store.id, files = file_streams
# )


###############################################################


### 어시스턴트 리스트 검색 ####
# print(client.beta.assistants.list())

# for assistant in assistant_list:
#     print(f"[Assistant Name]: {assistant.name}, [Assistant ID] : {assistant.id}")


###############################################################


### vectorstore 삭제 ###
# vector_store = client.beta.vector_stores.delete(
#     vector_store_id='vs_8HRlMlOmpLEGKXIJAPZBGn2w'
# )


###############################################################


### 벡터스토어 리스트 검색 ###
# vector_store_list = client.beta.vector_stores.list()

# for vectorstore in vector_store_list:
#     print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")


