-- LOCAL_STORE 테이블에 인덱스 생성
CREATE INDEX idx_local_store_city_district_sub
ON LOCAL_STORE (CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID);

-- CITY 테이블에 인덱스 생성
CREATE INDEX idx_city_id
ON CITY (CITY_ID);

-- DISTRICT 테이블에 인덱스 생성
CREATE INDEX idx_district_id
ON DISTRICT (DISTRICT_ID);

-- SUB_DISTRICT 테이블에 인덱스 생성
CREATE INDEX idx_sub_district_id
ON SUB_DISTRICT (SUB_DISTRICT_ID);
--