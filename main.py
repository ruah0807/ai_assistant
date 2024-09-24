import requests, time, asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from brand_discernment.mes import discernment_create_thread_and_run
from brand_similarity.mes import similarity_create_thread_and_run
from similar_img import mes_img
from similar_text import mes_text
import kipris_api, similar, save_file, init, common


app = FastAPI()

class DiscernmentEvaluation(BaseModel):
    brand_name: str 
    brand_image_url: str

class SimilarityEvaluation(BaseModel):
    brand_name: str = ''
    brand_image_url: str
    similarity_code: str = ''
    vienna_code: str = ''
    max_messages: int = 2

class SimilarityTextEvaluation(BaseModel):
    brand_name : str
    similarity_code : str
    
    
@app.post('/discernment', name="식별력 평가")
async def discernment_trademark(request: DiscernmentEvaluation):
    brand_name = request.brand_name
    brand_image_url = request.brand_image_url
    
    brand_image_path = save_file.download_image(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    # 스래드 생성
    thread, run = discernment_create_thread_and_run(
        f"""
        업로드한 이미지 상표 '{brand_name}'의 상표 식별력을 평가해주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )

    run= common.wait_on_run(run, thread)

    response = init.client.beta.threads.messages.list(thread_id=thread.id)
    messages = common.print_message(response)

    save_file.delete_downloaded_images(brand_image_path)

    return {"messages": messages}


@app.post("/similarity_report", name="상표유사여부보고서 형식의 유사도 평가 with KIPRIS",)
async def similarity_trademark(request: SimilarityEvaluation):

    return await process_similarity_evaluation(request, opinion_format="상표유사보고서")
    

@app.post("/similarity_img_opinion", name="의견서 형식의 이미지 유사도 평가 without 문서 검색",)
async def similarity_trademark_1(request: SimilarityEvaluation):
    return await process_similarity_evaluation(request, opinion_format="의견서형식 with 이미지")
    

@app.post("/similarity_text_opinion", name="의견서 형식의 테스트 유사도 평가 with 문서참고")
async def similar_text(request: SimilarityTextEvaluation):
    try:
        #입력받은 상표명과 유사성 코드를 기반으로 비슷한 단어 찾기
        similar_words = similar.generate_similar_barnd_names(request.brand_name)

        #상표 검색 수행
        result_data = kipris_api.updated_search_results_for_text(similar_words['words'], request.similarity_code)

        #메시지를 전송하기 위한 스레드 생성
        thread, run = await mes_text.create_thread_and_run(
            f"""
            제가 등록하고 싶은 상표명입니다.
            \n상표명 : {request.brand_name}\n상품류/유사군:{request.similarity_code}
            아래는 특허청에서 비슷한 상표를 검색한 데이터입니다. 업로드되어있는 문서를 기반으로 하여 10가지 상표명의 유사도를 명확하게 판단하고, 
            어떤 근거에 따라 유사성이 같은지 혹은 다른지를 소스를 주고 디테일하게 설명하세요.\n\n{result_data}""",
        )
        run = await common.wait_on_run(run, thread)
        response = common.get_response(thread)
        messages = common.print_message(response)

        return {"message": messages}

    except Exception as e :
        raise HTTPException(status_code=500, detail = f"서버오류 발생: {str(e)}")
    






########################################################################################################################################
#공통 함수 처리
async def process_similarity_evaluation(request: SimilarityEvaluation, opinion_format: str):
    try:
        start_time = time.time()
         #브랜드 이미지 다운로드
        brand_image_path = save_file.download_image(request.brand_image_url)
        if not brand_image_path:
            raise HTTPException(status_code=400, detail="이미지 파일 다운로드 실패")
        
        print(brand_image_path)

        #유사성 코드 및 비엔나 코드 설정
        search_words = []
        if request.brand_name:
            # 비슷한 단어 찾기
            similar_words = similar.generate_similar_barnd_names(request.brand_name)
            search_words = similar_words['words']
        else:
            # brand_name이 없으면 기본 빈 리스트로 설정
            print("상표이름 비어있음")
            search_words = []
        #상표 검색 수행
        result_data = await kipris_api.updated_search_results_for_image(search_words, request.similarity_code, request.vienna_code)

        all_responses = []
        download_image_paths = []

        tasks = []
        for idx, result in enumerate(result_data[:request.max_messages]):
            task = handle_single_result(result, idx, request, opinion_format, brand_image_path, all_responses, download_image_paths)
            tasks.append(task)

        # 비동기적으로 병렬 처리
        await asyncio.gather(*tasks)

        # save_file.save_messages_to_md(all_responses, filename='assistant_response.md')
        end_time = time.time()
        total_duration = end_time - start_time
        print(f"전체 처리 시간: {int(total_duration // 60)}분 {total_duration %60:.2f}초")

        save_file.delete_downloaded_images(download_image_paths)

        return{"message": all_responses}
    
    except Exception as e :
        raise HTTPException(status_code=500, detail = f"서버오류발생: {str(e)}")



async def handle_single_result(result, idx, request, opinion_format, brand_image_path, all_responses, download_image_paths):
    """ 개별 결과처리 함수"""
    try:
        similar_image_path = result['image_path']
        similar_image_url = result['similar_image_url']
        application_number = result['application_number']
        classification_code = result['classification_code']
        vienna_code = result['vienna_code']

        # 이미지 다운로드 경로 저장
        download_image_paths.append(similar_image_path)

        image_pair = [brand_image_path, similar_image_path]
        image_url_pair = [request.brand_image_url, similar_image_url]

        user_message = f"등록하고자 하는 이미지와(과) 유사성이 있을지 모르는 이미지 {idx + 1}입니다.\n 이 정보는 이사건 등록상표 입니다.: {request.brand_image_url} \n 다음 정보는 등록되어있는 유사한 이미지의 정보입니다:\n출원번호:{application_number}, 분류코드:{classification_code}, 비엔나코드: {vienna_code}, 이미지URL: {similar_image_url}\n 두 이미지를 비교하여 유사도를 분석하여 법적 자문을 주세요."

        # 메시지 전송 및 thread 생성
        if opinion_format == "상표유사보고서":
            thread, run = await similarity_create_thread_and_run(user_message, image_pair, image_url_pair)
        else:
            thread, run = await mes_img.create_thread_and_run(user_message, image_pair, image_url_pair)

        # 실행 완료 대기
        run = await common.wait_on_run(run, thread)  # 비동기 대기
        response = common.get_response(thread)
        messages = common.print_message(response)
        all_responses.append(messages)
    
    except Exception as e:
        print(f"Error handling result {idx}: {str(e)}")

########################################################################################################################################




