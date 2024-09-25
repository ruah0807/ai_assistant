from fastapi import FastAPI
from routes.pipeline import router


app = FastAPI()

routers = []

from routes import pipeline

#라우터 추가
app.include_router(pipeline.router)

@app.get("/")
async def main():
    return '서버 동작 중'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)