from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.api.endpoints import hello, rising_business, commercial_district
# from app.api.endpoints import testchrome
from app.api.endpoints import movepop
from app.api.endpoints import population

app = FastAPI()

load_dotenv()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(os.getenv("ALLOWED_ORIGINS", ""))


@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI!"}


app.include_router(hello.router, prefix="/hello")
# app.include_router(testchrome.router)
app.include_router(population.router, prefix="/population")
app.include_router(movepop.router)
app.include_router(commercial_district.router, prefix="/commercial")
# app.include_router(rising_business.router, prefix="/rising")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
