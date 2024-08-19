from fastapi import APIRouter, HTTPException, Body
from app.crud.movepop import get_population_data

router = APIRouter()

@router.post('/getmovepop')
async def get_month_population(
    srchFrYm: str = Body(..., embed=True, description="Search From Year-Month in YYYYMM format"),
    srchToYm: str = Body(..., embed=True, description="Search To Year-Month in YYYYMM format"),
    region: str = Body(..., embed=True, description="Region Code"),
):
    try:
        result = await get_population_data(srchFrYm, srchToYm, region)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))