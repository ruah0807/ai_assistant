import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from brand_discernment.mes import create_thread_and_run, wait_on_run, print_message, get_response
import kipris_api, similar, save_file, init


app = FastAPI()

class TrademarkRequest(BaseModel):
    brand_name: str
    brand_image_url: str
    
@app.post('/discernment')
async def discernment_trademark(request: TrademarkRequest):
    brand_name = request.brand_name
    brand_image_url = request.brand_image_url
    
    brand_image_path = save_file.download_image_from_url(brand_image_url)
    
    if not brand_image_path:
        raise HTTPException(status_code=400, detail="이미지 다운로드 실패")
    
    #스레드 생성 및 메시지 제출
    # 스래드 생성
    thread, run = create_thread_and_run(
        f"""
        업로드한 이미지 상표 '{brand_name}'의 상표 식별력을 평가해주세요.
        """, 
        image_path=brand_image_path, 
        image_url= brand_image_url
        )

    run= wait_on_run(run, thread)

    response = init.client.beta.threads.messages.list(thread_id=thread.id)
    messages = print_message(response)

    return {"messages": messages}