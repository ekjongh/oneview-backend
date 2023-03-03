/* ============================================================================================================
 * 원뷰 데이터 업데이트 현황을 조회하는 프로시저
 * [ 파라미터 ]
 * - 기준일자 : 예) 20230216
 *
 * [ 업데이트 확인방식 ]
 *  1) 테이블을 드랍하고 데이터를 삽입해 준 경우 : 스키마정보 확인(information_schema.tables)
 *  2) 데이터를 삭제하하고 갱신된 데이터를 삽입해 준 경우 : 각각의 테이블의 타임스템프 컬럼 확인(ETL_DT)
 * ------------------------------------------------------------------------------------------------------------
 * 2023.02.16 초기버전 작성
 * ==========================================================================================================*/
DROP PROCEDURE IF EXISTS usp_get_updated_tables;

DELIMITER //
CREATE PROCEDURE usp_get_updated_tables(IN base_date VARCHAR(10))
BEGIN

    /* 임시 테이블을 생성한다. */
    DROP TABLE IF EXISTS UPDATED_TABLES;
    CREATE TEMPORARY TABLE UPDATED_TABLES (
        UPDATE_TYPE VARCHAR(10),
        TBL_NAME VARCHAR(64),
        UPDATED_DT DATETIME
    );

    /* 1) 테이블을 드랍하고 데이터를 삽입한 경우 데이터 업데이트 현황 조회 */
    INSERT INTO UPDATED_TABLES
    SELECT 'table', table_name, create_time
        FROM information_schema.tables
        WHERE table_schema = 'ONEVIEW' AND
        DATE_FORMAT(create_time, '%Y%m%d') = base_date;

    /* ------------------------------------------------------------------------------------------------------------
     * 2) 데이터를 삭제하고 데이터를 상입한 경우
     * ------------------------------------------------------------------------------------------------------------*/

    /* 2-1) 오프로딩율_월별추이용 데이터 업데이트를 확인한다. */
    INSERT INTO UPDATED_TABLES
    SELECT 'data', 'SUM_5G_OFF_LOAD_RATE_MM', max(ETL_DT)
    FROM SUM_5G_OFF_LOAD_RATE_MM WHERE base_ym = SUBSTRING(base_date,1,6);

    /* 2-2) RRC_월별추이 데이터 업데이트를 확인한다. */
    INSERT INTO UPDATED_TABLES
    SELECT 'data', 'SUM_LTE_PRBUSAGE_MM', max(ETL_DT)
    FROM SUM_LTE_PRBUSAGE_MM WHERE base_ym = SUBSTRING(base_date,1,6);

    /* 2-3) MDT인빌딩_VOC상세분석용 데이터 업데이트를 확인한다. */
    INSERT INTO UPDATED_TABLES
    SELECT 'data', 'SUM_MDT_INBLDG_DD', max(ETL_DT)
    FROM SUM_MDT_INBLDG_DD WHERE base_date = base_date;

    /* 2-4) 가입자수_월별추이 데이터 업데이트를 확인한다. */
    INSERT INTO UPDATED_TABLES
    SELECT 'data', 'SUM_SBSTR_CNT_MM', max(ETL_DT)
    FROM SUM_SBSTR_CNT_MM WHERE base_ym = SUBSTRING(base_date,1,6);

    /* 2-5) VOC_월별추이 데이터 업데이트를 확인한다. */
    INSERT INTO UPDATED_TABLES
    SELECT 'data', 'SUM_VOC_TXN_MM', max(ETL_DT)
    FROM SUM_VOC_TXN_MM WHERE base_ym = SUBSTRING(base_date,1,6);

    /* 2-6) VOC_월별추이 데이터 업데이트를 확인한다. */
    INSERT INTO UPDATED_TABLES
    SELECT 'data', 'SUM_VOLTE_FAIL_RATE_MM', max(ETL_DT)
    FROM SUM_VOLTE_FAIL_RATE_MM WHERE base_ym = SUBSTRING(base_date,1,6);


    /* 데이터 업데이트 현황을 반환한다. */
    SELECT B.SVC_NAME, A.UPDATED_DT, A.TBL_NAME
    FROM UPDATED_TABLES AS A, CODE_SVCS_MAP B
    WHERE (A.TBL_NAME = B.TBL_NAME) AND
        DATE_FORMAT(UPDATED_DT, '%Y%m%d') = base_date;

    /* 임시 테이블을 삭제한다. */
    DROP TEMPORARY TABLE UPDATED_TABLES;

END//

DELIMITER ;

call usp_get_updated_tables('20230216');