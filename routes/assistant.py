import time, asyncio
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import brand_discernment.mes as discernment
import brand_similarity.mes as similarity
import kipris_control, file_handler, common

router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"]
)

class DiscernmentEvaluation(BaseModel):
    brand_name: str 
    brand_image_url: str

class LabeledKiprisItems(BaseModel):
    title: Optional[str] = None
    classification_code: Optional[str] = None
    similar_image_url: Optional[str] = None
    application_number: Optional[str] = None
    vienna_code : Optional[str] = None
    image_path: str = None

class SimilarityEvaluationRequest(BaseModel):
    brand_name: Optional[str] = None
    brand_image_url: str
    brand_image_path: str
    kipris_data: List[LabeledKiprisItems]
    
    
@router.post('/discernment', name="식별력 평가")
async def discernment_trademark(request: DiscernmentEvaluation):
    start_time = time.time()
    brand_name = request.brand_name
    brand_image_url = request.brand_image_url
    
    brand_image_path = file_handler.download_image(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    # 스래드 생성
    thread, run = discernment.discernment_create_thread_and_run(
        f"""
        업로드한 이미지 상표 '{brand_name}'의 상표 식별력을 평가해주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )

    messages = await common.handle_run_response(run,thread)

    file_handler.delete_downloaded_images(brand_image_path)
    
    end_time = time.time()
    total_duration = end_time - start_time
    total_duration = f"전체 처리 시간: {int(total_duration // 60)}분 {total_duration %60:.2f}초"
    print(total_duration)

    return {"messages": messages, "ducation": total_duration}


@router.post("/evaluate-similarity", name="상표유사여부보고서(별책).pdf를 참고한 형식의 유사도 평가(IMAGE포함)")
async def evaluate_similarity(request:SimilarityEvaluationRequest):
    try:    
        start_time = time.time()
        # # 1. 브랜드 이미지 다운로드
        # brand_image_path = file_handler.download_image(request.brand_image_url)

        # if not brand_image_path:
        #     raise HTTPException(status_code=400, detail="이미지 파일 다운로드 실패")
        # print(f"브랜드 이미지 경로: {brand_image_path}")

        # 2. kipris 데이터 이미지 다운로드 및 경로 추가
        result_data = await kipris_control.download_and_add_image_path(request.kipris_data)

        all_responses = []
        download_image_paths = [request.brand_image_path]

        tasks = []
        for idx, result in enumerate(result_data):
            task = handle_single_result(result, idx, request, request.brand_image_path, all_responses, download_image_paths)
            tasks.append(task)

        # 비동기적으로 병렬 처리
        await asyncio.gather(*tasks)

        end_time = time.time()
        total_duration = end_time - start_time
        total_duration = f"전체 처리 시간: {int(total_duration // 60)}분 {total_duration %60:.2f}초"
        print(total_duration)

        file_handler.delete_downloaded_images(download_image_paths)

        return{"message": all_responses, "processing_time": total_duration}
    
    except Exception as e :
        raise HTTPException(status_code=500, detail = f"서버오류발생: {str(e)}")
    

async def handle_single_result(result, idx, request, brand_image_path, all_responses, download_image_paths, expect_json=False):
    """ 개별 결과처리 함수"""
    try:
        # 딕셔너리로 접근하도록 수정
        similar_title = result.get('title')
        similar_image_path = result.get('image_path')
        similar_image_url = result.get('similar_image_url')
        application_number = result.get('application_number')
        classification_code = result.get('classification_code')
        vienna_code = result.get('vienna_code')

        # 이미지 다운로드 경로 저장
        download_image_paths.append(similar_image_path)

        image_pair = [brand_image_path, similar_image_path]
        image_url_pair = [request.brand_image_url, similar_image_url]

        user_message = f"""등록하고자 하는 이미지와(과) 유사성이 있을지 모르는 이미지 {idx + 1}입니다.

        이 정보는 이사건 등록상표 입니다.: 
        등록대상상표: {request.brand_image_url}
        상표명: {request.brand_name}

        다음 정보는 등록되어있는 유사한 이미지의 정보입니다:

        출원번호:{application_number},
        선등록상표명: {similar_title}
        분류코드:{classification_code},
        비엔나코드: {vienna_code}, 
        이미지URL: {similar_image_url}
        
        
        두 이미지를 비교하여 유사도를 분석하여 법적 자문을 주세요.
        
        """

        thread, run = await similarity.similarity_create_thread_and_run(user_message, image_pair, image_url_pair)

        messages = await common.handle_run_response(run,thread, expect_json=expect_json)
        all_responses.append(messages)
    
    except Exception as e:
        print(f"Error handling result {idx}: {str(e)}")



