from fastapi import FastAPI


app = FastAPI()

routers = []

from routes import pipeline, individual

#라우터 추가
app.include_router(pipeline.router)
app.include_router(individual.router)

@app.get("/")
async def main():
    return '서버 동작 중'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)