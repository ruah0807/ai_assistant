import os,sys, time, asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import b_similar_posibility_image.execute as filter_similarity
import c_brand_similarity.execute as similarity
import a_create_names.create_names as create_names
import kipris.kipris_control as kipris_control
import file_handler
import a_similarity_code.execute as similar_code
import a_vienna_code.execute as vienna


async def similarity_pipeline(brand_name, description, request_similarity_code, brand_image_url, num_of_rows, only_null_vienna_search, filter, exclude_application_number, exclude_registration_number, application_date, format_type):
    
    # Step 1 : brand유사 상표명 검색
    if brand_name:
        print(f"\n'{brand_name}'에 대한 유사 상표명 검색 중...\n")
        similar_words = create_names.generate_similar_barnd_names(brand_name, description)
        if not similar_words:
            return{"error": "비슷한 단어를 찾을 수 없습니다."} 
        search_words = similar_words['words']
    else : 
        search_words = [""]


    # Step 2 : request_similarity_code 로 similarity_code 생성
    similarity_code_data = await similar_code.similarity_code_finding_logic(request_similarity_code)
    similarity_code = similarity_code_data.get('combined_similarity_code', None)
    print(f"\n생성된 유사코드 : {similarity_code}\n")


    # Step 3 : brand_image_url로 vienna_code 생성
    if only_null_vienna_search:
        vienna_code= None
        print("\n비엔나코드를 생성하지 않고 vienna_code가 null 값인 것만 반환\n")
    else:
        vienna_code_data = await vienna.process_vienna_code(brand_image_url)
        vienna_code = vienna_code_data.get('combined_vienna_code', None)
        print(f"\n생성된 비엔나 코드 : {vienna_code}\n")


    # Step 4 : 유사상표명 KIPRIS 검색 수행
    kipris_result = await kipris_control.search_and_save_all_results(
        search_words,
        similarity_code,
        vienna_code,
        num_of_rows,
        only_null_vienna_search,
        exclude_application_number, exclude_registration_number, application_date
    )
    if not kipris_result:
            raise ValueError("KIPRIS 데이터가 검색되지 않았습니다. 검색 조건을 다시 확인해주세요.")

    # Step 5 : brand 이미지 다운로드
    brand_image_path = file_handler.download_image(brand_image_url)
    if not brand_image_path:
        return {"detail" :"이미지 파일 다운로드 실패"}
    print(f"\n브랜드 이미지 경로: {brand_image_path}\n")

    # Step 5 : Kipris 데이터 이미지 다운로드 및 경로 추가
    result_data = await kipris_control.download_and_add_image_path(kipris_result)
    print(f"\n총 데이터 갯수 : {len(result_data)}\n")

    request = {'brand_name': brand_name,'brand_image_url': brand_image_url}

    download_image_paths = [brand_image_path]

    # Step 5.5 : filter가 True라면 kipris검색 데이터 유사 데이터 찾기 필터링 실행( 검색어가 많을 경우 )
    if filter:
        all_responses = []
        tasks = []
        print(f"\n필터링을 시작합니다...\n")
        for idx, result in enumerate(result_data):
            task = filter_similarity.score_result(result, idx, request, brand_image_path, all_responses, download_image_paths)
            tasks.append(task)
        # 비동기적으로 병렬 처리
        await asyncio.gather(*tasks)
        filtered_results = [response for response in all_responses if response.get("similarity")==True]
        print(f"\n필터링된 데이터 갯수 : {len(filtered_results)}\n")
    else : 
        # filter가 false일 때는 모든 result_data를 사용
        filtered_results = result_data
        print(f"\n데이터 유사도 분석을 시작합니다.\n")

    # Step 6 : 유사보고서 작성 
    all_responses = [] # similarity 결과를 위한 새로운 리스트
    tasks = []
    for idx, result in enumerate(filtered_results):
        task = similarity.handle_single_result(result, idx, request, brand_image_path, all_responses, download_image_paths, format_type=format_type)
        tasks.append(task)
    # 비동기적으로 병렬 처리
    await asyncio.gather(*tasks)

    file_handler.delete_downloaded_images(download_image_paths)

    return{
        "brand_name": brand_name,
        "brand_image_url": brand_image_url,
        "brand_image_path": brand_image_path,
        "estimated_similarity_code": similarity_code,
        "estimated_vienna_code": vienna_code,
        "kipris_data": all_responses, 
        }


    
####################################################################################################



# # 실행 예시
# async def main():
#     start_time = time.time()

#     await similarity_pipeline(
#         brand_name = "mindshare",
#         brand_image_url= "https://kipris.s3.ap-northeast-2.amazonaws.com/mindshare.png",
#         similarity_code="G390802|S123301|S120505",   # 유사코드 (필요에 따라 변경)
#         vienna_code="",  # 비엔나 코드
#         num_of_rows= 5, # 검색 결과 수
#         only_null_vienna_search=True,  # 비엔나 코드 필터링 여부
#         filter=True
#     )
#     end_time = time.time()
#     total_duration = end_time - start_time
#     total_duration = f"전체 처리 시간: {int(total_duration // 60)}분 {total_duration %60:.2f}초"
#     print(total_duration)



# # 비동기 함수 실행
# if __name__ == "__main__":
#     asyncio.run(main())