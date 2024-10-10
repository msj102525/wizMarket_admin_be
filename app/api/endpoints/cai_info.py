from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
import httpx

router = APIRouter()


@router.get("")
async def get_cai_api_by_city(city: str):
    load_dotenv()
    cai_api_key = os.getenv("CAI_API_KEY")

    if not cai_api_key:
        raise HTTPException(status_code=500, detail="API key not found")

    # print(f"City: {city}")

    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
    params = {
        "serviceKey": cai_api_key,
        "returnType": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "sidoName": city,
        "ver": "1.3",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request Error: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=response.status_code, detail=f"HTTP Error: {e}"
            )
