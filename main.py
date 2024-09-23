import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from brand_discernment.mes import discernment_create_thread_and_run
from brand_similarity.mes import similarity_create_thread_and_run, get_response
import kipris_api, similar, save_file, init, common


app = FastAPI()

class DisCernmentEvaluation(BaseModel):
    brand_name: str 
    brand_image_url: str

class SimilarityEvaluation(BaseModel):
    brand_name: str = ''
    brand_image_url: str
    similarity_code: str = ''
    vienna_code: str = ''
    
    
@app.post('/discernment', description="식별력 평가")
async def discernment_trademark(request: DisCernmentEvaluation):
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



@app.post("/similarity", description="유사도 평가 with KIPRIS")
async def similarity_trademark(request: SimilarityEvaluation):
    try:
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
        result_data = kipris_api.updated_search_results_for_image(search_words, request.similarity_code, request.vienna_code)

        all_responses = []
        download_image_paths = []

        for idx, result in enumerate(result_data):
            similar_image_path = result['image_path'] #유사 이미지 경로
            similar_image_url = result['similar_image_url']
            application_number = result['application_number'] # 출원번호
            classification_code = result['classification_code']
            vienna_code = result['vienna_code']

            #이미지 다운로드 경로 저장
            download_image_paths.append(similar_image_path)

            image_pair = [brand_image_path, similar_image_path]
            image_url_pair = [request.brand_image_url, similar_image_url]

            user_message = f"등록하고자 하는 이미지와(과) 유사성이 있을지 모르는 이미지 {idx + 1}입니다.\n 이 정보는 이사건 등록상표 입니다.: {brand_image_url} \n 다음 정보는 등록되어있는 유사한 이미지의 정보입니다:\n출원번호:{application_number}, 분류코드:{classification_code}, 비엔나코드: {vienna_code}, 이미지URL: {similar_image_url}\n 두 이미지를 비교하여 유사도를 분석하여 법적 자문을 주세요."
            thread, run = similarity_create_thread_and_run(user_message, image_pair, image_url_pair)

            #실행 완료 대기
            run = common.wait_on_run(run, thread)
            response = get_response(thread)
            all_responses.append(response)

        save_file.save_messages_to_md(all_responses, filename='assistant_response.md')

        save_file.delete_downloaded_images(download_image_paths)

        return{"message": all_responses}
    
    except Exception as e :
        raise HTTPException(status_code=500, detail = f"서버오류발생: {str(e)}")