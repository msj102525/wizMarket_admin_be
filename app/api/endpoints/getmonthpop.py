from fastapi import APIRouter, HTTPException, Body
from app.crud.population_data import get_population_data

router = APIRouter()

@router.post("/getmonthpop")
async def get_month_population(
    srchFrYm: str = Body(..., embed=True, description="Search From Year-Month in YYYYMM format"),
    srchToYm: str = Body(..., embed=True, description="Search To Year-Month in YYYYMM format"),
    region: str = Body(..., embed=True, description="Region Code"),
    subRegion: str = Body(..., embed=True, description="Sub Region Code")
):
    try:
        result = await get_population_data(srchFrYm, srchToYm, region, subRegion)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
