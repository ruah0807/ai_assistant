import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

ass_id = 'asst_FY8Yfek8H3CrJKSLX2OyWFB1'


def return_ai_company():
    return '(주)에이아이노미스'

function_schema={
    'name' : 'return_ai_nomis',
    'description' : "모든 응답 마지막에 반환한 문자열 문구를 추가합니다",
    'parameters':{
        'type': 'object',
        'properties': {},
        'additionalProperties':False
    },
    'strict': True # 모든 응답에서 호출되도록
}

default_tools = [
        {'type': 'code_interpreter'},
        {'type': 'file_search'},
        {'type': 'function', 'function': function_schema}
    ]

instructions = '''
상표 유사도 평가 AI는 제시된 상표명의 텍스트 혹은 이미지를 분석하여 주어진 유사 데이터들을 이용하여 유사성을 판단하는 전문가입니다.
- 텍스트 유사도는 반드시 업로드된 문서기반으로 평가하여 출처를 내놓아야합니다. 
- 이미지 유사도는 사용자가 제시한 이미지와 유사도를 평가해야합니다.

'''



vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_lnyjqbRPhkqR5RkQ3Y3pdiN1'
)



### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
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


#### 백터스토어 생성및 파일 임베딩 업로드 ####
# vector_store = client.beta.vector_stores.create(
#     name = '상표 식별 documents',
# )


# # #업로드할 파일들의 경로를 지정
# files_to_uploaded = [
#     '../docs/상표검색 프로세스.pdf',
#     '../docs/상표심사기준202405.pdf',
#     '../docs/선행상표조사결과(샘플)_화음이 만든 샘플임_240822.pdf',
#     '../docs/상표유사여부보고서(별책).pdf',

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


