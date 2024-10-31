-- CITY 테이블에 인덱스 생성
CREATE INDEX idx_city_id
ON CITY (CITY_ID);

-- DISTRICT 테이블에 인덱스 생성
CREATE INDEX idx_district_id
ON DISTRICT (DISTRICT_ID);

-- SUB_DISTRICT 테이블에 인덱스 생성
CREATE INDEX idx_sub_district_id
ON SUB_DISTRICT (SUB_DISTRICT_ID);


-- 상권 정보 외래 키 인덱스
CREATE INDEX idx_city_id ON `COMMERCIAL_DISTRICT` (`CITY_ID`);
CREATE INDEX idx_district_id ON `COMMERCIAL_DISTRICT` (`DISTRICT_ID`);
CREATE INDEX idx_sub_district_id ON `COMMERCIAL_DISTRICT` (`SUB_DISTRICT_ID`);
CREATE INDEX idx_biz_main_category_id ON `COMMERCIAL_DISTRICT` (`BIZ_MAIN_CATEGORY_ID`);
CREATE INDEX idx_biz_sub_category_id ON `COMMERCIAL_DISTRICT` (`BIZ_SUB_CATEGORY_ID`);
CREATE INDEX idx_biz_detail_category_id ON `COMMERCIAL_DISTRICT` (`BIZ_DETAIL_CATEGORY_ID`);

-- 상권 정보 자주 사용될 컬럼 인덱스
CREATE INDEX idx_market_size ON `COMMERCIAL_DISTRICT` (`MARKET_SIZE`);
CREATE INDEX idx_average_sales ON `COMMERCIAL_DISTRICT` (`AVERAGE_SALES`);
CREATE INDEX idx_operating_cost ON `COMMERCIAL_DISTRICT` (`OPERATING_COST`);
CREATE INDEX idx_food_cost ON `COMMERCIAL_DISTRICT` (`FOOD_COST`);
CREATE INDEX idx_employee_cost ON `COMMERCIAL_DISTRICT` (`AVERAGE_PAYMENT`); -- 평균 결제 인건비X
CREATE INDEX idx_rental_cost ON `COMMERCIAL_DISTRICT` (`RENTAL_COST`);
CREATE INDEX idx_average_profit ON `COMMERCIAL_DISTRICT` (`AVERAGE_PROFIT`);


-- 매장 정보 외래키 인덱스
CREATE INDEX idx_local_store_city_id ON LOCAL_STORE (CITY_ID);
CREATE INDEX idx_local_store_district_id ON LOCAL_STORE (DISTRICT_ID);
CREATE INDEX idx_local_store_sub_district_id ON LOCAL_STORE (SUB_DISTRICT_ID);
CREATE INDEX idx_local_store_reference_id ON LOCAL_STORE (REFERENCE_ID);


-- 매장 정보 자주 사용될 컬럼 인덱스
CREATE INDEX idx_local_store_store_business_number ON LOCAL_STORE (STORE_BUSINESS_NUMBER);
CREATE INDEX idx_local_store_store_name ON LOCAL_STORE (STORE_NAME);
CREATE INDEX idx_local_store_is_exist_all_region_id ON LOCAL_STORE (IS_EXIST, CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID);
CREATE INDEX idx_local_store_is_exist ON LOCAL_STORE (IS_EXIST);


-- 입지 정보 외래키 인덱스
CREATE INDEX idx_loc_info_city_id ON LOC_INFO (CITY_ID);
CREATE INDEX idx_loc_info_distirct_id ON LOC_INFO (DISTRICT_ID);
CREATE INDEX idx_loc_info_sub_district_id ON LOC_INFO (SUB_DISTRICT_ID);
CREATE INDEX idx_loc_info_reference_id ON LOC_INFO (REFERENCE_ID);


-- 입지 정보 자주 사용될 컬럼 인덱스
CREATE INDEX idx_loc_info_all_region_id ON LOC_INFO (CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID);
CREATE INDEX idx_loc_info_city_district_id ON LOC_INFO (CITY_ID, DISTRICT_ID);
CREATE INDEX idx_loc_info_y_m ON LOC_INFO (Y_M);


-- 입지 정보 통계 외래키 인덱스
CREATE INDEX idx_loc_info_stat_city_id ON LOC_INFO_STATISTICS (CITY_ID);
CREATE INDEX idx_loc_info_stat_district_id ON LOC_INFO_STATISTICS (DISTRICT_ID);
CREATE INDEX idx_loc_info_stat_sub_district_id ON LOC_INFO_STATISTICS (SUB_DISTRICT_ID);
CREATE INDEX idx_loc_info_stat_reference_id ON LOC_INFO_STATISTICS (REFERENCE_ID);


-- 입지 정보 통계 자주 사용될 컬럼 인덱스
CREATE INDEX idx_loc_info_stat_all_region_id ON LOC_INFO_STATISTICS (CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID);
CREATE INDEX idx_loc_info_stat_city_district_id ON LOC_INFO_STATISTICS (CITY_ID, DISTRICT_ID);
CREATE INDEX idx_loc_info_stat_ref_date ON LOC_INFO_STATISTICS (REF_DATE);