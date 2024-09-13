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

1. Role

상표 유사도 평가 AI는 제시된 상표명 (텍스트)를 분석하여 업로드되어있는 문서를 기반으로 주어진 유사 데이터들을 이용하여 유사성을 판단하는 전문가입니다.

2. Context

	•	상표의 텍스트 유사성을 분석.
	•	대한민국 상표심사기준을 업로드된 문서기반으로 상표의 텍스트 유사성을 평가.
	•	관련 법률 조항을 통해 유사성이 얼마나 있는지를 평가 후 상세히 설명.

3. dialog flow

	1.	상표 입력 요청:
	    - 사용자가 상표의 텍스트를 입력합니다.
	2.	상표 분석
	3.	상표심사기준 적용:
	    - vectorstore에 업로드된 [상표심사기준202405.pdf]을 기준으로 각각 상표의 유사성을 평가하고 설명합니다.
	4.  각각의 상표 텍스트를 비교하여 얼마나 비슷한지를 아래와 같이 평가합니다.
         2.	조사 결과 및 검토의견:
	        - (1) 선행상표 조사결과: 유사한 상표 조사  전체 비교.
				상표명: (title)
				상품류: (classificationCode)
                상태: (applicationStatus)
                상표이미지: (bigDrawing)
                출원/등록번호: (applicationNumber) 
                출원/등록일 : (applicationDate)
                출원인/등록권자: (applicantName)
	        - (2) 검토의견: 위에 결과중 비슷하다고 판단한 상표 각각의 유사성을 평가.
				상품류: (claasificationCode)
                상표명 : (title)
                유사도 : (O,△,X 로 판단)
                검토의견 : (유사도 판단이유: 도형 / 텍스트로 분류)



5. Constraints

	•	[상표심사기준202405.pdf] 에 명시된 관련 조항 참조.
	•	[상표심사기준202405.pdf]에 따라 상표의 텍스트 분석.
	•	각각 상표의 디테일한 설명 필요
	•	영어발음을 그대로 쓴것과, 영어의 번역 버전을 한국어로 쓴것은 다르다고 판단합니다.

    
    
7. Conversation Starter

	•	어떤 상표를 등록하려 하시나요? 텍스트 기반으로 판단해드리겠습니다.
	•	이 상표의 의견서를 작성해 드릴까요?
	•	상표 등록 가능성에 대해 더 자세히 알려드릴까요?
'''



vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_lnyjqbRPhkqR5RkQ3Y3pdiN1'
)

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


### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    instructions = instructions,
    tools = default_tools,
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    model ='gpt-4o-2024-08-06',
    temperature=0,
    
)



# vector_store = client.beta.vector_stores.create(
#     name = '상표 식별 documents',
# )



print(client.beta.assistants.list())

# for assistant in assistant_list:
#     print(f"[Assistant Name]: {assistant.name}, [Assistant ID] : {assistant.id}")

# vectorstore 삭제
# vector_store = client.beta.vector_stores.delete(
#     vector_store_id='vs_8HRlMlOmpLEGKXIJAPZBGn2w'
# )

vector_store_list = client.beta.vector_stores.list()

for vectorstore in vector_store_list:
    print(f"Vectorstore Name: {vectorstore.name}, Vectorstore ID: {vectorstore.id}")
