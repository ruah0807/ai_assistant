import concurrent.futures, asyncio
from file_handler import save_to_json,download_image_with_application_number
from kipris_api import get_trademark_info

# 여러 상표명칭을 검색하여 모든 결과를 하나의 리스트에 모은 후 json 으로 저장
async def search_and_save_all_results(trademark_names, similarity_code, vienna_code, num_of_rows = 5, only_null_vienna_search=False):
    
    if not trademark_names:
        all_results = get_trademark_info(None, similarity_code, vienna_code, num_of_rows)
    else:
        all_results = []

        # ThreadPoolExecutor를 사용하여 병렬 처리
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #각 상표명에 대해 비동기로 검색 요청을 보냄
            futures = [executor.submit(get_trademark_info, name, similarity_code, vienna_code, num_of_rows) for name in trademark_names]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    all_results.extend(result)
    
    filtered_results = []
    application_numbers_seen = set()    # 중복 체크를 위한 집합.
    null_vienna_count = 0   # null인 viennaCode 항목의 수를 카운트하는 변수

    for item in all_results:
        # only_null_vienna_search 이 True일 경우 vienna_code가 null인 항목만 필터링
        if only_null_vienna_search and item.get('viennaCode')is not None:
            null_vienna_count += 1
            continue

        # 중복된 application_number를 제거.
        application_number = item.get('applicationNumber')
        if application_number in application_numbers_seen:
            continue

        filtered_item = {
            'title': item.get('title'),
            'classification_code' : item.get('classificationCode'),
            'similar_image_url' : item.get('bigDrawing'),
            'application_number' : item.get('applicationNumber'),
            'vienna_code': item.get('viennaCode')
        }
        filtered_results.append(filtered_item)
        application_numbers_seen.add(application_number)

    print(f"ViennaCode가 null인 항목 수: {null_vienna_count}")
    print(f"필터된 리스트 수: {len(filtered_results)}")
    save_to_json(filtered_results, f'item_labeling.json')

    return filtered_results


async def download_and_add_image_path(filtered_results: list, save_dir="img/downloaded_images"):
    tasks = []
    # 이미지 다운로드 작업 생성
    for item in filtered_results:
        # item이 객ㅔ인지 딕셔너리인지에 따라 동적으로 처리
        if hasattr(item, 'similar_image_url'):
            similar_image_url = item.similar_image_url
            application_number = item.application_number
        else :
            similar_image_url = item['similar_image_url']
            application_number = item['application_number']

        if similar_image_url and application_number:
            # 이미지 다운로드 처리
            task = download_image_with_application_number(similar_image_url, application_number, save_dir)
            tasks.append((task, item))
        else:
            print(f"Skipping item due to missing data - similar_image_url: {similar_image_url}, application_number: {application_number}")

    # 비동기 다운로드 작업 수행
    results = await asyncio.gather(*[task for task, _ in tasks])

    updated_results = []
    # 다운로드된 이미지 경로를 필터링하여 결과 생성
    for (result, (_, item)) in zip(results, tasks):
        if hasattr(item, 'dict'):
            item_dict = item.dict()  # 객체를 dict로 변환
        elif isinstance(item, dict):
            item_dict = item
        else: 
            raise TypeError(f"지원되지않는 타입")
        if result:
            item_dict['image_path'] = result  # dict에 이미지 경로 추가
        updated_results.append(item_dict)

    save_to_json(updated_results, f'item_labeling.json')

    return updated_results  # updated_results 반환


async def updated_search_results(seperated_words, similarity_code=None, vienna_code=None, download_images=True):
    # 모든 검색 결과를 하나의 리스트에 저장하고 반환
    filtered_results = await search_and_save_all_results(seperated_words, similarity_code, vienna_code)

    # 2. 이미지 다운로드가 필요한 경우 다운로드 및 경로 추가
    if download_images:
        updated_results = await download_and_add_image_path(filtered_results)
        return updated_results
    else:
        return filtered_results


# async def updated_search_results_for_image(seperated_words, similarity_code=None, vienna_code=None):
#     # 1. 모든 검색 결과를 하나의 리스트에 저장하고 반환
#     filtered_results = await search_and_save_all_results(seperated_words, similarity_code, vienna_code)
#     # 2. 이미지를 저장하고, 경로를 함께 업데이트 
#     updated_results = await download_and_add_image_path(filtered_results)
    
#     return updated_results


# async def updated_search_results_for_text(seperated_words, similarity_code=None):

#     # 1. 모든 검색 결과를 하나의 리스트에 저장하고 반환
#     all_results = await search_and_save_all_results(seperated_words, similarity_code, None)

#     filtered_results =[]
#     for item in all_results:
#         filtered_item = {
#             '상표명' : item.get('title'),
#             '상품류' : item.get('classificationCode'),
#             '상태' : item.get('applicationStatus'),
#             '상표이미지' : item.get('bigDrawing'),
#             '출원/등록번호' : item.get('applicationNumber'),
#             '출원/등록일' : item.get('applicationDate'),
#             '출원인/등록권자' : item.get('applicantName'),
#         }
#         filtered_results.append([filtered_item])

#     return filtered_results