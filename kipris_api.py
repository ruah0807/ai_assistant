import requests, os, xmltodict, json
from init import kipris_api
import base64
from io import BytesIO
from PIL import Image


#JSON 파일로 저장(자동 줄바꿈)
def save_to_json(data, filename='trademark_info.json'):

    with open(filename, 'w', encoding ='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f'DATA saved to {filename}')



# KIPRIS API 호출
def get_trademark_info(trademark_name, similarity_code):

    BASE_URL = 'http://plus.kipris.or.kr/kipo-api/kipi/trademarkInfoSearchService/getAdvancedSearch'

    params = {
        'application': 'true',          # 현재 출원된 상표
        'registration': 'true',         # 현재 등록된 상표
        'refused': 'false',             # 등록 거절된 상표
        'expiration': 'false',          # 기간 만료된 상표
        'withdrawal': 'false',          # 취하된 상표
        'publication': 'true',          # 공고된 상표
        'cancel': 'false',              # 무효인 상표
        'abandonment': 'false',         # 포기한 상표
        'character': 'true',            # 문자 상표 중에서 검색
        'figure': 'true',               # 도형 상표 중에서 검색
        'compositionCharacter': 'true', # 복합 문자 상표 중에서 검색
        'figureComposition': 'true',    # 도형 복합 상표 중에서 검색
        'fragrance': 'false',           # 냄새 상표 중에서 검색
        'sound': 'false',               # 소리 상표 중에서 검색
        'color': 'true',                # 색채 상표 중에서 검색
        'colorMixed': 'true',           # 색채 복합 상표 중에서 검색
        'dimension': 'false',           # 입체상표 중에서 검색
        'hologram': 'false',            # 홀로그램 상표 중에서 검색
        'invisible': 'false',           # 시각적으로 인식 불가능한 상표 중에서 검색
        'motion': 'false',              # 동작 상표 중에서 검색
        'visual': 'false',              # 시각적으로 인식 가능한 상표 중에서 검색
        'ServiceKey': kipris_api,       # KIPRIS API 키
        'trademarkName': trademark_name,# 검색할 상표 이름
        'trademark' : 'true',           # 이게 true여야 제대로 검색됩니다.
        'similarityCode': similarity_code,
        'pageNo' : 1,
        'numOfRows' : 20,
        
    }

    # api 요청 보내기
    response = requests.get(BASE_URL, params=params)

    #응답이 성공적인지 확인
    if response.status_code == 200 :
        # XML 데이터를 JSON으로 변환
        data = xmltodict.parse(response.content)

        # bigDrawing URL을 base64 로 변환
        try:
            items = data['response']['body']['items']['item']

            if isinstance (items, dict):
                items = [items]

            print(f'{trademark_name}의 데이터 개수 : {len(items)}개')
            
            return items[:20] # item 리스트 반환

        except Exception as e:
            print(f"검색결과 없음: {e}")
            return None
    else:
        print(f"Error: {response.status_code}")




# 여러 상표명칭을 검색하여 모든 결과를 하나의 리스트에 모은 후 json 으로 저장
def search_and_save_all_results(trademark_names, similarity_code):

    all_results = []
    for trademark_name in trademark_names:
        print(f'Searching for : {trademark_name}')
        result = get_trademark_info(trademark_name, similarity_code)

        if result : 
            all_results.extend(result)

    save_to_json(all_results, f'combined_trademark_info.json')
    return all_results


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



def updated_search_results_for_image(seperated_words, similarity_code):

    # 1. 모든 검색 결과를 하나의 리스트에 저장하고 반환
    all_results = search_and_save_all_results(seperated_words, similarity_code)

    # # 각 항목의 drawing을 base64로 변환
    # for item in all_results:
    #     process_drawing(item)

    # save_to_json(all_results, f'update_combined_trademark_info.json')
    
    filtered_results =[]

    for item in all_results:
        big_drawing_url = item.get('bigDrawing')
        application_number = item.get('applicationNumber')
        vienna_code = item.get('viennaCode') 

        image_path = None

        if vienna_code:
            if big_drawing_url and application_number:
                #이미지 다운로드 처리
                image_path = download_image_with_application_number(big_drawing_url, application_number)

            if image_path :
                filtered_item = {
                    'image_path': image_path,
                    'classification_code' : item.get('classificationCode'),
                    'image_url' : item.get('bigDrawing'),
                    'application_number' : item.get('applicationNumber'),
                    'vienna_code': item.get('viennaCode')
                    # '상표명' : item.get('title'),
                    # '상태' : item.get('applicationStatus'),
                    # '출원/등록일' : item.get('applicationDate'),
                    # '출원인/등록권자' : item.get('applicantName'),
                }
                filtered_results.append(filtered_item)

    save_to_json(filtered_results, f'filtered_item.json')
    return filtered_results[:10]




def updated_search_results_for_text(seperated_words, similarity_code):

    # 1. 모든 검색 결과를 하나의 리스트에 저장하고 반환
    all_results = search_and_save_all_results(seperated_words, similarity_code)

    filtered_results =[]
    for item in all_results:
        filtered_item = {
            '상표명' : item.get('title'),
            '상품류' : item.get('classificationCode'),
            '상태' : item.get('applicationStatus'),
            '상표이미지' : item.get('bigDrawing'),
            '출원/등록번호' : item.get('applicationNumber'),
            '출원/등록일' : item.get('applicationDate'),
            '출원인/등록권자' : item.get('applicantName'),
        }
        filtered_results.append([filtered_item])

    return filtered_results[:10]



# 테스트 데이터
# seperated_words = [
#     "mindshare",
#     "마인드쉐어",
#     "mind",
#     "share",
#     "마인드",
#     "쉐어",
#     "인지공유",
#     "마음나눔"
# ]


# all_result = updated_search_results(seperated_words)
# print(all_result)


######### big Drawing 필드를 처리하고 base64로 변환 ############
# def process_drawing(item):

#     drawing_url = item.get('drawing')

#     if drawing_url:
#         response = requests.get(drawing_url)
    
#         # Ensure the request was successful
#         if response.status_code == 200:
#             # Encode the image content to base64
#             encoded_image = base64.b64encode(response.content)
        
#             # Convert to a readable base64 string
#             base64_string = encoded_image.decode('utf-8')
#             item['drawingBase64'] = base64_string

#             return item['drawingBase64']
#         else:
#             print(f"Drawing URL not found in item: {item}")
#             return None
#     else:
#         print(f"Invalid item format: {item}")
#         return None

