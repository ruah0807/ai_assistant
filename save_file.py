import requests
from PIL import Image
from io import BytesIO
import os
import json

def download_image(image_url, save_dir = 'img/downloaded_images', application_number = None):
    """
    주어진 URL 내에서 이미지를 다운로드하고 로컬에저장
    application_number가 있으면 해당 번호로 파일명을 저장하고, 없으면 기본 URL내에서 추출한 파일명 사용.
    """
    try:
        #이미지 URL 에서 이미지 데이터 다운로드 
        response = requests.get(image_url)
        response.raise_for_status()     # 응답 오류 있을 경우 예외 발생

        # 이미지 파일을 저장할 디렉토리 생성
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        #application_number가 있을 경우 파일명에 출원 번호 사용
        if application_number:
            image_filename = f'출원번호_{application_number}.png'
        else:
            image_filename = image_url.split("/")[-1]
            
        image_path = os.path.join(save_dir, image_filename)

        #이미지 데이터를 파일로 저장
        image = Image.open(BytesIO(response.content))
        image.save(image_path)

        print(f"이미지가 성공적으로 다운로드되었습니다: {image_path}")
        return image_path  # 이미지의 로컬 경로 반환

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {e}")
        return None



#JSON 파일로 저장(자동 줄바꿈)
def save_to_json(data, filename='trademark_info.json', folder_name= 'docs/output_folder'):
    # 폴더가 없으면 생성
    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)
        
    # 폴더 경로와 파일명을 결합하여 파일 저장 경로 설정
    file_path = os.path.join(folder_name, filename)
        
    with open(file_path, 'w', encoding ='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f'DATA saved to {file_path}')



# 이미지 파일 삭제
def delete_downloaded_images(downloaded_image_paths):
    try:
        if isinstance(downloaded_image_paths, str):
            os.remove(downloaded_image_paths)
            print(f"로컬에 저장된 이미지가 삭제되었습니다.: {downloaded_image_paths}")
        
        elif isinstance(downloaded_image_paths, list):
            for image in downloaded_image_paths:
                os.remove(image)
                print(f"로컬에 저장된 이미지가 삭제되었습니다. : {image}")
        else:
            print(f"잘못된 경로 형식 : {downloaded_image_paths}")

    except OSError as e:
        print(f"이미지 삭제 실패 : {image}. 에러 : {e}")


# 메시지들을 Markdown 파일로 저장하는 함수
def save_messages_to_md(responses, filename='assistant_response.md'):
    """
    responses : get_response 함수로부터 받은 메시지 리스트
    filename : 저장할 md 파일명
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for res in responses:
            # assistant의 응답만을 저장
            if res.role == 'assistant':
                for content in res.content:
                    if content.type == 'text':
                        f.write(f"{content.text.value}")
                f.write("\n\n---\n\n")
    print(f"Assistant의 응답이 {filename} 파일에 저장되었습니다.")






# def download_image_from_url(image_url, save_dir='img/downloaded_images'):
#     """
#     주어진 URL에서 이미지를 다운로드하고 로컬에 저장합니다.
#     """
#     try:
#         # 이미지 URL에서 이미지 데이터를 다운로드
#         response = requests.get(image_url)
#         response.raise_for_status()  # 응답 오류가 있을 경우 예외 발생

#         # 이미지 파일을 저장할 디렉토리 생성
#         if not os.path.exists(save_dir):
#             os.makedirs(save_dir)

#         # 이미지 이름을 URL에서 추출하거나 고유한 이름으로 지정
#         image_name = image_url.split("/")[-1]
#         image_path = os.path.join(save_dir, image_name)

#         # 이미지 데이터를 파일로 저장
#         image = Image.open(BytesIO(response.content))
#         image.save(image_path)

#         print(f"이미지가 성공적으로 다운로드되었습니다: {image_path}")
#         return image_path  # 이미지의 로컬 경로 반환

#     except requests.exceptions.RequestException as e:
#         print(f"이미지 다운로드 실패: {e}")
#         return None
    
    


# # 이미지 url로부터 다운로드하고 파일로 저장하는 함수
# def download_image_with_application_number(image_url, application_number,save_dir="similar_img"):

#     # 이미지 url 내에서 이미지 다운로드
#     response = requests.get(image_url)
    
#     if response.status_code == 200 :
        
#         img = Image.open(BytesIO(response.content))
        
#         # 디렉토리 경로 설정 (상대 경로를 절대 경로로 변환)
#         save_dir = os.path.join(os.getcwd(), save_dir)
        
#         # 디렉토리가 없으면 생성
#         if not os.path.exists(save_dir):
#             os.makedirs(save_dir)
#             print(f"디렉토리 생성됨: {save_dir}")
        
#         # 파일 경로 설정
#         image_filename = os.path.join(save_dir, f'출원번호_{application_number}.png')
        
#         # 이미지 저장
#         img.save(image_filename)
#         print(f'이미지가 {image_filename}으로 저장되었습니다.')
#         return image_filename
#     else:
#         print(f"Error : {response.status_code} - 이미지를 다운로드 할 수 없습니다.")
#         return None
    