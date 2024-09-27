from fastapi import APIRouter, HTTPException
import time, asyncio
from typing import List, Optional
from pydantic import BaseModel
import kipris_control, file_handler, common
import comparison.mes as similarity

router = APIRouter(
    prefix="/assistant",
    tags=["Comepare Brands"]
)

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
    kipris_data: List[LabeledKiprisItems]
    
    

@router.post("/comepare_brands", name="각각의 상표 유사도를 평가하는 Assistant")
async def compare_brand(request:SimilarityEvaluationRequest):
    try:    
        start_time = time.time()
        # 1. 브랜드 이미지 다운로드
        brand_image_path = file_handler.download_image(request.brand_image_url)

        if not brand_image_path:
            raise HTTPException(status_code=400, detail="이미지 파일 다운로드 실패")
        print(f"브랜드 이미지 경로: {brand_image_path}")

        # 2. kipris 데이터 이미지 다운로드 및 경로 추가
        result_data = await kipris_control.download_and_add_image_path(request.kipris_data)

        all_responses = []
        download_image_paths = [brand_image_path]

        tasks = []
        for idx, result in enumerate(result_data):
            task = score_result(result, idx, request, brand_image_path, all_responses, download_image_paths)
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
    



async def score_result(result, idx, request, brand_image_path, all_responses, download_image_paths):
    """ 개별 결과처리 함수"""
    try:
        # 딕셔너리로 접근하도록 수정
        similar_image_path = result.get('image_path')
        similar_image_url = result.get('similar_image_url')
        application_number = result.get('application_number')
        classification_code = result.get('classification_code')
        vienna_code = result.get('vienna_code')

        # 이미지 다운로드 경로 저장
        download_image_paths.append(similar_image_path)

        image_pair = [brand_image_path, similar_image_path]
        image_url_pair = [request.brand_image_url, similar_image_url]

        user_message = f"""
        상표 이미지 비교를 요청합니다.
        등록대상상표 : {request.brand_image_url}
        선등록상표 : {similar_image_url}

        """

        thread, run = await similarity.similarity_create_thread_and_run(user_message, image_pair, image_url_pair)

        messages = await common.handle_run_response(run,thread)
        all_responses.append(messages)
    
    except Exception as e:
        print(f"Error handling result {idx}: {str(e)}")
