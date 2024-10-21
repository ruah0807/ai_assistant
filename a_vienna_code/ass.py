import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

ass_id = 'asst_5AAVBLsDY7vpCx7g4nVGe67R'

instructions = '''
[ Role ]
당신은 도형의 모양을 분석하는 AI 전문가 입니다.
사용자가 업로드하는 이미지의 도형을 분석하고, 해당되는 '도형 설명'을 문서에서 그대로 가져오세요. 
'''

# Vectorstore Name: 비엔나 코드 도형 설명, Vectorstore ID: vs_apE7367DjWeVFeFB9w1Gqom1
vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_apE7367DjWeVFeFB9w1Gqom1'
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


# # 백터스토어 생성및 파일 임베딩 업로드 ####
# vector_store = client.beta.vector_stores.create(
#     name = '비엔나 코드 도형 설명',
# )


# # #업로드할 파일들의 경로를 지정
# files_to_uploaded = [
#     '../_docs/example/vienna.md',
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
#     vector_store_id='vs_29PdeQVTdKwG6KaxiwgygMDo'
# )


###############################################################


### 벡터스토어 리스트 검색 ###
# vector_store_list = client.beta.vector_stores.list()

# for vectorstore in vector_store_list:
#     print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")



