import requests
from PIL import Image
from io import BytesIO
import os
import json

def download_image_from_url(image_url, save_dir='downloaded_images'):
    """
    주어진 URL에서 이미지를 다운로드하고 로컬에 저장합니다.
    """
    try:
        # 이미지 URL에서 이미지 데이터를 다운로드
        response = requests.get(image_url)
        response.raise_for_status()  # 응답 오류가 있을 경우 예외 발생

        # 이미지 파일을 저장할 디렉토리 생성
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 이미지 이름을 URL에서 추출하거나 고유한 이름으로 지정
        image_name = image_url.split("/")[-1]
        image_path = os.path.join(save_dir, image_name)

        # 이미지 데이터를 파일로 저장
        image = Image.open(BytesIO(response.content))
        image.save(image_path)

        print(f"이미지가 성공적으로 다운로드되었습니다: {image_path}")
        return image_path  # 이미지의 로컬 경로 반환

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {e}")
        return None
    
    


# 이미지 url로부터 다운로드하고 파일로 저장하는 함수
def download_image_with_application_number(image_url, application_number,save_dir="similar_img"):

    # 이미지 url 내에서 이미지 다운로드
    response = requests.get(image_url)
    
    if response.status_code == 200 :
        
        img = Image.open(BytesIO(response.content))
        
        # 디렉토리 경로 설정 (상대 경로를 절대 경로로 변환)
        save_dir = os.path.join(os.getcwd(), save_dir)
        
        # 디렉토리가 없으면 생성
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"디렉토리 생성됨: {save_dir}")
        
        # 파일 경로 설정
        image_filename = os.path.join(save_dir, f'출원번호_{application_number}.png')
        
        # 이미지 저장
        img.save(image_filename)
        print(f'이미지가 {image_filename}으로 저장되었습니다.')
        return image_filename
    else:
        print(f"Error : {response.status_code} - 이미지를 다운로드 할 수 없습니다.")
        return None
    


#JSON 파일로 저장(자동 줄바꿈)
def save_to_json(data, filename='trademark_info.json', folder_name= 'output_folder'):
    # 폴더가 없으면 생성
    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)
        
    # 폴더 경로와 파일명을 결합하여 파일 저장 경로 설정
    file_path = os.path.join(folder_name, filename)
        
    with open(file_path, 'w', encoding ='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f'DATA saved to {file_path}')

