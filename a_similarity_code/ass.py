import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from dotenv import load_dotenv
from init import client

load_dotenv()

ass_id = 'asst_W8YP62HfQPvHsKFavgndRJ1T'

instructions = """
[ Role ]
당신은 similarityCode를 분석하는 전문가 입니다. 문서를 기반으로하여 해당 유사코드를 추측하고 답변하세요.
"""

vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_n45uaYmRy4Em5BxJA6AFDZFr'
)
# # [ Similarity Code Batch Ver.] - vs_0dJoKkouQ6Qa7HbczRnwC1VG
# # [ Similarity Code ] -  vs_72qRAe3yFTBvAP1XP305J9e0

### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    name= '유사코드 추측 전문가',
    instructions = instructions,
    model ='gpt-4o',
    tools =  [{'type': 'file_search'}],
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    temperature=0,
    top_p= 0.9
)

assistant_info = client.beta.assistants.retrieve(assistant_id=ass_id)
print(f"[현재 어시스턴트 정보]\n{assistant_info}")



###############################################################


# ## 백터스토어 생성및 파일 임베딩 업로드 ####
# vector_store = client.beta.vector_stores.create(
#     name = 'Similarity Code Document',
# )


# # #업로드할 파일들의 경로를 지정
# files_to_uploaded = [
#     "/Users/ainomis_dev/Desktop/ainomis/ai_assistant/_docs/similarity_code/trademark_class.md"
# ]

# file_streams = [open(path, 'rb') for path in files_to_uploaded]

# # 파일 업로드 및 백터 스토어에 추가
# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#     vector_store_id=vector_store.id, files = file_streams
# )



###############################################################

# ### vectorstore 삭제 ###
# vector_store = client.beta.vector_stores.delete(
#     vector_store_id='vs_eKgl1FIZqLcqCYSBaa8UlZiJ'
# )


###############################################################


# # 기존 어시스턴트 ID 확인
# assistant_list = client.beta.assistants.list()

# for assistant in assistant_list:
#     print(f"Assistant Name: {assistant.name}, Assistant ID: {assistant.id}")


###############################################################


# # 벡터스토어 리스트 검색 ###
# vector_store_list = client.beta.vector_stores.list()

# for vectorstore in vector_store_list:
#     print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")


# # 백터스토어 아이디 안 파일 리스트 ####
# vector_store_files = client.beta.vector_stores.retrieve(
#     vector_store_id='vs_eKgl1FIZqLcqCYSBaa8UlZiJ',
# )
# file_ids = vector_store_files.file_counts

# print('백터스토어에 저장된 파일 목록 : ')
# for file_id in file_ids:
#     print(file_id)