import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

ass_id = 'asst_5AAVBLsDY7vpCx7g4nVGe67R'

instructions = '''
[ Role ]
비엔나 분류(파리조약 가입국들이 상표에 포함된 도형요소를 일관되게 분류해서 데이터베이스를 구축할 목적으로 만든 "Vienna Agreement"에 따라서 만든 도형상표 분류 기준)를 분석하고 찾아내는 분석가 입니다.
'''

vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_QtSniSyyBiMQ8P8AJYONaBJq'
)

### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    name= '비엔나코드 추측 전문가',
    instructions = instructions,
    model ='gpt-4o',
    tools =  [{'type': 'file_search'}],
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    temperature=0.56,
    top_p= 0.9
)

assistant_info = client.beta.assistants.retrieve(assistant_id=ass_id)
print(f"[현재 어시스턴트 정보]\n{assistant_info}")






###############################################################


### 백터스토어 생성및 파일 임베딩 업로드 ####
# vector_store = client.beta.vector_stores.create(
#     name = 'Vienna Code',
# )


# # #업로드할 파일들의 경로를 지정
# files_to_uploaded = [
#     '../_docs/example/vienna_code.md',
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


## 벡터스토어 리스트 검색 ###
# vector_store_list = client.beta.vector_stores.list()

# for vectorstore in vector_store_list:
#     print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")



