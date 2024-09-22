import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

# Assistant Name: 상표 TEXT 유사도 평가 Assistant
ass_id = 'asst_IbYT7EatQkmSnremkg5RuiC0'


default_tools = [
        {'type': 'code_interpreter'},
        {'type': 'file_search'},
    ]

instructions = '''
[ Role ]
    당신은 상표 등록을 위한 '텍스트 유사도 분석가' 입니다. 

[ Context ]
    •	업로드된 문서기반으로 상표의 텍스트 유사성을 평가.
    •	관련 법률 조항을 통해 유사성이 얼마나 있는지를 법률기반으로 상세히 설명.

[ dialog flow ]
    1.	상표 입력 요청:
        - 사용자가 상표의 텍스트를 입력합니다.
    2.	상표 분석
    3.	상표심사기준 적용:
        - vectorstore에 업로드된 [상표심사기준202405.pdf]을 기준으로 각각 상표의 유사성을 평가하고 설명합니다.
    각각의 상표 텍스트를 비교하여 얼마나 비슷한지를 평가합니다.

[ Constraints ]
    •	영어발음을 그대로 쓴것과, 영어의 번역 버전을 한국어로 쓴것은 다르다고 판단합니다.
    •	반드시 백터 데이터베이스에 업로드된 상표심사기준202405.pdf 파일을 참고하여 법적근거의 소스를 밝혀야합니다.
'''


vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_rLXYrSoCNE7aNpLI6cBGPseN'
)


### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    name='상표 TEXT 유사도 평가 Assistant',
    instructions = instructions,
    tools = default_tools,
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    # model ='gpt-4o-2024-08-06',
    model ='gpt-4o',
    temperature=0,
    
)

assistant_info = client.beta.assistants.retrieve(assistant_id=ass_id)
print(f"[현재 어시스턴트 정보]\n{assistant_info}")








###############################################################


# ### 백터스토어 생성및 파일 임베딩 업로드 ####
# vector_store = client.beta.vector_stores.create(
#     name = '상표심사기준202405',
# )


# # #업로드할 파일들의 경로를 지정
# files_to_uploaded = [
#     '../docs/상표심사기준202405.pdf',

# ]

# file_streams = [open(path, 'rb') for path in files_to_uploaded]

# # 파일 업로드 및 백터 스토어에 추가
# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#     vector_store_id=vector_store.id, files = file_streams
# )


###############################################################


## 어시스턴트 리스트 검색 ####
assistant_list = client.beta.assistants.list()

for assistant in assistant_list:
    print(f"[Assistant Name]: {assistant.name}, [Assistant ID] : {assistant.id}")


###############################################################


# ## vectorstore 삭제 ###
# vector_store = client.beta.vector_stores.delete(
#     vector_store_id='vs_8HRlMlOmpLEGKXIJAPZBGn2w'
# )


###############################################################


# ## 벡터스토어 리스트 검색 ###
# vector_store_list = client.beta.vector_stores.list()

# for vectorstore in vector_store_list:
#     print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")


