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
        lease identify which Code in the vienna_code_kr.md file corresponds to this image. You should return them in JSON style.
        The Code consists of 6 digits: the first 2 represent the major classification, the next 2 represent the sub-classification, and the last 2 represent the minor classification. 
        Codes that are not 6 digits long are for reference only. 
        The major classification includes the sub-classification, and the sub-classification includes the minor classification, so please refer to that. 
        Find all major classifications, and start by looking for the one that is most similar to the image. 
        Then, within that major classification, find the sub-classification that is most similar to the image, and finally, within that sub-classification, find the minor classification that is most similar to the image. If there are multiple classifications, find them step by step. 

        Additionally, establish a relationship between the text and the objects in the image; if there is a Code that includes that object, return that Code. 
            - For example, if there is text that says 일타르타르트 along with an object similar to pie, this would correspond to tart, so you would search for tart and return the corresponding Code, such as 080116.

        If the object is integrated with other images or text, find the Code that includes that object. 
        If the content in the English column matches the image, return the corresponding 6-digit Code only. 
        A single image may correspond to multiple Codes. If there is no exact match for the Code, find the Code that belongs to the closest matching English entry. 
        Do not create new Codes that are not present in the vienna_code_kr.md file. 
        
        If the letters in the image are stylized, look for other codes as well, but make sure to refer to codes from 270901 to 270926. Return only 6-digit Codes.
            •	If the letters in the image are stylized, check the 270901 to 270926 range, where each code corresponds to a specific alphabet letter.
	        •	Since these codes each represent a different letter, look for the matching code within this range based on the stylized letter in the image.
        These instructions ensure the Code selection process is clear, precise, and that results are consistently returned in the required JSON format below.
        
        ### Response Format(JSON) :
        
        {{
            results: [
                {
                    "vienna_code": (6-digit code / could be multiple codes),
                    "description": (Description to the right of the Vienna Code - both in English and Korean (영어 & 한국어)),
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