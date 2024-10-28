import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from init import client



# assistant_list = client.beta.assistants.list()

# for assistant in assistant_list:
#     print(f"Assistant Name: {assistant.name}, Assistant ID: {assistant.id}")


# assistant id를 별도의 변수에 담음
ASSISTANT_ID = 'asst_mD9MAguey0mzXs0wKEJmG4lV'

instructions = '''
# Role
업로드된 상표 이미지 또는 텍스트를 분석하여 상표의 '주요부'를 판단 후, 업로드되어있는 [상표심사기준202405.pdf]문서를 기반으로 해당 상표의 식별력과 등록 가능성을 판단합니다.
'''



vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_rLXYrSoCNE7aNpLI6cBGPseN'
)



### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ASSISTANT_ID,
    name= '상표 식별력 평가 AI',
    instructions = instructions,
    model ='gpt-4o',
    tools =  [{'type': 'file_search'}],
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    temperature=0,
)

assistant_info = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)
print(f"[현재 어시스턴트 정보]\n{assistant_info}")

# print(client.beta.vector_stores.list())
# print(client.beta.assistants.list())





# assistant update & functions schema 
### function과 schema


# def return_ai_company():
#     return '(주)에이아이노미스'

# function_schema={
#     'name' : 'return_ai_nomis',
#     'description' : "모든 응답 마지막에 반환한 문자열 문구를 추가합니다",
#     'parameters':{
#         'type': 'object',
#         'properties': {},
#         'additionalProperties':False
#     },
#     'strict': True # 모든 응답에서 호출되도록
# }