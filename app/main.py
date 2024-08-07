from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.api.endpoints import hello

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
