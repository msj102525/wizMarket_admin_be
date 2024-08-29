from app.db.connect import commit
import pandas as pd

def insert_crime_data(connection, df, city_id, quarter):
    # "-" 값을 0으로 변환하고, NaN 값을 0으로 변환
    df.replace('-', 0, inplace=True)
    df.fillna(0, inplace=True)

    # 데이터 삽입
    with connection.cursor() as cursor:
        for index, row in df.iterrows():
            cursor.execute("""
                INSERT INTO crime (
                    CITY_ID, QUARTER, CRIME_MAJOR_CATEGORY, CRIME_MINOR_CATEGORY, 
                    INCIDENT_COUNT, ARREST_COUNT, INCIDENT_TO_ARREST_RATIO, 
                    ARREST_PERSONNEL, LEGAL_ENTITY
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                city_id,
                quarter,
                row['MajorCategory'],
                row['MinorCategory'],
                int(row['IncidentCount']),
                int(row['ArrestCount']),
                float(row['ArrestRatio']),
                int(row['ArrestPersonnel']),
                int(row['LegalEntity'])
            ))

    # 트랜잭션 커밋
    commit(connection)
