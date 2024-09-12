import requests
import xmltodict
from init import kipris_api
import json
import requests
import base64


# big Drawing 필드를 처리하고 base64로 변환
def process_drawing(item):

    drawing_url = item.get('drawing')

    if drawing_url:
        response = requests.get(drawing_url)
    
        # Ensure the request was successful
        if response.status_code == 200:
            # Encode the image content to base64
            encoded_image = base64.b64encode(response.content)
        
            # Convert to a readable base64 string
            base64_string = encoded_image.decode('utf-8')
            item['drawingBase64'] = base64_string

            return item['drawingBase64']
        else:
            print(f"Drawing URL not found in item: {item}")
            return None
    else:
        print(f"Invalid item format: {item}")
        return None



#JSON 파일로 저장(자동 줄바꿈)
def save_to_json(data, filename='trademark_info.json'):

    with open(filename, 'w', encoding ='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print(f'DATA saved to {filename}')



# KIPRIS API 호출
def get_trademark_info(trademark_name):

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
        # 'classification' : classification, # 상품 분류 넘버
        'trademark' : 'true',           # 이게 true여야 제대로 검색됩니다.
        'pageNo' : 1,
        'numOfRows' : 5
        
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

            count_items = len(items)
            print(f'{trademark_name}의 데이터 개수 : {count_items}개')

            # 결과가 없으면 None을 반환하고 다음으로 넘어감
            if not items:
                print(f"'{trademark_name}'에 대한 검색 결과가 없습니다.")
                return None
            
            return items # item 리스트 반환

        except Exception as e:
            print(f"Error processing bigDrawing: {e}")
            return None
    else:
        print(f"Error: {response.status_code}")




# 여러 상표명칭을 검색하여 모든 결과를 하나의 리스트에 모은 후 json 으로 저장
def search_and_save_all_results(trademark_names):

    all_results = []
    for trademark_name in trademark_names:
        print(f'Searching for : {trademark_name}')
        result = get_trademark_info(trademark_name)

        if result : 
            all_results.extend(result)

    save_to_json(all_results, f'combined_trademark_info.json')
    return all_results




def updated_search_results(seperated_words):

    # 1. 모든 검색 결과를 하나의 리스트에 저장하고 반환
    all_results = search_and_save_all_results(seperated_words)

    # 각 항목의 drawing을 base64로 변환
    for item in all_results:
        process_drawing(item)

    save_to_json(all_results, f'update_combined_trademark_info.json')

    return all_results
    



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