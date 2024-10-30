import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ASSISTANT_ID = 'asst_5AAVBLsDY7vpCx7g4nVGe67R'


def submit_message_with_image(thread, user_message, image_path, image_url):
    content = [{'type': 'text', 'text': user_message}]

    print(f"Opening image file: {image_path}")  # 각 이미지 경로를 출력하여 확인
    try:
        with open(image_path, 'rb') as image_file:
            file = client.files.create(file=image_file, purpose='vision')  # 이미지 분석을 위한 용도
            # 이미지 파일과 함께 라벨을 텍스트로 추가
            content.append({'type': 'image_file', 'image_file': {'file_id': file.id}})
            content.append({'type': 'text', 'text': f'등록하려는 상표 URL: {image_url}'})  # 원본 이미지 URL 라벨링
    except FileNotFoundError as e:
        print(f"Error: 파일을 찾을 수 없습니다. 경로: {image_path}. 에러: {str(e)}")

    if content:
        # 이미지 파일 전송
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)
    else:
        print(f"Error : 이미지 파일 전송 실패 ")

    print(f"이미지 업로드 완료 . thread_id : {thread.id}")


def run_with_tools(ASSISTANT_ID, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        tools=  [{'type': 'file_search'}],
        instructions= """
       	1.	코드 매칭 식별: 이미지를 보고 Vienna 분류에서 해당 코드를 식별합니다. 각 코드는 6자리 숫자로 구성됩니다:
            •	첫 두 자리는 대분류를 나타냅니다.
            •	다음 두 자리는 중분류를 나타냅니다.
            •	마지막 두 자리는 소분류를 나타냅니다.
            •	6자리가 아닌 코드는 참조용이므로 제외해야 합니다.
        2.	분류 계층:
            •	대분류는 중분류를 포함하고, 중분류는 소분류를 포함합니다. 이 계층 구조를 따라 코드를 단계적으로 좁혀갑니다.
            •	먼저 이미지와 가장 유사한 대분류를 식별한 후, 해당 대분류 내에서 가장 가까운 중분류를 찾고, 마지막으로 해당 중분류 내에서 가장 가까운 소분류를 찾습니다.
        3.	코드 식별 과정:
            •	이미지 내 포함된 객체나 텍스트를 식별하여, 이와 관련된 코드를 찾습니다.
            •	텍스트에 특정 품목이 포함된 경우(예: “일타르타르트”에 “타르트”라는 단어가 있는 경우), 해당 품목과 관련된 코드를 찾습니다. 예를 들어 “타르트”가 포함된다면 080116과 같은 관련 코드를 찾습니다.
            •	객체가 다른 이미지나 텍스트와 통합되어 있다면 해당 객체를 포함하는 코드를 찾습니다.
            •	영어 열(English column)의 내용이 이미지와 정확히 일치하는 경우, 해당 6자리 코드만 반환합니다.
            •	정확히 일치하는 코드가 없을 경우, 가장 유사한 영어 항목과 연결된 코드를 반환합니다.
            •	이미지 하나에 여러 코드가 대응될 수 있습니다.
        4.	스타일화된 텍스트 확인:
            •	이미지에 스타일화된 알파벳이 포함된 경우, 270901부터 270926 내에서 해당 알파벳을 확인합니다.
            •	이 코드들은 각기 다른 알파벳을 나타내므로, 이미지의 스타일화된 알파벳에 따라 해당 범위에서 일치하는 알파벳의 코드를 찾습니다.
        5.	반환 지침:
            •	반드시 응답을 JSON 형식으로 제공합니다.
            •	존재하는 6자리 코드만 반환합니다.
            •	여러 코드가 적용될 경우, 계층 구조에 따라 가장 일치하는 코드부터 단계별로 반환합니다.
            •	Vienna 코드 문서에 없는 새로운 코드를 생성하지 않습니다.

        추가 지침:

            •	응답을 JSON 형식으로 제공하여, 결과가 일관되게 반환되도록 하세요.
        
        {{
            results: [
                {
                    "vienna_code": (6-digit code / could be multiple codes),
                    "description": (Description to the right of the Vienna Code - both in English and Korean from document (영어 & 한국어)),
                    "reason": (reason for the choice in Korean)
                }
            ] 
        }}

        이미지 분석 :

        “이미지를 분석하고, 추상적인 형태의 다음 특징들에 기반하여 Vienna 분류 코드에서 가장 유사한 코드를 식별하세요:
            •	모양: 이미지의 전반적인 형태와 구조를 파악합니다. 예를 들어, 다각형, 원형, 정사각형 등과 같은 기본 도형인지, 혹은 더 복잡한 기하학적 모양인지 확인합니다.
            •	색상 구성: 이미지의 주요 색상과 그라데이션, 혹은 색상 배치 패턴을 관찰합니다. 특정 색상이 도형의 일부를 강조하거나, 색상이 어떻게 배열되어 있는지 설명할 수 있습니다.
            •	패턴: 도형 내부 또는 주변의 패턴을 확인합니다. 예를 들어, 세로 또는 가로의 줄무늬, 기하학적 패턴, 점선, 혹은 반복적인 텍스처 등이 있을 수 있습니다.
            •	텍스트: 이미지에 포함된 텍스트가 있는 경우, 텍스트의 언어, 스타일, 의미를 분석합니다. 텍스트가 이미지와 어떻게 통합되어 있는지, 특정 품목이나 상징을 나타내는지 확인합니다.
        이러한 특징들을 사용하여 Vienna 분류 시스템에서 추상적이거나 기하학적, 또는 스타일화된 도형에 대한 섹션을 참고해 가장 유사한 코드를 검색하세요. 이러한 특징을 가장 잘 나타내는 6자리 코드를 반환하세요.”
        
        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input, image_path, image_url):
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input, image_path, image_url)
    run = run_with_tools(ASSISTANT_ID, thread)
    return thread, run

# """
#         [ Context ]
#         사용자가 올린 이미지가 어떤형태인지 도형의 모양이나 물체의 갯수, 모양을 추측하고  
#         vienna.md 문서를 참고하여 해당되는 '도형설명'을 찾아 가져옵니다.

#         [ instructions ]
#         1. 사용자가 업로드한 이미지의 도형및 형태를 분석합니다.
#         2. [vienna.md] 파일에서 분석한 이미지에 대응하는 '도형설명'을 찾습니다.
#             1. # 부분에서 대분류를 찾습니다.
#             2. ## 부분에서 중분류를 찾습니다.
#             3. ### 소분류 부분에서 해당 설명을 찾으세요
#         3. 찾은 도형을 여러개 나열하세요.

#         [ Document example ]
#         문서는 다음과 같은 형식으로 되어있습니다.:
#             ```
#             # 27	문자, 숫자의 서체
#             ## 09	알파벳 문자 도형
#             ### 도형 설명
#             - 	03	도형화(디자인화)된 "C"
#             C Stylized
#             ```
#         ### results
#         shape: 도형화(디자인화)된 'C'(### 해당 설명부분을 변경하지 않고 그대로 씁니다.)
#         reason : (이유를 설명)

#         [Warning]
#         - 최대 10개 이하의 리스트로 나열합니다.
#         - 반드시 문서에서 vienn code에 대한 설명을 찾아야합니다.
#         - 도형 뿐아니라 형태, 디자인화된 글자까지 분석합니다. 
#             예 : 사람(여자 혹은 남자 혹은 어린이), 이젤, 도구, 도형화(디자인화)된 'A' 등.
#         - 설명은 절대 변형해서 쓰지 않습니다.
#         - 반드시 한국어로 작성합니다.
        
#         응답 형식 : 
#         ```json
#         {{
#             results: [
#                 {
#                  "shape" :(찾은 '도형'혹은 '형태' 혹은 '글자'의 설명)
#                  "reason" : (이유)
#                    }
#             ] 
#         }} 
#         ```       
#         """



"""
Please tell me which category in the vienna_code_eu.pdf file this image corresponds. 
        The answer should be follow the 'Response Format' below in json style.
        
        Categories are composed of three numbers with two periods in between, like 2.1.15. 
        It's possible for one image to belong to multiple categories. 
        If there's no exact match, find the closest category. 
        Don't create new categories that aren't in the vienna_code_eu.pdf file. 
        Don't use categories that have a red strikethrough. 

        Prompt Example for Image Analysis Including Abstract Shapes and Specific Objects/People:
        “Analyze the abstract shapes and specific objects or people in the image according to the following criteria:

            •	Geometric features (e.g., circular, triangular, rectangular shapes)
            •	Pattern repetition: Whether there is any recurring pattern in the shapes
            •	Symmetry or irregularity: Whether the shapes are symmetrical or have irregular characteristics
            •	Color variations and gradients: Analyze changes in color, including shading and gradient effects
            •	Presence of specific objects or people: Identify whether the image contains identifiable objects or people such as a woman, man, child, palette, brush, or any other recognizable items (e.g., a woman dancing, someone painting, etc.)
            •	Action or motion: If people are depicted, determine whether they are engaged in any action (e.g., dancing, painting, playing an instrument) and describe the activity.

        For each shape, object, or person, apply these criteria and provide as detailed a classification and description as possible.”



        

        
        Response Format :
        {{
            results: [
                {
                    "vienna_code": (3 to 6-digit code(with period) / could be multiple codes),
                    "description": (Description to the right of the Vienna Code - both in English and translated into Korean (영어원문과 번역된 한국어)),
                    "reason": (reason for the choice in Korean)
                }
            ] 
        }}

"""