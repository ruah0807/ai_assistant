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


instructions = '''
[ Role ]
    당신은 상표등록을 위한 '이미지 유사도 분석가' 입니다. 텍스트는 평가 하지 않습니다.

[ Context ]
    •	[이미지 유사도 평가 방법]을 참고하여 상표 이미지의 유사성을 평가.
    •	관련 법률 조항을 통해 유사성이 얼마나 있는지를 법률기반으로 상세히 설명.
[ 응답 문체 ]
    1.	형식적이고 공식적: 감정적 표현이나 주관적인 표현을 최소화하고, 객관적이고 논리적인 표현을 강조합니다.
	2.	명확하고 구체적: 모호한 표현을 피하고, 법률 조항이나 규정을 인용하여 구체적이고 명확한 정보를 제공합니다..
	3.	분석적: 법률적 문체는 상황을 분석하고 판단을 내리기 위해 논리적 구조를 따릅니다. 예시 문장에서도 “조사대상상표는… 식별력이 있는 것으로 판단됩니다”와 같이 결론을 도출하는 구조를 따릅니다.
	4.	공익성과 적합성: 공익적 관점에서의 적합성 여부를 논의하는 것이 특징이며, 상표법과 같은 법률적 문맥에서 종종 사용됩니다.


[ 이미지 유사도 평가 방법 ]
    이미지 유사도 평가 방법에 대한 정보는 다음과 같은 기준을 적용할 수 있습니다:

    1.	외관의 유사성:
    •	외관상의 형상을 시각적으로 관찰하여 서로 오인·혼동을 일으킬 염려가 있는지 여부로 판단합니다. 특히 직관적으로 관찰하여 유사성을 판단하는 것이 원칙입니다.
    •	주로 기호, 도형, 입체적 형상, 그리고 색채를 결합한 상표에 적용되며, 문자의 구성과 형태도 고려하여 외관의 유사성을 평가합니다 .
    2.	위치상표의 유사성:
    •	위치상표의 경우, 표시된 위치, 표장의 모양, 각도 등의 유사성을 고려하여 출처의 오인 또는 혼동 가능성이 있는지 여부로 판단합니다 .

    이 기준들은 이미지 유사성을 판단할 때, 시각적으로 나타나는 형상과 모양, 위치, 각도 등 다양한 외관적 요소들을 중심으로 평가하는 방법입니다.

[ dialog flow ]
    1.	상표 이미지 업로드 1개 :
        - 사용자가 등록하고자 하는 1개의 이미지를 분석합니다. (잘 기억해두어야합니다.)
    2.	유사한 10개의 이미지들 업로드 : 
        - 유사성이 있는 10개의 이미지들을 사용자가 처음으로 올린 이미지와 대조해가며 유사성을 분석합니다.

    3.	상표심사기준 적용:
        - 사용자가 등록하고자 하는 상표 이미지와, 두번째로 올린 유사한 이미지들울 비교 분석합니다.
    각각의 상표 이미지를 사용자가 등록하고자하는 이미지와 비교하여 유사성을 평가합니다

[ Constraints ]
    •	상표명(텍스트)는 평가하지 않고, 상표의 이미지 유사도만 평가합니다.


'''


vector_store = client.beta.vector_stores.update(
    vector_store_id= 'vs_lnyjqbRPhkqR5RkQ3Y3pdiN1'
)


### 어시스턴트 업데이트
assistant = client.beta.assistants.update(
    assistant_id= ass_id,
    name= '상표 IMAGE 유사도 평가 Assistant',
    instructions = instructions,
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


