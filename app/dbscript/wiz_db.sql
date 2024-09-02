-- 외래 키 제약 조건을 비활성화
SET
    FOREIGN_KEY_CHECKS = 0;

-- 테이블 삭제
DROP TABLE IF EXISTS `POPULATION`;

DROP TABLE IF EXISTS `GENDER`;

DROP TABLE IF EXISTS `LOC_INFO`;

DROP TABLE IF EXISTS `RISING_BUSINESS`;

DROP TABLE IF EXISTS `COMMERCIAL_DISTRICT`;

DROP TABLE IF EXISTS `BIZ_DETAIL_CATEGORY`;

DROP TABLE IF EXISTS `BIZ_SUB_CATEGORY`;

DROP TABLE IF EXISTS `BIZ_MAIN_CATEGORY`;

DROP TABLE IF EXISTS `SUB_DISTRICT`;

DROP TABLE IF EXISTS `DISTRICT`;

DROP TABLE IF EXISTS `CITY`;

DROP TABLE IF EXISTS `LOC_STORE`;

DROP TABLE IF EXISTS `CRIME`;

DROP TABLE IF EXISTS `CLASSIFICATION`;

-- 테이블 생성
CREATE TABLE
    `CITY` (
        `CITY_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_CID',
        `CITY_NAME` VARCHAR(50) NOT NULL COMMENT '시/도명',
        PRIMARY KEY (`CITY_ID`)
    );

CREATE TABLE
    `DISTRICT` (
        `DISTRICT_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_DID',
        `CITY_ID` INT NOT NULL COMMENT 'FK_CID',
        `DISTRICT_NAME` VARCHAR(50) NOT NULL COMMENT '시/군/구명',
        PRIMARY KEY (`DISTRICT_ID`),
        FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`)
    );

CREATE TABLE
    `SUB_DISTRICT` (
        `SUB_DISTRICT_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_SDID',
        `CITY_ID` INT NOT NULL COMMENT 'FK_CID',
        `DISTRICT_ID` INT NOT NULL COMMENT 'FK_DID',
        `SUB_DISTRICT_NAME` VARCHAR(50) NOT NULL COMMENT '읍/면/동 명',
        PRIMARY KEY (`SUB_DISTRICT_ID`),
        FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`),
        FOREIGN KEY (`DISTRICT_ID`) REFERENCES `DISTRICT` (`DISTRICT_ID`)
    );

CREATE TABLE
    `BIZ_MAIN_CATEGORY` (
        `BIZ_MAIN_CATEGORY_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_BMCID',
        `BIZ_MAIN_CATEGORY_NAME` VARCHAR(50) NOT NULL COMMENT '비즈맵 대분류명',
        PRIMARY KEY (`BIZ_MAIN_CATEGORY_ID`)
    );

CREATE TABLE
    `BIZ_SUB_CATEGORY` (
        `BIZ_SUB_CATEGORY_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_BSCID',
        `BIZ_MAIN_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BMCID',
        `BIZ_SUB_CATEGORY_NAME` VARCHAR(50) NOT NULL COMMENT '비즈맵 중분류명',
        PRIMARY KEY (`BIZ_SUB_CATEGORY_ID`),
        FOREIGN KEY (`BIZ_MAIN_CATEGORY_ID`) REFERENCES `BIZ_MAIN_CATEGORY` (`BIZ_MAIN_CATEGORY_ID`)
    );

CREATE TABLE
    `BIZ_DETAIL_CATEGORY` (
        `BIZ_DETAIL_CATEGORY_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_BDID',
        `BIZ_SUB_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BSCID',
        `BIZ_DETAIL_CATEGORY_NAME` VARCHAR(50) NOT NULL COMMENT '비즈맵 소분류명',
        PRIMARY KEY (`BIZ_DETAIL_CATEGORY_ID`),
        FOREIGN KEY (`BIZ_SUB_CATEGORY_ID`) REFERENCES `BIZ_SUB_CATEGORY` (`BIZ_SUB_CATEGORY_ID`)
    );

CREATE TABLE
    `COMMERCIAL_DISTRICT` (
        `COMMERCIAL_DISTRICT_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_CDID',
        `CITY_ID` INT NOT NULL COMMENT 'FK_CID',
        `DISTRICT_ID` INT NOT NULL COMMENT 'FK_DID',
        `SUB_DISTRICT_ID` INT NOT NULL COMMENT 'FK_SDID',
        `BIZ_MAIN_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BMCID',
        `BIZ_SUB_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BSCID',
        `BIZ_DETAIL_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BDID',
        `NATIONAL_DENSITY` DECIMAL(5, 2) NULL COMMENT '전국 밀집도',
        `CITY_DENSITY` DECIMAL(5, 2) NULL COMMENT '시/도 밀집도',
        `DISTRICT_DENSITY` DECIMAL(5, 2) NULL COMMENT '시/군/구 밀집도',
        `SUB_DISTRICT_DENSITY` DECIMAL(5, 2) NULL COMMENT '읍/면/동 밀집도',
        `MARKET_SIZE` INT NULL COMMENT '시장 규모',
        `AVERAGE_SALES` INT NULL COMMENT '평균 매출',
        `AVERAGE_PAYMENT` INT NULL COMMENT '결재단가',
        `USAGE_COUNT` INT NULL COMMENT '이용건수',
        `OPERATING_COST` INT NULL COMMENT '영업비용',
        `FOOD_COST` INT NULL COMMENT '식재료비',
        `EMPLOYEE_COST` INT NULL COMMENT '교용인 인건비',
        `RENTAL_COST` INT NULL COMMENT '임차료',
        `TAX_COST` INT NULL COMMENT '세금',
        `FAMILY_EMPLOYEE_COST` INT NULL COMMENT '가족 종사자 인건비',
        `CEO_COST` INT NULL COMMENT '대표자 인건비',
        `ETC_COST` INT NULL COMMENT '기타 비용',
        `AVERAGE_PROFIT` INT NULL COMMENT '영업이익',
        `AVG_PROFIT_PER_MON` DECIMAL(5, 2) NULL COMMENT '평균 월요일 매출 비중',
        `AVG_PROFIT_PER_TUE` DECIMAL(5, 2) NULL COMMENT '평균 화요일 매출 비중',
        `AVG_PROFIT_PER_WED` DECIMAL(5, 2) NULL COMMENT '평균 수요일 매출 비중',
        `AVG_PROFIT_PER_THU` DECIMAL(5, 2) NULL COMMENT '평균 목요일 매출 비중',
        `AVG_PROFIT_PER_FRI` DECIMAL(5, 2) NULL COMMENT '평균 금요일 매출 비중',
        `AVG_PROFIT_PER_SAT` DECIMAL(5, 2) NULL COMMENT '평균 토요일 매출 비중',
        `AVG_PROFIT_PER_SUN` DECIMAL(5, 2) NULL COMMENT '평균 일요일 매출 비중',
        `AVG_PROFIT_PER_06_09` DECIMAL(5, 2) NULL COMMENT '시간별 매출 비중06_09',
        `AVG_PROFIT_PER_09_12` DECIMAL(5, 2) NULL COMMENT '시간별 매출 비중09_12',
        `AVG_PROFIT_PER_12_15` DECIMAL(5, 2) NULL COMMENT '시간별 매출 비중12_15',
        `AVG_PROFIT_PER_15_18` DECIMAL(5, 2) NULL COMMENT '시간별 매출 비중15_18',
        `AVG_PROFIT_PER_18_21` DECIMAL(5, 2) NULL COMMENT '시간별 매출 비중18_21',
        `AVG_PROFIT_PER_21_24` DECIMAL(5, 2) NULL COMMENT '시간별 매출 비중21_24',
        `AVG_PROFIT_PER_24_06` DECIMAL(5, 2) NULL COMMENT '시간별 매출 비중24_06',
        `AVG_CLIENT_PER_M_20` DECIMAL(5, 2) NULL COMMENT '남 20대 비중',
        `AVG_CLIENT_PER_M_30` DECIMAL(5, 2) NULL COMMENT '남 30대 비중',
        `AVG_CLIENT_PER_M_40` DECIMAL(5, 2) NULL COMMENT '남 40대 비중',
        `AVG_CLIENT_PER_M_50` DECIMAL(5, 2) NULL COMMENT '남 50대 비중',
        `AVG_CLIENT_PER_M_60` DECIMAL(5, 2) NULL COMMENT '남 60대 비중',
        `AVG_CLIENT_PER_F_20` DECIMAL(5, 2) NULL COMMENT '여 20대 비중',
        `AVG_CLIENT_PER_F_30` DECIMAL(5, 2) NULL COMMENT '여 30대 비중',
        `AVG_CLIENT_PER_F_40` DECIMAL(5, 2) NULL COMMENT '여 40대 비중',
        `AVG_CLIENT_PER_F_50` DECIMAL(5, 2) NULL COMMENT '여 50대 비중',
        `AVG_CLIENT_PER_F_60` DECIMAL(5, 2) NULL COMMENT '여 60대 비중',
        `TOP_MENU_1` VARCHAR(50) NULL COMMENT '뜨는 메뉴 TOP1',
        `TOP_MENU_2` VARCHAR(50) NULL COMMENT '뜨는 메뉴 TOP2',
        `TOP_MENU_3` VARCHAR(50) NULL COMMENT '뜨는 메뉴 TOP3',
        `TOP_MENU_4` VARCHAR(50) NULL COMMENT '뜨는 메뉴 TOP4',
        `TOP_MENU_5` VARCHAR(50) NULL COMMENT '뜨는 메뉴 TOP5',
        `CREATED_AT` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
        `UPDATED_AT` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
        PRIMARY KEY (`COMMERCIAL_DISTRICT_ID`),
        FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`),
        FOREIGN KEY (`DISTRICT_ID`) REFERENCES `DISTRICT` (`DISTRICT_ID`),
        FOREIGN KEY (`SUB_DISTRICT_ID`) REFERENCES `SUB_DISTRICT` (`SUB_DISTRICT_ID`),
        FOREIGN KEY (`BIZ_MAIN_CATEGORY_ID`) REFERENCES `BIZ_MAIN_CATEGORY` (`BIZ_MAIN_CATEGORY_ID`),
        FOREIGN KEY (`BIZ_SUB_CATEGORY_ID`) REFERENCES `BIZ_SUB_CATEGORY` (`BIZ_SUB_CATEGORY_ID`),
        FOREIGN KEY (`BIZ_DETAIL_CATEGORY_ID`) REFERENCES `BIZ_DETAIL_CATEGORY` (`BIZ_DETAIL_CATEGORY_ID`)
    );


CREATE TABLE `LOC_INFO` (
	`LOC_INFO_ID`	int	NOT NULL    AUTO_INCREMENT	COMMENT 'PK_LIID',
	`CITY_ID`	INT	NOT NULL	COMMENT 'FK_CID',
	`DISTRICT_ID`	INT	NOT NULL	COMMENT 'FK_DID',
	`SUB_DISTRICT_ID`	INT	NOT NULL	COMMENT 'FK_SDID',
	`SHOP`	int	NULL	COMMENT '업소 갯수',
	`MOVE_POP`	int	NULL	COMMENT '유동인구',
	`SALES`	int	NULL	COMMENT '매출',
	`WORK_POP`	INT	NULL	COMMENT '직장인구',
	`INCOME`	INT	NULL	COMMENT '소득',
	`SPEND`	INT	NULL	COMMENT '소비',
	`HOUSE`	INT	NULL	COMMENT '세대수',
	`RESIDENT`	INT	NULL	COMMENT '주거인구',
	`CREATED_AT`	DATETIME	NULL	COMMENT '생성일시',
	`UPDATED_AT`	DATETIME	NULL	COMMENT '수정일시',
	`Y_M`	DATE	NULL	COMMENT '기준 년 월',
    PRIMARY KEY (`LOC_INFO_ID`),
    FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`),
    FOREIGN KEY (`DISTRICT_ID`) REFERENCES `DISTRICT` (`DISTRICT_ID`),
    FOREIGN KEY (`SUB_DISTRICT_ID`) REFERENCES `SUB_DISTRICT` (`SUB_DISTRICT_ID`)
);

CREATE TABLE
    `RISING_BUSINESS` (
        `RISING_BUSINESS_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_RBID',
        `CITY_ID` INT NOT NULL COMMENT 'FK_CID',
        `DISTRICT_ID` INT NOT NULL COMMENT 'FK_DID',
        `SUB_DISTRICT_ID` INT NOT NULL COMMENT 'FK_SDID',
        `BIZ_MAIN_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BMCID',
        `BIZ_SUB_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BSCID',
        `BIZ_DETAIL_CATEGORY_ID` INT NOT NULL COMMENT 'FK_BDID',
        `BUSINESS_NAME` VARCHAR(100) NOT NULL COMMENT '사업체명',
        `ADDRESS` VARCHAR(255) NULL COMMENT '주소',
        `PHONE` VARCHAR(20) NULL COMMENT '전화번호',
        `CREATED_AT` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
        `UPDATED_AT` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
        PRIMARY KEY (`RISING_BUSINESS_ID`),
        FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`),
        FOREIGN KEY (`DISTRICT_ID`) REFERENCES `DISTRICT` (`DISTRICT_ID`),
        FOREIGN KEY (`SUB_DISTRICT_ID`) REFERENCES `SUB_DISTRICT` (`SUB_DISTRICT_ID`),
        FOREIGN KEY (`BIZ_MAIN_CATEGORY_ID`) REFERENCES `BIZ_MAIN_CATEGORY` (`BIZ_MAIN_CATEGORY_ID`),
        FOREIGN KEY (`BIZ_SUB_CATEGORY_ID`) REFERENCES `BIZ_SUB_CATEGORY` (`BIZ_SUB_CATEGORY_ID`),
        FOREIGN KEY (`BIZ_DETAIL_CATEGORY_ID`) REFERENCES `BIZ_DETAIL_CATEGORY` (`BIZ_DETAIL_CATEGORY_ID`)
    );


CREATE TABLE `LOC_STORE` (
	`LOC_STORE_ID`	INT	NOT NULL    AUTO_INCREMENT	COMMENT 'PK_LCID',
	`CITY_ID`	INT	NOT NULL	COMMENT 'FK_CID',
	`DISTRICT_ID`	INT NULL	COMMENT 'FK_DID',
	`SUB_DISTRICT_ID`	INT NULL	COMMENT 'FK_SDID',
    `StoreBusinessNumber` VARCHAR(100) NULL COMMENT '상가업소번호',
	`store_name`	VARCHAR(255)	NULL	COMMENT '상호명',
	`branch_name`	VARCHAR(255)	NULL	COMMENT '지점명',
	`large_category_code`	VARCHAR(10)	NULL	COMMENT '상권업종대분류코드',
	`large_category_name`	VARCHAR(100)	NULL	COMMENT '상권업종대분류명',
	`medium_category_code`	VARCHAR(10)	NULL	COMMENT '상권업종중분류코드',
	`medium_category_name`	VARCHAR(100)	NULL	COMMENT '상권업종중분류명',
	`small_category_code`	VARCHAR(10)	NULL	COMMENT '상권업종소분류코드',
	`small_category_name`	VARCHAR(100)	NULL	COMMENT '상권업종소분류명',
	`industry_code`	VARCHAR(10)	NULL	COMMENT '표준산업분류코드',
	`industry_name`	VARCHAR(100)	NULL	COMMENT '표준산업분류명',
	`province_code`	VARCHAR(10)	NULL	COMMENT '시도코드',
	`province_name`	VARCHAR(100)	NULL	COMMENT '시도명',
	`district_code`	VARCHAR(10)	NULL	COMMENT '시군구코드',
	`district_name`	VARCHAR(100)	NULL	COMMENT '시군구명',
	`administrative_dong_code`	VARCHAR(20)	NULL	COMMENT '행정동코드',
	`administrative_dong_name`	VARCHAR(100)	NULL	COMMENT '행정동명',
	`legal_dong_code`	VARCHAR(20)	NULL	COMMENT '법정동코드',
	`legal_dong_name`	VARCHAR(100)	NULL	COMMENT '법정동명',
	`lot_number_code`	VARCHAR(30)	NULL	COMMENT '지번코드',
	`land_category_code`	VARCHAR(10)	NULL	COMMENT '대지구분코드',
	`land_category_name`	VARCHAR(100)	NULL	COMMENT '대지구분명',
	`lot_main_number`	VARCHAR(10)	NULL	COMMENT '지번본번지',
	`lot_sub_number`	VARCHAR(10)	NULL	COMMENT '지번부번지',
	`lot_address`	VARCHAR(255)	NULL	COMMENT '지번주소',
	`road_name_code`	VARCHAR(20)	NULL	COMMENT '도로명코드',
	`road_name`	VARCHAR(255)	NULL	COMMENT '도로명',
	`building_main_number`	VARCHAR(30)	NULL	COMMENT '건물본번지',
	`building_sub_number`	VARCHAR(30)	NULL	COMMENT '건물부번지',
	`building_management_number`	VARCHAR(100)	NULL	COMMENT '건물관리번호',
	`building_name`	VARCHAR(255)	NULL	COMMENT '건물명',
	`road_name_address`	VARCHAR(255)	NULL	COMMENT '도로명주소',
	`old_postal_code`	VARCHAR(10)	NULL	COMMENT '구우편번호',
	`new_postal_code`	VARCHAR(10)	NULL	COMMENT '신우편번호',
	`dong_info`	VARCHAR(100)	NULL	COMMENT '동정보',
	`floor_info`	VARCHAR(50)	NULL	COMMENT '층정보',
	`unit_info`	VARCHAR(50)	NULL	COMMENT '호정보',
	`longitude`	VARCHAR(30)	NULL	COMMENT '경도',
	`latitude`	VARCHAR(30)	NULL	COMMENT '위도',
	`Y_Q`	VARCHAR(30)	NULL	COMMENT '기준 년 분기',
	`CREATED_AT`	DATETIME	NULL	COMMENT '생성일자',
	`UPDATED_AT`	DATETIME	NULL	COMMENT '수정일자',
    PRIMARY KEY (`LOC_STORE_ID`),
    FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`),
    FOREIGN KEY (`DISTRICT_ID`) REFERENCES `DISTRICT` (`DISTRICT_ID`),
    FOREIGN KEY (`SUB_DISTRICT_ID`) REFERENCES `SUB_DISTRICT` (`SUB_DISTRICT_ID`)
);


CREATE TABLE gender (
    gender_id INT PRIMARY KEY,
    gender_name VARCHAR(10) NOT NULL
);


CREATE TABLE
    `POPULATION` (
        `POPULATION_ID` INT NOT NULL AUTO_INCREMENT COMMENT 'PK_PID',
        `CITY_ID` INT NOT NULL COMMENT 'FK_CID',
        `DISTRICT_ID` INT NOT NULL COMMENT 'FK_DID',
        `SUB_DISTRICT_ID` INT NOT NULL COMMENT 'FK_SDID',
        `GENDER_ID` INT NOT NULL COMMENT 'FK_GID',
        `admin_code` BIGINT NULL COMMENT '행정기관코드',
        `reference_date` DATE NULL COMMENT '기준연월',
        `province_name` VARCHAR(100) NULL COMMENT '시도명',
        `district_name` VARCHAR(100) NULL COMMENT '시군구명',
        `subdistrict_name` VARCHAR(100) NULL COMMENT '읍면동명',
        `total_population` integer NULL COMMENT '계',
        `male_population` integer NULL COMMENT '남자',
        `female_population` integer NULL COMMENT '여자',
        `age_0` integer NULL COMMENT '만0세',
        `age_1` integer NULL COMMENT '만1세',
        `age_2` integer NULL COMMENT '만2세',
        `age_3` integer NULL COMMENT '만3세',
        `age_4` integer NULL COMMENT '만4세',
        `age_5` integer NULL COMMENT '만5세',
        `age_6` integer NULL COMMENT '만6세',
        `age_7` integer NULL COMMENT '만7세',
        `age_8` integer NULL COMMENT '만8세',
        `age_9` integer NULL COMMENT '만9세',
        `age_10` integer NULL COMMENT '만10세',
        `age_11` integer NULL COMMENT '만11세',
        `age_12` integer NULL COMMENT '만12세',
        `age_13` integer NULL COMMENT '만13세',
        `age_14` integer NULL COMMENT '만14세',
        `age_15` integer NULL COMMENT '만15세',
        `age_16` integer NULL COMMENT '만16세',
        `age_17` integer NULL COMMENT '만17세',
        `age_18` integer NULL COMMENT '만18세',
        `age_19` integer NULL COMMENT '만19세',
        `age_20` integer NULL COMMENT '만20세',
        `age_21` integer NULL COMMENT '만21세',
        `age_22` integer NULL COMMENT '만22세',
        `age_23` integer NULL COMMENT '만23세',
        `age_24` integer NULL COMMENT '만24세',
        `age_25` integer NULL COMMENT '만25세',
        `age_26` integer NULL COMMENT '만26세',
        `age_27` integer NULL COMMENT '만27세',
        `age_28` integer NULL COMMENT '만28세',
        `age_29` integer NULL COMMENT '만29세',
        `age_30` integer NULL COMMENT '만30세',
        `age_31` integer NULL COMMENT '만31세',
        `age_32` integer NULL COMMENT '만32세',
        `age_33` integer NULL COMMENT '만33세',
        `age_34` integer NULL COMMENT '만34세',
        `age_35` integer NULL COMMENT '만35세',
        `age_36` integer NULL COMMENT '만36세',
        `age_37` integer NULL COMMENT '만37세',
        `age_38` integer NULL COMMENT '만38세',
        `age_39` integer NULL COMMENT '만39세',
        `age_40` integer NULL COMMENT '만40세',
        `age_41` integer NULL COMMENT '만41세',
        `age_42` integer NULL COMMENT '만42세',
        `age_43` integer NULL COMMENT '만43세',
        `age_44` integer NULL COMMENT '만44세',
        `age_45` integer NULL COMMENT '만45세',
        `age_46` integer NULL COMMENT '만46세',
        `age_47` integer NULL COMMENT '만47세',
        `age_48` integer NULL COMMENT '만48세',
        `age_49` integer NULL COMMENT '만49세',
        `age_50` integer NULL COMMENT '만50세',
        `age_51` integer NULL COMMENT '만51세',
        `age_52` integer NULL COMMENT '만52세',
        `age_53` integer NULL COMMENT '만53세',
        `age_54` integer NULL COMMENT '만54세',
        `age_55` integer NULL COMMENT '만55세',
        `age_56` integer NULL COMMENT '만56세',
        `age_57` integer NULL COMMENT '만57세',
        `age_58` integer NULL COMMENT '만58세',
        `age_59` integer NULL COMMENT '만59세',
        `age_60` integer NULL COMMENT '만60세',
        `age_61` integer NULL COMMENT '만61세',
        `age_62` integer NULL COMMENT '만62세',
        `age_63` integer NULL COMMENT '만63세',
        `age_64` integer NULL COMMENT '만64세',
        `age_65` integer NULL COMMENT '만65세',
        `age_66` integer NULL COMMENT '만66세',
        `age_67` integer NULL COMMENT '만67세',
        `age_68` integer NULL COMMENT '만68세',
        `age_69` integer NULL COMMENT '만69세',
        `age_70` integer NULL COMMENT '만70세',
        `age_71` integer NULL COMMENT '만71세',
        `age_72` integer NULL COMMENT '만72세',
        `age_73` integer NULL COMMENT '만73세',
        `age_74` integer NULL COMMENT '만74세',
        `age_75` integer NULL COMMENT '만75세',
        `age_76` integer NULL COMMENT '만76세',
        `age_77` integer NULL COMMENT '만77세',
        `age_78` integer NULL COMMENT '만78세',
        `age_79` integer NULL COMMENT '만79세',
        `age_80` integer NULL COMMENT '만80세',
        `age_81` integer NULL COMMENT '만81세',
        `age_82` integer NULL COMMENT '만82세',
        `age_83` integer NULL COMMENT '만83세',
        `age_84` integer NULL COMMENT '만84세',
        `age_85` integer NULL COMMENT '만85세',
        `age_86` integer NULL COMMENT '만86세',
        `age_87` integer NULL COMMENT '만87세',
        `age_88` integer NULL COMMENT '만88세',
        `age_89` integer NULL COMMENT '만89세',
        `age_90` integer NULL COMMENT '만90세',
        `age_91` integer NULL COMMENT '만91세',
        `age_92` integer NULL COMMENT '만92세',
        `age_93` integer NULL COMMENT '만93세',
        `age_94` integer NULL COMMENT '만94세',
        `age_95` integer NULL COMMENT '만95세',
        `age_96` integer NULL COMMENT '만96세',
        `age_97` integer NULL COMMENT '만97세',
        `age_98` integer NULL COMMENT '만98세',
        `age_99` integer NULL COMMENT '만99세',
        `age_100` integer NULL COMMENT '만100세',
        `age_101` integer NULL COMMENT '만101세',
        `age_102` integer NULL COMMENT '만102세',
        `age_103` integer NULL COMMENT '만103세',
        `age_104` integer NULL COMMENT '만104세',
        `age_105` integer NULL COMMENT '만105세',
        `age_106` integer NULL COMMENT '만106세',
        `age_107` integer NULL COMMENT '만107세',
        `age_108` integer NULL COMMENT '만108세',
        `age_109` integer NULL COMMENT '만109세',
        `age_110_over` integer NULL COMMENT '만110세이상',
        `CREATED_AT` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
        `UPDATED_AT` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
        PRIMARY KEY (`population_id`),
        FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`),
        FOREIGN KEY (`DISTRICT_ID`) REFERENCES `DISTRICT` (`DISTRICT_ID`),
        FOREIGN KEY (`SUB_DISTRICT_ID`) REFERENCES `SUB_DISTRICT` (`SUB_DISTRICT_ID`),
        FOREIGN KEY (`GENDER_ID`) REFERENCES `GENDER` (`GENDER_ID`)
    );



CREATE TABLE CRIME (
    CRIME_ID INT AUTO_INCREMENT PRIMARY KEY COMMENT '범죄 ID',
    CITY_ID INT NOT NULL COMMENT '시/도 ID',
    QUARTER VARCHAR(10) NOT NULL COMMENT '해당 분기',
    CRIME_MAJOR_CATEGORY VARCHAR(50) NOT NULL COMMENT '범죄의 대분류',
    CRIME_MINOR_CATEGORY VARCHAR(50) NOT NULL COMMENT '범죄의 소분류',
    INCIDENT_COUNT INT NOT NULL COMMENT '발생한 사건의 건수',
    ARREST_COUNT INT NOT NULL COMMENT '검거된 사건의 건수',
    INCIDENT_TO_ARREST_RATIO DECIMAL(5,2) NOT NULL COMMENT '발생 건수 대비 검거 건수의 비율',
    ARREST_PERSONNEL INT NOT NULL COMMENT '검거에 관여한 인원 수',
    LEGAL_ENTITY INT NOT NULL COMMENT '관련된 법인체의 수',
    FOREIGN KEY (`CITY_ID`) REFERENCES `CITY` (`CITY_ID`)
);


CREATE TABLE CLASSIFICATION (
    CLASSIFICATION_ID INT AUTO_INCREMENT PRIMARY KEY,
    MAIN_CATEGORY_CODE CHAR(1),
    MAIN_CATEGORY_NAME VARCHAR(100),
    SUB_CATEGORY_CODE CHAR(2),
    SUB_CATEGORY_NAME VARCHAR(100),
    DETAIL_CATEGORY_CODE CHAR(3),
    DETAIL_CATEGORY_NAME VARCHAR(100),
    SUB_DETAIL_CATEGORY_CODE CHAR(4),
    SUB_DETAIL_CATEGORY_NAME VARCHAR(100),
    SUB_SUB_DETAIL_CATEGORY_CODE CHAR(5),
    SUB_SUB_DETAIL_CATEGORY_NAME VARCHAR(100)
);

-- 외래 키 제약 조건을 다시 활성화
SET
    FOREIGN_KEY_CHECKS = 1;

INSERT INTO gender (gender_id, gender_name)
VALUES (1, '남자'), 
       (2, '여자');


