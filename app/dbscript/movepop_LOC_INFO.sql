CREATE TABLE semin.movepopdata LIKE test.movepopdata;
INSERT INTO semin.movepopdata SELECT * FROM test.movepopdata;

-- 1. city_id, district_id, sub_district_id 컬럼 추가
ALTER TABLE movepopdata
ADD COLUMN city_id INT,
ADD COLUMN district_id INT,
ADD COLUMN sub_district_id INT;

-- 2. 외래 키 제약 조건 추가
ALTER TABLE movepopdata
ADD CONSTRAINT fk_city_id FOREIGN KEY (city_id) REFERENCES city(city_id),
ADD CONSTRAINT fk_district_id FOREIGN KEY (district_id) REFERENCES district(district_id),
ADD CONSTRAINT fk_sub_district_id FOREIGN KEY (sub_district_id) REFERENCES sub_district(sub_district_id);

-- 3. keyword 기반으로 city_id, district_id, sub_district_id 값 설정
UPDATE movepopdata m
JOIN city c ON m.keyword LIKE CONCAT('%', c.city_name, '%')
JOIN district d ON m.keyword LIKE CONCAT('%', d.district_name, '%')
JOIN sub_district s ON m.keyword LIKE CONCAT('%', s.sub_district_name, '%')
SET 
    m.city_id = c.city_id,
    m.district_id = d.district_id,
    m.sub_district_id = s.sub_district_id;

-- 4. person, price, wrcppl, earn, cnsmp, hhCnt, rsdppl 컬럼의 단위 제거
UPDATE movepopdata
SET 
    person = REPLACE(person, ' 명', ''),
    price = REPLACE(REPLACE(price, ' 만원', ''), ',', ''),
    wrcppl = REPLACE(wrcppl, ' 명', ''),
    earn = REPLACE(REPLACE(earn, ' 만원', ''), ',', ''),
    cnsmp = REPLACE(REPLACE(cnsmp, ' 만원', ''), ',', ''),
    hhCnt = REPLACE(hhCnt, ' 세대', ''),
    rsdppl = REPLACE(rsdppl, ' 명', '');

-- 5. 기존 기본 키 제거 (이전에 정의된 PRIMARY KEY 컬럼 제거)
ALTER TABLE movepopdata
DROP PRIMARY KEY;

-- 6. temp_yearmonth라는 임시 컬럼 생성
ALTER TABLE movepopdata ADD COLUMN temp_yearmonth VARCHAR(10);

-- 7. temp_yearmonth 컬럼에 yearmonth 데이터를 변환하여 저장합니다.
UPDATE movepopdata
SET temp_yearmonth = CONCAT(SUBSTRING(yearmonth, 1, 4), '-', SUBSTRING(yearmonth, 5, 2), '-01')
WHERE LENGTH(yearmonth) = 6;

-- 8. yearmonth 컬럼을 삭제하고 temp_yearmonth 컬럼을 사용하여 대체합니다.
ALTER TABLE movepopdata DROP COLUMN yearmonth;
ALTER TABLE movepopdata CHANGE COLUMN temp_yearmonth yearmonth DATE;

-- 9. 컬럼 이름 및 자료형 변경, LOC_INFO_ID 기본 키 추가
ALTER TABLE movepopdata
CHANGE COLUMN `person` `MOVE_POP` INT,
CHANGE COLUMN `price` `SALES` INT,
CHANGE COLUMN `wrcppl` `WORK_POP` INT,
CHANGE COLUMN `earn` `INCOME` INT,
CHANGE COLUMN `cnsmp` `SPEND` INT,
CHANGE COLUMN `hhCnt` `HOUSE` INT,
CHANGE COLUMN `rsdppl` `RESIDENT` INT,
ADD COLUMN `LOC_INFO_ID` INT AUTO_INCREMENT PRIMARY KEY;

ALTER TABLE movepopdata RENAME TO LOC_INFO;