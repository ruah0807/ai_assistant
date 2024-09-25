import requests, os, xmltodict, json, concurrent.futures, asyncio
from init import kipris_api
import base64
from save_file import download_image, save_to_json,download_image_with_application_number



# KIPRIS API 호출
def get_trademark_info(trademark_name, similarity_code, vienna_code, num_of_rows=5):

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
        'trademark' : 'true',           # 이게 true여야 제대로 검색됩니다.
        'pageNo' : 1,
        'numOfRows': num_of_rows,
        
    }
    if trademark_name:
        params['trademarkName'] = trademark_name
    if similarity_code:
        params['similarityCode'] = similarity_code
    if vienna_code:
        params['viennaCode'] = vienna_code
        
    # api 요청 보내기
    response = requests.get(BASE_URL, params=params)
    
    #응답이 성공적인지 확인
    if response.status_code == 200 :
 
        # XML 데이터를 JSON으로 변환
        data = xmltodict.parse(response.content)
        try:
            items = data['response']['body']['items']['item']
            if isinstance(items, dict):
                items = [items]  # 단일 항목을 리스트로 변환
            print(f"KIPRIS 검색명 [{trademark_name}] : {len(items)}개가 검색되었습니다.")
            return items
        except Exception as e:
            print(f"API 응답에서 [{trademark_name}] 검색 결과를 찾을 수 없습니다: {e}")
            return []
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None


# 병렬 처리를 위한 함수
def search_trademark(trademark_name, similarity_code, vienna_code, num_of_rows):
    return get_trademark_info(trademark_name, similarity_code, vienna_code, num_of_rows)



# 여러 상표명칭을 검색하여 모든 결과를 하나의 리스트에 모은 후 json 으로 저장
async def search_and_save_all_results(trademark_names, similarity_code, vienna_code, num_of_rows = 5):
    print(f"검색어: {trademark_names}, 유사성 코드: {similarity_code}, 비엔나 코드: {vienna_code}")
    print(f"KIPRIS API KEY : {kipris_api}")
    
    if not trademark_names:
        all_results = get_trademark_info(None, similarity_code, vienna_code, num_of_rows)
    else:
        all_results = []

        # ThreadPoolExecutor를 사용하여 병렬 처리
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #각 상표명에 대해 비동기로 검색 요청을 보냄
            futures = [executor.submit(search_trademark, name, similarity_code, vienna_code, num_of_rows) for name in trademark_names]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    all_results.extend(result)
    
    filtered_results = []
    for item in all_results:
        filtered_item = {
            'title': item.get('title'),
            'classification_code' : item.get('classificationCode'),
            'similar_image_url' : item.get('bigDrawing'),
            'application_number' : item.get('applicationNumber'),
            'vienna_code': item.get('viennaCode')
        }
        filtered_results.append(filtered_item)
    print(f"필터된 리스트 수: {len(filtered_results)}")
    save_to_json(filtered_results, f'item_labeling.json')

    return filtered_results




async def updated_search_results_for_image(seperated_words, similarity_code=None, vienna_code=None):
    # 1. 모든 검색 결과를 하나의 리스트에 저장하고 반환
    filtered_results = await search_and_save_all_results(seperated_words, similarity_code, vienna_code)
    
    tasks = []

    for item in filtered_results:
        similar_image_url = item.get('similar_image_url')
        application_number = item.get('application_number')  # 'applicationNumber' 대신 'application_number' 사용 확인

        if similar_image_url and application_number:
            # 이미지 다운로드 처리
            task = download_image_with_application_number(similar_image_url, application_number)
            tasks.append((task, item))
        else:
            print(f"Skipping item due to missing data - similar_image_url: {similar_image_url}, application_number: {application_number}")

    results = await asyncio.gather(*[task for task, _ in tasks])

    # 다운로드된 이미지 경로를 필터링하여 결과 생성
    for (result, (_, item)) in zip(results, tasks):
        if result:
            item['image_path'] = result  # 이미지 경로 추가
    save_to_json(filtered_results, f'item_labeling.json')

    return filtered_results



async def updated_search_results_for_text(seperated_words, similarity_code=None):

    # 1. 모든 검색 결과를 하나의 리스트에 저장하고 반환
    all_results = await search_and_save_all_results(seperated_words, similarity_code, None)

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

    return filtered_results



# # 테스트 데이터
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


# all_result = updated_search_results_for_text(seperated_words)
# print(all_result)



# # big Drawing 필드를 처리하고 base64로 변환
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
