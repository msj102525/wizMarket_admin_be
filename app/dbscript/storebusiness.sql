DROP TABLE IF EXISTS store_business;

CREATE TABLE store_business (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- 자동 증가 ID (프라이머리 키)
    business_name VARCHAR(255),         -- 상호명
    branch_name VARCHAR(255),           -- 지점명
    major_category VARCHAR(255),        -- 상권업종대분류명
    middle_category VARCHAR(255),       -- 상권업종중분류명
    minor_category VARCHAR(255),        -- 상권업종소분류명
    standard_industry_code VARCHAR(255),-- 표준산업분류명
    city VARCHAR(255),                  -- 시도명
    district VARCHAR(255),              -- 시군구명
    administrative_dong_code VARCHAR(255), -- 행정동코드
    administrative_dong_name VARCHAR(255), -- 행정동명
    legal_dong_code VARCHAR(255),       -- 법정동코드
    legal_dong_name VARCHAR(255),       -- 법정동명
    land_category VARCHAR(255),         -- 대지구분명
    lot_number_address VARCHAR(255),    -- 지번주소
    building_name VARCHAR(255),         -- 건물명
    road_name_address VARCHAR(255),     -- 도로명주소
    building_unit_info VARCHAR(255),    -- 동정보
    floor_info VARCHAR(255),            -- 층정보
    unit_number VARCHAR(255),           -- 호정보
    year_quarter VARCHAR(255)           -- 몇년도 몇분기
);

