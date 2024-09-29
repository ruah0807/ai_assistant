import requests, os, xmltodict, json, concurrent.futures, asyncio
from init import kipris_api

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
        'pageNo' : 1
    }
    if trademark_name:
        params['trademarkName'] = trademark_name
    if similarity_code:
        params['similarityCode'] = similarity_code
    if vienna_code:
        params['viennaCode'] = vienna_code
    if num_of_rows:
        params['numOfRows'] = num_of_rows
        
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
        except Exception as e:
            print(f"API 응답에서 [{trademark_name}] 검색 결과를 찾을 수 없습니다: {e}")
            return []
        
        # viennaCode를 빈값으로 요청시 null 값만 반환 
        if not vienna_code : 
            filtered_items = [item for item in items if not item.get('viennaCode')]
            print(f"ViennaCode가 null인 항목 수: {len(filtered_items)}")
            return filtered_items
        else:
            return items
            
    else:
        print(f"Error: {response.status_code} - {response.reason}")
        return None



########################################################################



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
