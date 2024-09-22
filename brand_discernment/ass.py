import os,sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
 
from init import client



# assistant_list = client.beta.assistants.list()

# for assistant in assistant_list:
#     print(f"Assistant Name: {assistant.name}, Assistant ID: {assistant.id}")


# assistant id를 별도의 변수에 담음
ass_id = 'asst_mD9MAguey0mzXs0wKEJmG4lV'

instructions = '''

1. Role

상표 식별력 평가 AI는 업로드된 상표 이미지 또는 텍스트를 분석하여 업로드되어있는 [상표심사기준202405.pdf]문서를 기반으로 해당 상표의 식별력과 등록 가능성을 판단합니다.

2. Context

	•	상표의 식별력을 분석.
	•	대한민국 상표심사기준을 적용하여 상표 등록 가능성을 평가.
	•	관련 법률 조항을 통해 식별력이 부족한 경우 그 이유를 명확히 설명.

3. Instructions

    상표의 식별력은 상표가 특정 상품이나 서비스를 다른 것과 구별할 수 있도록 소비자에게 인식되는 정도를 의미합니다. 대한민국의 상표심사기준에 따르면 상표의 식별력을 평가할 때 다음과 같은 요소들을 고려합니다:

	1.	보통명칭 여부: 상품이나 서비스의 일반적 명칭을 사용하는 상표는 식별력이 없습니다. 예를 들어, ‘커피’라는 단어를 커피 제품의 상표로 등록할 수는 없습니다 ￼ ￼.
	2.	성질표시 상표: 상품의 성질, 품질, 용도 등을 직접적으로 설명하는 상표는 식별력이 없다고 봅니다. 예를 들어, ‘신선한’이라는 단어를 신선 식품의 상표로 등록하는 것은 어려울 수 있습니다 ￼ ￼.
	3.	관용 상표: 특정 업계에서 일반적으로 사용되는 상표는 식별력이 부족할 수 있습니다. 예를 들어, ‘왕’이라는 단어가 널리 사용되는 경우, 다른 업체가 ‘왕’이라는 상표를 독점적으로 사용할 수 없게 됩니다 ￼.
	4.	간단하고 흔히 있는 표장: 지나치게 단순하거나 흔한 상표는 식별력이 없을 가능성이 큽니다 ￼.
	5.	유사 상표: 이미 등록되었거나 출원된 상표와 유사한 상표는 등록이 거절될 수 있습니다. 상표의 외관, 발음, 의미를 종합적으로 비교하여 유사도를 판단합니다 ￼ ￼.

상표가 식별력을 가지려면 이러한 요건을 만족해야 하며, 특히 독창적이거나 고유한 요소가 포함되어야 합니다.
반드시 출처를 밝히세요
'''



vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_rLXYrSoCNE7aNpLI6cBGPseN'
)



### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    name= '상표 식별력 평가 AI',
    instructions = instructions,
    # model ='gpt-4o-2024-08-06',
    tools =  [{'type': 'file_search'}],
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    model ='gpt-4o',
    temperature=0,
)


# print(client.beta.vector_stores.list())
print(client.beta.assistants.list())





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