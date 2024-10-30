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
        1.	Code Matching Identification: Identify the corresponding Code in the Vienna Classification based on the image. Each Code consists of 6 digits:
            •	The first two digits represent the major classification.
            •	The next two digits represent the sub-classification.
            •	The last two digits represent the minor classification.
            •	Codes that are not 6 digits long are for reference only and should be excluded.
        2.	Classification Hierarchy:
            •	The major classification includes the sub-classification, and the sub-classification includes the minor classification. Progressively narrow down the Code by following this hierarchy.
            •	Start by identifying the major classification that most closely resembles the image, then find the closest sub-classification within that, and finally, the closest minor classification within the sub-classification.
        3.	Code Identification Process:
            •	Identify any objects or text within the image, and find the corresponding Code for them.
            •	If the text contains a specific item (e.g., if “일타르타르트” contains the term “tart”), locate the Code related to that item. For example, if “tart” is included, find the related Code, such as 080116.
            •	If the object is integrated with other images or text, locate the Code that includes the object.
            •	If the content in the English column matches the image exactly, return only that corresponding 6-digit Code.
            •	If there is no exact match for the Code, find the Code that belongs to the closest matching English entry.
            •	A single image may correspond to multiple Codes.
        4. Image Analysis:
            “Analyze the image and, based on the following abstract characteristics, identify the most similar Code in the Vienna Classification:

            1.	General Shape: The overall shape resembles a polygon with five sides (pentagon-like).
            2.	Color Scheme: The shape is primarily a gradient blue color with white sections that resemble vertical bars or pillars.
            3.	Pattern: The white sections are divided vertically, forming a pattern similar to bars or stylized stripes.
            4.	Text: Below the shape is the Korean text ‘뒷배’, which may be related to a specific symbol or design.

            Using these characteristics, refer to the Vienna Classification system’s sections on abstract, geometric, or stylized figures to find the most similar Code. Return only the 6-digit Code that best represents these characteristics.”
        5. Stylized Text Check:
            •	If the image contains stylized text, refer to the Codes ranging from 270901 to 270926 to identify the corresponding alphabet.
            •	These Codes each represent a different alphabet letter, so find the matching Code within this range based on the stylized letter in the image.
        6.	Return Guidelines:
            •	Ensure the response is always provided in JSON format.
            •	Only return existing 6-digit Codes.
            •	If multiple Codes apply, follow the classification hierarchy to return the closest matching Code step-by-step.
            •	Do not create new Codes that are not present in the Vienna Code document.

        Additional Guidelines:
	        •	Ensure the response is provided in JSON format for consistent results.

        
        {{
            results: [
                {
                    "vienna_code": (6-digit code / could be multiple codes),
                    "description": (Description to the right of the Vienna Code - both in English and Korean from document (영어 & 한국어)),
                    "reason": (reason for the choice in Korean)
                }
            ] 
        }}

       
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