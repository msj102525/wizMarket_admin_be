from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.api.endpoints import hello
from app.api.endpoints import testchrome
from app.api.endpoints import getmonthpop
from app.api.endpoints import testopenup
from multiprocessing import cpu_count

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
app.include_router(testchrome.router)
app.include_router(getmonthpop.router)
app.include_router(testopenup.router)

print(f"최대 CPU 개수는 {cpu_count()}.")