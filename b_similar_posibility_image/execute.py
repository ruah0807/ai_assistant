import common
import b_similar_posibility_image.mes as similarity


async def score_result(result, idx, request, brand_image_path, all_responses, download_image_paths, expect_json=True):
    """ 개별 결과처리 함수"""
    try:
        # 딕셔너리로 접근하도록 수정
        similar_title = result.get('title')
        similar_image_path = result.get('similar_image_path')
        similar_image_url = result.get('similar_image_url')
        application_number = result.get('application_number')
        classification_code = result.get('classification_code')
        vienna_code = result.get('vienna_code')

        # 이미지 다운로드 경로 저장
        download_image_paths.append(similar_image_path)


        image_pair = [brand_image_path, similar_image_path]
        
        # request가 객체인지 딕셔너리인지 확인
        if isinstance(request, dict):
            brand_image_url = request['brand_image_url']
            brand_name = request['brand_name']
        else:
            brand_image_url = request.brand_image_url
            brand_name = request.brand_name

        image_url_pair = [brand_image_url, similar_image_url]

        user_message = f"""
        {idx + 1}번째 상표 이미지 비교를 요청합니다.
        등록대상상표 : {brand_image_url}
        등록대상상표명 : {brand_name}
        선등록상표 : {similar_image_url}
        선등록상표 경로 : {similar_image_path}
        선등록상표명 : {similar_title}
        출원번호: {application_number}, 분류코드: {classification_code}, 비엔나코드: {vienna_code}
        아주 조금이라도 유사하다 판단 한것을 true로 필터링해주세요.
        """

        thread, run = await similarity.similarity_create_thread_and_run(user_message, image_pair, image_url_pair)

        messages = await common.handle_run_response(run,thread, expect_json=expect_json)
        if messages:
            all_responses.append(messages)
    
    except Exception as e:
        print(f"Error handling result {idx}: {str(e)}")
