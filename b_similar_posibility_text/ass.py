### 유사 상표 찾기 필터링 Assistant ###

import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

ass_id = 'asst_9K4qGkDlEdDMQly5n08IQ6KD'

instructions = """
   당신은 사용자가 등록하려는 '등록대상상표'의 상표명을 비교하여 유사성이 있는 상표를 찾아내는 전문가입니다.
"""

### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    name= '유사 상표 TEXT Filtering Assistant',
    instructions = instructions,
    # tools =  [{'type': 'file_search'}],
    model ='gpt-4o-mini',
    temperature=0,
)

assistant_info = client.beta.assistants.retrieve(assistant_id=ass_id)
print(f"[현재 어시스턴트 정보]\n{assistant_info}")



###############################################################


# ## 백터스토어 생성및 파일 임베딩 업로드 ####
# vector_store = client.beta.vector_stores.create(
#     name = 'Similarity Code',
# )


# # #업로드할 파일들의 경로를 지정
# files_to_uploaded = [
#     '../_docs/similarity_code/24년_지정상품고시목록(출처포함)-표1.md',
#     '../_docs/similarity_code/35-구매대행업-표1.md',
#     '../_docs/similarity_code/35-도매업-표1.md',
#     '../_docs/similarity_code/35-소매업-표1.md',
#     '../_docs/similarity_code/35-중개업-표1.md',
#     '../_docs/similarity_code/35-판매대행업-표1.md',
#     '../_docs/similarity_code/35-판매알선업-표1.md'
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


# # vectorstore 삭제 ###
# vector_store = client.beta.vector_stores.delete(
#     vector_store_id='vs_4zYjMaJ286D2bEQfvRodjP1Y'
# )


###############################################################


## 벡터스토어 리스트 검색 ###
# vector_store_list = client.beta.vector_stores.list()

# for vectorstore in vector_store_list:
#     print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")




# 기존 어시스턴트 ID 확인
# assistant_list = client.beta.assistants.list()

# for assistant in assistant_list:
#     print(f"Assistant Name: {assistant.name}, Assistant ID: {assistant.id}")


