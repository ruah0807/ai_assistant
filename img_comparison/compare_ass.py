### 유사 상표 찾기 필터링 Assistant ###

import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

ass_id = 'asst_JQfJwI5N6CdoPMqQyAtTUptv'


instructions = """
[ Role ]
   당신은 사용자가 등록하려는 [등록대상상표]의 유사한 상표명이나 이미지의 도형을 비교하여 점수를 매기는 전문가 입니다. 

[ Given ]
    사용자의 등록대상상표 이미지, 상표이름.
    유사한 선등록상표 이미지와 상표이름.
   
[ Context ]
    1. 텍스트 유사 점수: 0~10 사이 판단

    2. 텍스트+도형 유사 점수 : 0~10 사이 판단
    
    3. 이미지 도형 유사 점수: 0~10 사이 판단
    
"""


### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    name= '유사 상표 IMAGE SCORE Assistant',
    instructions = instructions,
    tools =  [{'type': 'file_search'}],
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
#     '../docs/example/상표심사기준202405.pdf',
#     '../docs/example/상표유사여부보고서(예시).md',
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


## vectorstore 삭제 ###
# vector_store = client.beta.vector_stores.delete(
#     vector_store_id='vs_iuSR8xFYdZML64ycdt8TC6BW'
# )


###############################################################


# ## 벡터스토어 리스트 검색 ###
# vector_store_list = client.beta.vector_stores.list()

# for vectorstore in vector_store_list:
#     print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")



