from fastapi import FastAPI

app = FastAPI()

routers = []

from routes import a_find_similar_vienna_code, a_individual,b_mid_assistant, c_last_assistant, pipeline

#라우터 추가
# app.include_router(pipeline.router)
app.include_router(a_find_similar_vienna_code.router)
app.include_router(a_individual.router)
app.include_router(b_mid_assistant.router)
app.include_router(c_last_assistant.router)

@app.get("/")
async def main():
    return '서버 동작 중'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)