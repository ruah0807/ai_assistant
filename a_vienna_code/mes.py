import os, sys, asyncio, concurrent.futures
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

ass_id = 'asst_5AAVBLsDY7vpCx7g4nVGe67R'


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


def run_with_tools(ass_id, thread):

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ass_id,
        tools=  [{'type': 'file_search'}],
        instructions= """
        [ Context ]
        Please let me know which category in the vienna_code_eu.pdf file this image corresponds to. 
        Categories are composed of three numbers with two periods in between (e.g., 2.1.15). 
        If the image belongs to multiple categories, return all of them. 
        If there is no exact match, either return no result or find the closest category. 
        Don’t create new categories that aren’t in the file, and don’t use categories that have a red strikethrough.
        Return up to 10 similar categories if they seem relevant.
        
        After finding the category, convert it into a code using the following rules:

        •	If the number before the period is single-digit, add a 0; if it’s double-digit, leave it as is.
	    •	Remove the periods, and if the number after the period is single-digit, add a 0; if it’s double-digit, leave it as is.
	    •	Apply the same rule to the last number after the second period.

        For example:
        •	1.2.1 becomes 010201,
        •	24.15.1 becomes 241501,
        •	14.7.7 becomes 140707.
            
        If the category has multiple parts, return the converted code for each.

        Response Format : 
        ```json
        {{
            results: [
                {
                "vienna_code" : (shoud be 6 number of digit / could be several codes.)
                "description" :(Description to the right of the Vienna Code - English and translate Korean(영어원문과 번역된 한국어))
                "reason" : (reason for choicing in Korean)
                   }
            ] 
        }} 
        ```

        Warning:
        - Response should show up from the document.  
        - You should only give it json format.     
        """
    )
    return run


# 새로운 스레드 생성 및 메시지 제출
def create_thread_and_run(user_input, image_path, image_url):
    thread = client.beta.threads.create()
    submit_message_with_image(thread, user_input, image_path, image_url)
    run = run_with_tools(ass_id, thread)
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