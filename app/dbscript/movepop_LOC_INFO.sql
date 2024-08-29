-- 기존 데이터 LOC_INFO 로 복사

INSERT INTO semin.LOC_INFO (
    CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID, SHOP, MOVE_POP, SALES, WORK_POP, INCOME, SPEND, HOUSE, RESIDENT, Y_M, CREATED_AT, UPDATED_AT
)
SELECT
    c.CITY_ID,
    d.DISTRICT_ID,
    sd.SUB_DISTRICT_ID,
    CAST(REPLACE(mp.business, ',', '') AS UNSIGNED) AS SHOP,
    CAST(REPLACE(mp.person, ',', '') AS UNSIGNED) AS MOVE_POP,
    CAST(REPLACE(REPLACE(mp.price, '만원', ''), ',', '') AS UNSIGNED) * 10000 AS SALES,
    CAST(REPLACE(REPLACE(mp.wrcppl, '명', ''), ',', '') AS UNSIGNED) AS WORK_POP,
    CAST(REPLACE(REPLACE(mp.earn, '만원', ''), ',', '') AS UNSIGNED) * 10000 AS INCOME,
    CAST(REPLACE(REPLACE(mp.cnsmp, '만원', ''), ',', '') AS UNSIGNED) * 10000 AS SPEND,
    CAST(REPLACE(mp.hhCnt, ',', '') AS UNSIGNED) AS HOUSE,
    CAST(REPLACE(REPLACE(mp.rsdppl, '명', ''), ',', '') AS UNSIGNED) AS RESIDENT,
    STR_TO_DATE(CONCAT(mp.yearmonth, '01'), '%Y%m%d') AS Y_M,
    NOW() AS CREATED_AT,
    NOW() AS UPDATED_AT
FROM
    test.movepopdata mp
JOIN
    semin.CITY c ON SUBSTRING_INDEX(SUBSTRING_INDEX(mp.keyword, ' ', 1), ' ', -1) = c.CITY_NAME
JOIN
    semin.DISTRICT d ON SUBSTRING_INDEX(SUBSTRING_INDEX(mp.keyword, ' ', 2), ' ', -1) = d.DISTRICT_NAME AND d.CITY_ID = c.CITY_ID
JOIN
    semin.SUB_DISTRICT sd ON SUBSTRING_INDEX(mp.keyword, ' ', -1) = sd.SUB_DISTRICT_NAME AND sd.DISTRICT_ID = d.DISTRICT_ID AND sd.CITY_ID = c.CITY_ID;
