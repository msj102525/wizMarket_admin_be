from fastapi import APIRouter, HTTPException, Body
from app.schemas.population import *
from app.service.population import *
import pandas as pd
import io
from fastapi.responses import StreamingResponse



router = APIRouter()




@router.post("/select_population")
async def select_population(filters: PopulationSearch):
    # 입력된 필터 데이터만 딕셔너리로 변환 (unset된 필드는 제외)
    filters_dict = filters.dict(exclude_unset=True)
    try:
        # 필터 데이터를 서비스 레이어로 전달하여 결과 가져옴
        result = await filter_population_data(filters_dict)
        print(result)
        return {"filtered_data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")
    


# 예시: 연령대에 따른 나이 범위 설정
age_groups = {
    "age_under_10": range(0, 10),
    "age_10s": range(10, 20),
    "age_20s": range(20, 30),
    "age_30s": range(30, 40),
    "age_40s": range(40, 50),
    "age_50s": range(50, 60),
    "age_60_plus": range(60, 111)  # 60세 이상은 60세부터 110세까지 포함
}


@router.post("/download")
async def download(filters: PopulationSearch):
    # 입력된 필터 데이터를 딕셔너리로 변환 (unset된 필드는 제외)
    filters_dict = filters.dict(exclude_unset=True)
    print(filters_dict)

    try:
        # 서비스 레이어를 통해 필터 데이터 기반의 결과 가져오기
        result = await download_data(filters_dict)
        print(result)
        
        # 기본적으로 가져올 컬럼들 (지역 및 성별)
        column_names = ['시/도 명', '시/군/구 명', '읍/면/동 명', '남성 총 인구', '여성 총 인구', '기준 날짜', '성별']

        # 연령대 필터에 따른 동적 컬럼 생성
        age_columns = []
        if filters_dict.get('ageGroupMin') or filters_dict.get('ageGroupMax'):
            # ageGroupMin 또는 ageGroupMax 값이 있으면 해당 값에 맞는 나이 범위를 설정
            min_age_range = age_groups[filters_dict.get('ageGroupMin', 'age_under_10')]  # 최소값 없으면 0~10세로 설정
            max_age_range = age_groups[filters_dict.get('ageGroupMax', 'age_60_plus')]   # 최대값 없으면 60세 이상으로 설정
        else:
            # 나이 필터가 없으면 전체 범위 (0세 ~ 110세 이상)
            min_age_range = age_groups['age_under_10']
            max_age_range = age_groups['age_60_plus']

        # 나이 범위에 해당하는 컬럼 이름 생성
        age_columns = [f"age_{i}" for i in range(min(min_age_range), max(max_age_range) + 1)]
        
        # 나이 관련 컬럼을 최종 컬럼 이름 리스트에 추가
        column_names += age_columns

        print(column_names)

        # 튜플 데이터를 DataFrame으로 변환 (컬럼 이름을 동적으로 설정)
        df = pd.DataFrame(result, columns=column_names)

        print('asd1')
        
        # 메모리 내에서 엑셀 파일 생성
        output = io.BytesIO()
        print('asd2')
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        print('asd3')
        output.seek(0)  # 파일 포인터를 처음으로 이동
        print('asd4')
        
        
        # 엑셀 파일을 클라이언트에 반환
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename=population_data.xlsx'}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")