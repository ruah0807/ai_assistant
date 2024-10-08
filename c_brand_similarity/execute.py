import c_brand_similarity.mes as report
import c_similar_img.mes_img as opinion
import common


async def handle_single_result(result, idx, request, brand_image_path, all_responses, download_image_paths, format, expect_json=False):
    """ 개별 결과처리 함수"""
    try:
        # result가 딕셔너리인지 Pydantic 모델인지에 따라 다른 방식으로 처리
        if isinstance(result, dict):
            # 딕셔너리일 경우
            similar_title = result.get('title')
            similar_image_url = result.get('similar_image_url')
            similar_image_path = result.get('similar_image_path')
            application_number = result.get('application_number')
            classification_code = result.get('classification_code')
            vienna_code = result.get('vienna_code')
        elif hasattr(result, 'title'):  # Pydantic 모델일 경우 점 표기법으로 접근
            similar_title = result.title
            similar_image_url = result.similar_image_url
            similar_image_path = result.similar_image_path
            application_number = result.application_number
            classification_code = result.classification_code
            vienna_code = result.vienna_code
        else:
            # 예상하지 못한 타입일 경우 예외 처리
            raise ValueError(f"Unexpected result type: {type(result)}")

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

        user_message = f"""등록하고자 하는 이미지와(과) 유사성이 있을지 모르는 이미지 {idx + 1}입니다.

        이 정보는 이사건 등록상표 입니다.: 
        등록대상상표: {brand_image_url}
        상표명: {brand_name}

        다음 정보는 등록되어있는 유사한 이미지의 정보입니다:

        출원번호:{application_number},
        선등록상표명: {similar_title}
        분류코드:{classification_code},
        비엔나코드: {vienna_code}, 
        이미지URL: {similar_image_url}
        
        두 이미지를 비교하여 유사도를 분석하여 법적 자문을 주세요.
        """

        if format == "report":
            thread, run = await report.similarity_create_thread_and_run(user_message, image_pair, image_url_pair)
        else:
            thread, run = await opinion.create_thread_and_run(user_message, image_pair, image_url_pair)

        messages = await common.handle_run_response(run,thread, expect_json=expect_json)
        all_responses.append(messages)
    
    except Exception as e:
        print(f"Error handling result {idx}: {str(e)}")
