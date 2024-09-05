# pip install openai load_dotenv 


# openai 패키지의 버전 정보 확인
# pip show openai | grep Version

import os 
from dotenv import load_dotenv
import openai

load_dotenv()


# # Helper 함수
# show_json() 함수 : 인자로 받은 객체의 모델을 json 형태로 변환하여 출력
# Assistant가 응답한 결과를 분석할 때 print 목적으로 활용

# %%
import json 

def show_json(obj):
    #obj의 모델을 Json 형태로 변환 후 출력
    display(json.loads(obj.model_dump_json()))

# %%
api_key = os.environ.get('OPENAI_API_KEY')
# print(api_key)


# %%
from openai import OpenAI

# Open ai API를 사용하기 위한 클라이언트 객체생성
client = OpenAI(api_key=api_key)

# file = client.files.create(
#     file = open('/Users/ainomis_dev/Desktop/상표 식별자/상표심사기준202405.pdf','rb'),
#     purpose='assistants'
    
# )

# %%

assistant = client.beta.assistants.create(
    name = "상표 식별력 판단 AI(GPT-4o)",
    instructions="""
    1. Role
    상표 식별력 판단 AI 서비스는 업로드한 파일들을 Retrieval 하고, 상표의 이미지 또는 텍스트를 분석하여, 해당 상표의 식별력을 평가하고 등록 가능성을 판단하는 역할을 수행합니다.

    2. Context

    이 GPT는 대한민국의 상표를 새로 등록하려는 업체를 대상으로, 상표가 이미지든 텍스트든 상관없이 대한민국 상표심사기준 문서에 따라 식별력을 평가합니다. 또한, 식별력이 부족한 경우 그 이유를 상세히 설명하고, 관련 법률 조항과 판례를 참조하여 사용자가 이해할 수 있도록 도와줍니다.

    3. Dialog Flow

        1.	상표 입력 요청: 사용자가 상표 이미지를 업로드하거나 텍스트 형태의 상표를 입력하도록 요청합니다. 
        2.	상표 형태 인식: 입력된 상표가 이미지인지 텍스트인지 인식합니다.
        •	이미지일 경우: 이미지에서 텍스트나 시각적 요소를 추출한 후 분석합니다.
        •	텍스트일 경우: 텍스트를 직접 분석합니다.
        3.	법률 기준 참조: [상표심사기준202405.pdf]안에 있는 내용을 기준으로 상표의 식별력을 평가합니다.
        •	식별력이 충분한경우 :  GPT는 상표심사기준 문서에서 관련 조항을 참조하여, 왜 식별력이 있는지를 신뢰성있는 데이터를 바탕으로 상세히 설명합니다. 
        •	식별력이 부족한 경우: GPT는 상표심사기준 문서에서 관련 조항을 참조하여, 왜 식별력이 부족한지 이유를 신뢰성있는 데이터를 바탕으로 상세히 설명합니다.
        4.	결과 제공: 상표가 식별력이 있는지, 등록 가능성이 있는지 평가한 후 결과를 사용자에게 제공합니다. 이때, 식별력이 부족한 경우 해당 법률 조항을 명시하고 이유를 설명합니다.
        5.	피드백 요청: 사용자에게 제공된 분석 결과에 대해 피드백을 요청하고, 추가 분석이 필요한지 확인합니다.

    4. Instructions

        1.	상표를 이미지나 텍스트 형태로 입력받으세요.
        2.	상표의 형태를 인식한 후, 해당 상표를 분석하세요.
        •	이미지에서 텍스트를 추출하거나 시각적 요소를 분석합니다.
        •	텍스트 형태의 상표는 직접 분석합니다.
        3.	대한민국 [상표심사기준202405.pdf]에 따라 상표의 식별력을 평가하세요.
        •	식별력이 부족한 경우, 상표심사기준 문서에서 관련 조항을 참조하여 상세한 이유를 제공하세요.
        •	사용자가 신뢰를 느끼도록 참고한 문서의 메타데이터를 보여주세요
        4.	상표의 식별력 여부와 등록 가능성을 명확히 설명하고, 결과를 사용자에게 전달하세요.
        5.	사용자의 피드백을 받아 필요 시 추가 분석이나 법적 조언을 제공하세요.

    5. Constraints

        •	GPT는 상표의 이미지 또는 텍스트를 분석할 때 대한민국 상표심사기준에 따라 판단해야 합니다.
        •	식별력이 부족한 경우, 상표심사기준 문서의 관련 조항을 참조하여 상세한 이유를 제공해야 합니다.
        •	법률적 용어를 사용하여 명확하게 결과를 전달해야 합니다.

    6. Output Indicator

        •	상표가 식별력이 있는지 여부를 명확히 판단하고, 해당 상표가 등록 가능성이 있는지를 법률적 기준에 따라 정확히 평가합니다.
        •	식별력이 부족한 경우, 상표심사기준 문서에서 참조한 조항과 함께 구체적이고 명확한 이유를 제시합니다.
        •	사용자의 피드백에 따라 추가 분석이나 정보 제공이 이루어집니다.
""",
model='gpt-4o',

)
# 생성된 챗봇의 정보를 json 형태로 출력 
show_json(assistant)


# 기존 어시스턴트 ID 확인
assistant_list = client.beta.assistants.list()

for assistant in assistant_list:
    print(f"Assistant Name: {assistant.name}, Assistant ID: {assistant.id}")


# assistant id를 별도의 변수에 담음
ASSISTANT_ID = 'asst_mD9MAguey0mzXs0wKEJmG4lV'
print(f"[새로 생성한 ASSISTANT_ID]\n{ASSISTANT_ID}")


# assistant 삭제
client.beta.assistants.delete(assistant_id=ASSISTANT_ID)
print(f"어시스턴트 {ASSISTANT_ID}가 삭제되었습니다.")



# 업데이트 및 Code_interpreter
#  assistant가 자체적으로 구동이 가능한 코드를 구현하고 query를 만들어 검색
# - 데이터가 많을 경우 토큰을 효율적으로 사용가능

# update assistant
assistant = client.beta.assistants.update(
    ASSISTANT_ID,
    tools=[{'type':'code_interpreter'}], 
)
show_json(assistant)

def upload_files(files):
    uploaded_files = []
    for filepath in files:
        file = client.beta.create(
            file = open(
                filepath,
                'rb'
            ),
            purpose='assistants'
        )
        uploaded_files.append(file.id)
        print(f'[업로드한 파일 ID]\n{file.id}')
    return uploaded_files



#업로드할 파일들의 경로를 지정
files_to_uploaded = [
    '상표식별/상표검색 프로세스.pdf',
    '상표식별/상표심사기준202405.pdf',
    '상표식별/상표유사여부보고서(별책).pdf',
]

file_streams = [open(path, 'rb') for path in files_to_uploaded]

# 파일 업로드
# file_ids = upload_files(files_to_uploaded)
# print(f'[업로드한 파일 리스트]\n{file_ids}')



## 업로드한 모든 파일 ID와 파일 명 출력
for file in client.files.list():
    print(f'[파일 ID] {file.id}, [파일명] {file.filename} ')

# pdf 파일 retriever 활용하기
file_ids = ['file-92LEUyQQl3JANFCeme88zg26','file-86Clgdid5xIjKGRP6woYiuCT','file-hpjBTNyZRMpQG4lxlqGLaa2c']


### 파일 백터화

vector_store = client.beta.vector_stores.create(
    name = '상표 식별 documents',
)

show_json(vector_store)

### 2. 파일을 업로드 하고 vector store에 추가

# 파일 업로드 및 백터 스토어에 추가
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files = file_streams
)

show_json(file_batch)
print(file_batch.status)
print(file_batch.file_counts)

#assistant 설정 업데이트
assistant = client.beta.assistants.update(
    ASSISTANT_ID,
    tools=[
        {'type': 'code_interpreter'},
        {'type': "file_search"}
    ]
)

### 3. 새 백터 스토어를 사용하도록 어시스턴트 업데이트

# 업로드된 파일 참조 및 검색 요청
assistant = client.beta.assistants.update(
    assistant_id=ASSISTANT_ID,
    tool_resources={'file_search': {'vector_store_ids': [vector_store.id]}},
    temperature=0
)
show_json(assistant)

### 4. 스레드 만들기
# 스레드에 메시지 첨부파일로 파일을 첨부 가능
# vector_store 스레드와 연관된 다른 파일이 생성되거나, 스레드에 이미 벡터 스토어가 첨부 되어있는 경우 새 파일을 기존 스레드 벡터 스토어에 첨부

# 	1.	파일 업로드: message_file 객체는 업로드된 이미지의 파일 ID를 가지고 있으며, 이 파일 ID를 스레드에서 사용하여 이미지 파일을 참조합니다.
# 	2.	스레드 생성: thread 객체는 대화의 흐름을 관리하는 스레드이며, 여기에 사용자가 보낸 메시지(텍스트와 이미지)가 포함됩니다.
# 	3.	어시스턴트 실행: client.beta.threads.runs.create()를 사용하여 스레드 내에서 어시스턴트를 실행시킵니다. 이때 어시스턴트의 ID가 필요하며, 해당 어시스턴트가 이미지를 분석할 수 있는지 확인해야 합니다.
# 	4.	결과 확인: client.beta.threads.messages.list()로 스레드의 대화 내용을 확인하여 어시스턴트가 이미지에 대해 어떤 응답을 했는지 확인할 수 있습니다.

thread = client.beta.threads.create()
show_json(thread)


message = client.beta.threads.messages.create(
    thread_id= thread.id,
    role='user',
    content='식별력이 뭐야?'
)
show_json(message)


run = client.beta.threads.runs.create(
    thread_id=thread.id, # 생성한스레드(카톡방)
    assistant_id=ASSISTANT_ID # 적용할 AssistantID
)
show_json(run)






# run을 생성하는 것은 비동기 작업이다.
# 이는 Run의 메타데이터와 함께 즉시 반환되며, status 는 queued(대기중)으로 표기된다.
# status 는 Assistant가 작업을 수행함에 따라(도구 사용 및 메시지 추가와 같은) 업데이트될 것임.

### status 목록
# - queued : 아직 실행이 되지 않고 대기중인 상태
# - in_progress: 처리중
# - requires_action : 사용자 입력 대기중
# - cancelling : 작업 취소중
# - cancelled : 취소 완료
# - failed: 오류(실패)
# - completed: 작업완료
# - expired: 작업 만료

import time 

def wait_on_run(run, thread):
    # 주어진 실행 (run)이 완료 될때까지 대기
    # status 가 'queued' 또는 'inprogress'인 경우에는 계속 polling 하며 대기
    while run.status == 'queued' or run.status == 'in_progress':
        # run.status를 업데이트 합니다.
        run = client.beta.threads.runs.retrieve(
            thread_id = thread.id,
            run_id= run.id
        )
        time.sleep(0.5)
    return run

# run 객체를 대기 상태로 설정하고, 해당 스레드에서 실행을 완료할 때가지 기다림
run = wait_on_run(run, thread)

# status가 'complete'인 경우에는 결과를 출력합니다.
show_json(run)




### Message(메세지)
# run이 완료되었다면, Assistant에 의해 처리된 결과를 보기 위해 Thread에서 messages를 확인할 수 있다.

# thread.id 를 사용하여 메시지 목록을 가져옴
messages = client.beta.threads.messages.list(thread_id=thread.id)

#결과 출력
show_json(messages)


# 이전에 받은 답변을 기억하고 있는지 확인
message = client.beta.threads.messages.create(
    thread_id= thread.id,
    role='user',
    content='상표심사기준 제 33조에는 어떤사항이 있어? 간단하게 말해줘'
)

run = client.beta.threads.runs.create(
    thread_id = thread.id,
    assistant_id= ASSISTANT_ID
)

# 답변 완료될때까지 대기
wait_on_run(run, thread)

# 마지막 사용자 메시지 이후 추가된 모든 메시지 검색
messages = client.beta.threads.messages.list(
    thread_id=thread.id, 
    order='asc', #오름차순으로 출력
    after=message.id  # 이전 메세지를 제외하고 출력
)
show_json(messages)



### 아미지 업로드와 함께 물어보기.###
file = client.files.create(
    file = open('/Users/ainomis_dev/Desktop/ainomis/ai_assistant/brand_img/starbings.png','rb'),
    purpose='vision'
)

message = client.beta.threads.messages.create(
    thread_id= thread.id,
    role='user',
    content=[
        {
            'type': 'text',
            'text': '이 상표의 식별력을 판단해줘'
        },
        {
            'type': 'image_file',
            'image_file': {'file_id': file.id}
        }
    ],
    
)

run = client.beta.threads.runs.create(
    thread_id = thread.id,
    assistant_id= ASSISTANT_ID
)

# 답변 완료될때까지 대기
wait_on_run(run, thread)

# 마지막 사용자 메시지 이후 추가된 모든 메시지 검색
messages = client.beta.threads.messages.list(
    thread_id=thread.id, 
    # order='asc', #오름차순으로 출력
    # after=message.id  # 이전 메세지를 제외하고 출력
)
show_json(messages)


