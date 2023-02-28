CREATE TABLE blacklists (
  created_at datetime DEFAULT NULL,
  updated_at datetime DEFAULT NULL,
  id varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  token varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  owner_id varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (id),
  KEY owner_id (owner_id),
  CONSTRAINT blacklists_ibfk_1 FOREIGN KEY (owner_id) REFERENCES users (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE users (
  created_at datetime DEFAULT NULL,
  updated_at datetime DEFAULT NULL,
  user_id varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  user_name varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  email varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  phone varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  group_1 varchar(1000) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  group_2 varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  group_3 varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  group_4 varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  board_modules varchar(5000) DEFAULT NULL,
  is_active tinyint(1) DEFAULT NULL,
  is_superuser tinyint(1) DEFAULT NULL,
  level varchar(50) DEFAULT NULL,
  auth varchar(30) DEFAULT NULL,
  board_id int(11) DEFAULT NULL,
  start_board_id int(11) DEFAULT NULL,
  PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE CODE_ADDR (
  SIDO_NM varchar(20) DEFAULT NULL,
  SIDO_CD varchar(30) DEFAULT NULL,
  GUN_GU_NM varchar(50) DEFAULT NULL,
  GUN_GU_CD varchar(20) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_CD varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE CODE_HOUR (
  hh varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE CODE_MENU (
  MENU1 varchar(100) DEFAULT NULL,
  MENU2 varchar(100) DEFAULT NULL,
  MENU3 varchar(200) DEFAULT NULL,
  MENU4 varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE CODE_ORG (
  SEQ_NO int(11) NOT NULL AUTO_INCREMENT,
  BIZ_HQ_NM varchar(30) DEFAULT NULL,
  OPER_TEAM_NM varchar(30) DEFAULT NULL,
  AREA_CENTER_NM varchar(30) DEFAULT NULL,
  AREA_TEAM_NM varchar(30) DEFAULT NULL,
  AREA_JO_NM varchar(30) DEFAULT NULL,
  bonbu_nm varchar(50) DEFAULT NULL,
  eng_sosok tinyint(1) DEFAULT NULL,
  PRIMARY KEY (SEQ_NO)
) ENGINE=InnoDB AUTO_INCREMENT=1155 DEFAULT CHARSET=utf8
;

CREATE TABLE DASHBOARD_CONFIG (
  Created_at datetime DEFAULT NULL,
  Updated_at datetime DEFAULT NULL,
  board_id int(11) NOT NULL AUTO_INCREMENT,
  owner_id varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  name varchar(100) DEFAULT NULL,
  board_module varchar(5000) DEFAULT NULL,
  update_yn tinyint(1) DEFAULT NULL,
  login_config tinyint(1) DEFAULT NULL,
  PRIMARY KEY (board_id),
  KEY owner_id (owner_id),
  CONSTRAINT DASHBOARD_CONFIG_ibfk_1 FOREIGN KEY (owner_id) REFERENCES users (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=573 DEFAULT CHARSET=utf8
;

CREATE TABLE ORG_GROUP (
  EX_ORG_CD varchar(20) DEFAULT NULL,
  NAME varchar(100) DEFAULT NULL,
  EX_COMPANY_CD varchar(4) DEFAULT NULL,
  EX_COMPANY_NM varchar(40) DEFAULT NULL,
  STATUS varchar(1) DEFAULT NULL,
  PARENT_ID varchar(20) DEFAULT NULL,
  EX_DEPT_CAP_NUM varchar(10) DEFAULT NULL,
  EX_ORG_LEVEL varchar(10) DEFAULT NULL,
  EX_ORG_ORDER varchar(10) DEFAULT NULL,
  REPL_DT date DEFAULT NULL,
  BATCH_FLAG varchar(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE ORG_USER (
  LOGIN_ID varchar(10) DEFAULT NULL,
  NAME varchar(128) DEFAULT NULL,
  STATUS varchar(1) DEFAULT NULL,
  EX_LEVEL_CD varchar(3) DEFAULT NULL,
  EX_LEVEL_NM varchar(40) DEFAULT NULL,
  EX_TITLE_CD varchar(3) DEFAULT NULL,
  EX_TITLE_NM varchar(40) DEFAULT NULL,
  EX_DEPT_CD varchar(20) DEFAULT NULL,
  EX_DEPT_NM varchar(100) DEFAULT NULL,
  EX_BONBU_CD varchar(6) DEFAULT NULL,
  EX_BONBU_NM varchar(100) DEFAULT NULL,
  EX_AGENCY_CD varchar(10) DEFAULT NULL,
  EX_AGENCY_NM varchar(100) DEFAULT NULL,
  EX_COMPANY_CD varchar(10) DEFAULT NULL,
  EX_COMPANY_NM varchar(40) DEFAULT NULL,
  EX_POSITION_CD varchar(50) DEFAULT NULL,
  EX_POSITION_NM varchar(255) DEFAULT NULL,
  EX_MANAGER_NO varchar(10) DEFAULT NULL,
  EMAIL varchar(50) DEFAULT NULL,
  MOBILE varchar(30) DEFAULT NULL,
  REPL_DT date DEFAULT NULL,
  BATCH_FLAG varchar(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_5G_OFF_LOAD_RATE_BTS (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  G3D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  LD_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G3D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G5D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTDL bigint(20) DEFAULT NULL,
  G5D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  LD_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTUL bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_5G_OFF_LOAD_RATE_HNDSET (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  HNDSET_PET_NM varchar(50) DEFAULT NULL,
  SA_5G_SUPRT_DIV_NM varchar(50) DEFAULT NULL,
  G3D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G3D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  LD_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  LD_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTDL bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTUL bigint(20) DEFAULT NULL,
  G5D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G5D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  KEY idx_off_hndset_date (BASE_DATE),
  KEY idx_off_hndset_team (OPER_TEAM_NM),
  KEY idx_off_hndset_hndset (HNDSET_PET_NM)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_5G_OFF_LOAD_RATE_MM (
  BASE_YM int(11) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  G3D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  LD_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G3D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G5D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTDL bigint(20) DEFAULT NULL,
  G5D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  LD_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTUL bigint(20) DEFAULT NULL,
  ETL_DT timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_5G_OFF_LOAD_RATE (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  G3D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  LD_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G3D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G5D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTDL bigint(20) DEFAULT NULL,
  G5D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  LD_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTUL bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_DAT_CNT (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  G3D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  LD_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G3D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  G5D_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTDL bigint(20) DEFAULT NULL,
  G5D_DOWNL_DATA_QNT bigint(20) DEFAULT NULL,
  LD_UPLD_DATA_QNT bigint(20) DEFAULT NULL,
  SRU_USAGECOUNTUL bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_LTE_PRBUSAGE_DD (
  BASE_DATE int(11) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  PRB_AVG decimal(15,4) DEFAULT NULL,
  RRC_ATT_SUM decimal(15,4) DEFAULT NULL,
  RRC_SUCES_SUM bigint(20) DEFAULT NULL,
  RRC_SUCES_RATE_AVG decimal(15,4) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  KEY idx_rrc_date (BASE_DATE),
  KEY idx_rrc_team (OPER_TEAM_NM),
  KEY idx_rrc_hq (BIZ_HQ_NM),
  KEY idx_rrc_jo (AREA_JO_NM)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_LTE_PRBUSAGE_MM (
  BASE_YM int(11) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  PRB_AVG decimal(15,4) DEFAULT NULL,
  RRC_ATT_SUM decimal(15,4) DEFAULT NULL,
  RRC_SUCES_SUM bigint(20) DEFAULT NULL,
  RRC_SUCES_RATE_AVG decimal(15,4) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  PRB_SUM double DEFAULT NULL,
  CQI_AVG double DEFAULT NULL,
  CQI_SUM double DEFAULT NULL,
  CQI_EDGE_AVG double DEFAULT NULL,
  CQI_EDGE_SUM double DEFAULT NULL,
  ACTIVE_UE_AVG double DEFAULT NULL,
  ACTIVE_UE_SUM double DEFAULT NULL,
  PRB_MAX double DEFAULT NULL,
  ACTIVE_UE_MAX double DEFAULT NULL,
  ETL_DT timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_LTE_PRBUSAGE_TMP (
  base_date int(11) DEFAULT NULL,
  mkng_cmpn_nm varchar(50) DEFAULT NULL,
  biz_hq_nm varchar(50) DEFAULT NULL,
  oper_team_nm varchar(50) DEFAULT NULL,
  sido_nm varchar(100) DEFAULT NULL,
  gun_gu_nm varchar(100) DEFAULT NULL,
  eup_myun_dong_nm varchar(100) DEFAULT NULL,
  area_hq_nm varchar(50) DEFAULT NULL,
  area_center_nm varchar(50) DEFAULT NULL,
  area_jo_nm varchar(50) DEFAULT NULL,
  sum_prb_avg decimal(37,4) DEFAULT NULL,
  cnt_prb_avg bigint(21) NOT NULL DEFAULT '0',
  rrc_att_sum decimal(37,4) DEFAULT NULL,
  rrc_suces_sum decimal(41,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_MDT_BAD_RATE (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  BTS_MAKER_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  RSRP_M105D_CNT bigint(20) DEFAULT NULL,
  RSRP_M110D_CNT bigint(20) DEFAULT NULL,
  RSRP_CNT bigint(20) DEFAULT NULL,
  RSRP_SUM bigint(20) DEFAULT NULL,
  RSRQ_M15D_CNT bigint(20) DEFAULT NULL,
  RSRQ_M17D_CNT bigint(20) DEFAULT NULL,
  RSRQ_CNT bigint(20) DEFAULT NULL,
  RSRQ_SUM bigint(20) DEFAULT NULL,
  NEW_RIP_MAXD_CNT bigint(20) DEFAULT NULL,
  RIP_CNT bigint(20) DEFAULT NULL,
  RIP_SUM bigint(20) DEFAULT NULL,
  NEW_PHR_M3D_CNT bigint(20) DEFAULT NULL,
  NEW_PHR_MIND_CNT bigint(20) DEFAULT NULL,
  PHR_CNT bigint(20) DEFAULT NULL,
  PHR_SUM bigint(20) DEFAULT NULL,
  NR_RSRP_CNT bigint(20) DEFAULT NULL,
  NR_RSRP_SUM bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  KEY idx_mdt_date (BASE_DATE),
  KEY idx_mdt_jo (AREA_JO_NM),
  KEY dx_mdt_team (OPER_TEAM_NM),
  KEY dx_mdt_hq (BIZ_HQ_NM)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_MDT_INBLDG_DD (
  BASE_DATE int(11) DEFAULT NULL,
  SVC_CONT_ID varchar(20) DEFAULT NULL,
  BLD_ID varchar(30) DEFAULT NULL,
  TR_BLD_NAME_DONG varchar(50) DEFAULT NULL,
  ADR_UTMKX varchar(50) DEFAULT NULL,
  ADR_UTMKY varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  ADR_BLDG_TYPE_DESC varchar(30) DEFAULT NULL,
  ADDR_DIV varchar(30) DEFAULT NULL,
  ADDR_DIV_NM varchar(30) DEFAULT NULL,
  BLD_FLR varchar(10) DEFAULT NULL,
  BLD_FLR_DESC varchar(10) DEFAULT NULL,
  BLDG_ADDR varchar(200) DEFAULT NULL,
  BLDG_RSCP_CNT bigint(20) DEFAULT NULL,
  BLDG_RSCP_SUM bigint(20) DEFAULT NULL,
  BLDG_RSCP_0_M100D_CNT bigint(20) DEFAULT NULL,
  BLDG_RSCP_0_M105D_CNT bigint(20) DEFAULT NULL,
  BLDG_RSRP_M105D_CNT bigint(20) DEFAULT NULL,
  BLDG_RSRP_M110D_CNT bigint(20) DEFAULT NULL,
  BLDG_RSRP_CNT bigint(20) DEFAULT NULL,
  BLDG_RSRP_SUM bigint(20) DEFAULT NULL,
  BLDG_NSINR_CNT bigint(20) DEFAULT NULL,
  BLDG_NSINR_SUM double DEFAULT NULL,
  BLDG_NEW_PHR_MIND_CNT bigint(20) DEFAULT NULL,
  BLDG_NEW_PHR_M3D_CNT bigint(20) DEFAULT NULL,
  BLDG_PHR_CNT bigint(20) DEFAULT NULL,
  BLDG_PHR_SUM double DEFAULT NULL,
  BLDG_NEW_RIP_MAXD_CNT bigint(20) DEFAULT NULL,
  BLDG_RIP_CNT bigint(20) DEFAULT NULL,
  BLDG_RIP_SUM bigint(20) DEFAULT NULL,
  BLDG_NR_RSRP_CNT bigint(20) DEFAULT NULL,
  BLDG_NR_RSRP_SUM double DEFAULT NULL,
  ETL_DT timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_SBSTR_CNT_MM (
  BASE_YM int(11) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  BPROD_MAINT_SBSCR_CASCNT bigint(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  ETL_DT timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_SBSTR_CNT (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  HNDSET_PET_NM varchar(50) DEFAULT NULL,
  SA_5G_SUPRT_DIV_NM varchar(50) DEFAULT NULL,
  BPROD_MAINT_SBSCR_CASCNT bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOC_DTL_TXN (
  BASE_DATE int(11) DEFAULT NULL,
  SVC_CONT_ID varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  LATIT_VAL varchar(50) DEFAULT NULL,
  LNGIT_VAL varchar(50) DEFAULT NULL,
  CELL_CD varchar(50) DEFAULT NULL,
  S1AP_CNT bigint(20) DEFAULT NULL,
  S1AP_FAIL_CNT bigint(20) DEFAULT NULL,
  RSRP_M105D_CNT bigint(20) DEFAULT NULL,
  RSRP_M110D_CNT bigint(20) DEFAULT NULL,
  RSRP_CNT bigint(20) DEFAULT NULL,
  RSRP_SUM bigint(20) DEFAULT NULL,
  RSRQ_M15D_CNT bigint(20) DEFAULT NULL,
  RSRQ_M17D_CNT bigint(20) DEFAULT NULL,
  RSRQ_CNT bigint(20) DEFAULT NULL,
  RSRQ_SUM bigint(20) DEFAULT NULL,
  NEW_RIP_MAXD_CNT bigint(20) DEFAULT NULL,
  RIP_CNT bigint(20) DEFAULT NULL,
  RIP_SUM bigint(20) DEFAULT NULL,
  NEW_PHR_M3D_CNT bigint(20) DEFAULT NULL,
  NEW_PHR_MIND_CNT bigint(20) DEFAULT NULL,
  PHR_CNT bigint(20) DEFAULT NULL,
  PHR_SUM bigint(20) DEFAULT NULL,
  NR_RSRP_CNT bigint(20) DEFAULT NULL,
  NR_RSRP_SUM bigint(20) DEFAULT NULL,
  VOLTE_TRY_CACNT bigint(20) DEFAULT NULL,
  VOLTE_COMP_CACNT bigint(20) DEFAULT NULL,
  VOLTE_SELF_FAIL_CACNT bigint(20) DEFAULT NULL,
  VOLTE_OTHER_FAIL_CACNT bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  KEY idx_volc_dtl_svcid (SVC_CONT_ID),
  KEY idx_voc_dtl_date_svcid (BASE_DATE,SVC_CONT_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOC_TXN_MM (
  BASE_YM int(11) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  BPROD_NM varchar(50) DEFAULT NULL,
  HNDSET_PET_NM varchar(50) DEFAULT NULL,
  SA_5G_SUPRT_DIV_NM varchar(50) DEFAULT NULL,
  VOC_TYPE_NM varchar(20) DEFAULT NULL,
  VOC_WJT_PRMR_NM varchar(50) DEFAULT NULL,
  VOC_WJT_SCND_NM varchar(50) DEFAULT NULL,
  VOC_WJT_TERT_NM varchar(50) DEFAULT NULL,
  VOC_WJT_QRTC_NM varchar(50) DEFAULT NULL,
  SR_TT_RCP_NO bigint(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  ETL_DT timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOC_TXN_RT_TMP (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  LATIT_VAL varchar(50) DEFAULT NULL,
  LNGIT_VAL varchar(50) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  BPROD_NM varchar(50) DEFAULT NULL,
  HNDSET_PET_NM varchar(50) DEFAULT NULL,
  SA_5G_SUPRT_DIV_NM varchar(50) DEFAULT NULL,
  VOC_TYPE_NM varchar(20) DEFAULT NULL,
  VOC_WJT_PRMR_NM varchar(50) DEFAULT NULL,
  VOC_WJT_SCND_NM varchar(50) DEFAULT NULL,
  VOC_WJT_TERT_NM varchar(50) DEFAULT NULL,
  VOC_WJT_QRTC_NM varchar(50) DEFAULT NULL,
  SR_TT_RCP_NO varchar(30) DEFAULT NULL,
  SVC_CONT_ID varchar(20) DEFAULT NULL,
  TROBL_RGN_BROAD_SIDO_NM varchar(100) DEFAULT NULL,
  TROBL_RGN_SGG_NM varchar(100) DEFAULT NULL,
  TROBL_RGN_EUP_MYUN_DONG_LI_NM varchar(100) DEFAULT NULL,
  TROBL_RGN_DTL_SBST varchar(200) DEFAULT NULL,
  UTMKX varchar(50) DEFAULT NULL,
  UTMKY varchar(50) DEFAULT NULL,
  DAY_UTMKX varchar(50) DEFAULT NULL,
  DAY_UTMKY varchar(50) DEFAULT NULL,
  NGT_UTMKX varchar(50) DEFAULT NULL,
  NGT_UTMKY varchar(50) DEFAULT NULL,
  VOC_RCP_TXN longtext,
  TT_TRT_SBST longtext,
  VOC_ACTN_TXN longtext,
  SR_TT_RCP_NO_CNT bigint(20) DEFAULT NULL,
  EQUIP_CD_DATA varchar(50) DEFAULT NULL,
  EQUIP_NM_DATA varchar(200) DEFAULT NULL,
  LATIT_VAL_DATA varchar(50) DEFAULT NULL,
  LNGIT_VAL_DATA varchar(50) DEFAULT NULL,
  TECH_TT_TRT_STTUS_NM varchar(100) DEFAULT NULL,
  INTMD_TRT_METH_NM varchar(100) DEFAULT NULL,
  INTMD_TRT_METH_DTL_NM varchar(100) DEFAULT NULL,
  CMPLT_TRT_METH_NM varchar(100) DEFAULT NULL,
  CMPLT_TRT_METH_DTL_NM varchar(100) DEFAULT NULL,
  VOC_TRT_CMPLT_DATE varchar(100) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOC_TXN (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  LATIT_VAL varchar(50) DEFAULT NULL,
  LNGIT_VAL varchar(50) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  BPROD_NM varchar(50) DEFAULT NULL,
  HNDSET_PET_NM varchar(50) DEFAULT NULL,
  SA_5G_SUPRT_DIV_NM varchar(50) DEFAULT NULL,
  VOC_TYPE_NM varchar(20) DEFAULT NULL,
  VOC_WJT_PRMR_NM varchar(50) DEFAULT NULL,
  VOC_WJT_SCND_NM varchar(50) DEFAULT NULL,
  VOC_WJT_TERT_NM varchar(50) DEFAULT NULL,
  VOC_WJT_QRTC_NM varchar(50) DEFAULT NULL,
  SR_TT_RCP_NO varchar(30) DEFAULT NULL,
  SVC_CONT_ID varchar(20) DEFAULT NULL,
  TROBL_RGN_BROAD_SIDO_NM varchar(100) DEFAULT NULL,
  TROBL_RGN_SGG_NM varchar(100) DEFAULT NULL,
  TROBL_RGN_EUP_MYUN_DONG_LI_NM varchar(100) DEFAULT NULL,
  TROBL_RGN_DTL_SBST varchar(200) DEFAULT NULL,
  UTMKX varchar(50) DEFAULT NULL,
  UTMKY varchar(50) DEFAULT NULL,
  DAY_UTMKX varchar(50) DEFAULT NULL,
  DAY_UTMKY varchar(50) DEFAULT NULL,
  NGT_UTMKX varchar(50) DEFAULT NULL,
  NGT_UTMKY varchar(50) DEFAULT NULL,
  VOC_RCP_TXN longtext,
  TT_TRT_SBST longtext,
  VOC_ACTN_TXN longtext,
  SR_TT_RCP_NO_CNT bigint(20) DEFAULT NULL,
  EQUIP_CD_DATA varchar(50) DEFAULT NULL,
  EQUIP_NM_DATA varchar(200) DEFAULT NULL,
  LATIT_VAL_DATA varchar(50) DEFAULT NULL,
  LNGIT_VAL_DATA varchar(50) DEFAULT NULL,
  TECH_TT_TRT_STTUS_NM varchar(100) DEFAULT NULL,
  INTMD_TRT_METH_NM varchar(100) DEFAULT NULL,
  INTMD_TRT_METH_DTL_NM varchar(100) DEFAULT NULL,
  CMPLT_TRT_METH_NM varchar(100) DEFAULT NULL,
  CMPLT_TRT_METH_DTL_NM varchar(100) DEFAULT NULL,
  VOC_TRT_CMPLT_DATE varchar(100) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOLTE_FAIL_RATE_BTS (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  EQUIP_CD varchar(50) DEFAULT NULL,
  EQUIP_NM varchar(200) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  TRY_CACNT bigint(20) DEFAULT NULL,
  COMP_CACNT bigint(20) DEFAULT NULL,
  FAIL_CACNT bigint(20) DEFAULT NULL,
  FC373_CNT bigint(20) DEFAULT NULL,
  FC374_CNT bigint(20) DEFAULT NULL,
  FC9563_CNT bigint(20) DEFAULT NULL,
  FC8501_CNT bigint(20) DEFAULT NULL,
  FC417_CNT bigint(20) DEFAULT NULL,
  FC8210_CNT bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  KEY idx_volte_fail_bts_date (BASE_DATE),
  KEY idx_volte_jo (AREA_JO_NM),
  KEY idx_volte_center (BIZ_HQ_NM),
  KEY idx_volte_team (OPER_TEAM_NM)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOLTE_FAIL_RATE_HNDSET (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  HNDSET_PET_NM varchar(50) DEFAULT NULL,
  SA_5G_SUPRT_DIV_NM varchar(50) DEFAULT NULL,
  TRY_CACNT bigint(20) DEFAULT NULL,
  COMP_CACNT bigint(20) DEFAULT NULL,
  FAIL_CACNT bigint(20) DEFAULT NULL,
  FC373_CNT bigint(20) DEFAULT NULL,
  FC374_CNT bigint(20) DEFAULT NULL,
  FC9563_CNT bigint(20) DEFAULT NULL,
  FC8501_CNT bigint(20) DEFAULT NULL,
  FC417_CNT bigint(20) DEFAULT NULL,
  FC8210_CNT bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  KEY idx_volte_hndset_date (BASE_DATE),
  KEY idx_volte_hndset_team (OPER_TEAM_NM),
  KEY idx_volte_hndset_hndset (HNDSET_PET_NM)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOLTE_FAIL_RATE_MM (
  BASE_YM int(11) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  TRY_CACNT bigint(20) DEFAULT NULL,
  COMP_CACNT bigint(20) DEFAULT NULL,
  FAIL_CACNT bigint(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  ETL_DT timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE SUM_VOLTE_FAIL_RATE (
  BASE_YM varchar(6) DEFAULT NULL,
  YEAR_BASE_WEEK_NM varchar(8) DEFAULT NULL,
  BASE_DATE int(11) DEFAULT NULL,
  DOW_NM varchar(20) DEFAULT NULL,
  WDAY_EWEEK_DIV_NM varchar(20) DEFAULT NULL,
  MKNG_CMPN_NM varchar(50) DEFAULT NULL,
  BIZ_HQ_NM varchar(50) DEFAULT NULL,
  OPER_TEAM_NM varchar(50) DEFAULT NULL,
  SIDO_NM varchar(100) DEFAULT NULL,
  GUN_GU_NM varchar(100) DEFAULT NULL,
  EUP_MYUN_DONG_NM varchar(100) DEFAULT NULL,
  AREA_HQ_NM varchar(50) DEFAULT NULL,
  AREA_CENTER_NM varchar(50) DEFAULT NULL,
  AREA_TEAM_NM varchar(50) DEFAULT NULL,
  AREA_JO_NM varchar(50) DEFAULT NULL,
  ANALS_3_PROD_LEVEL_NM varchar(50) DEFAULT NULL,
  TRY_CACNT bigint(20) DEFAULT NULL,
  COMP_CACNT bigint(20) DEFAULT NULL,
  FAIL_CACNT bigint(20) DEFAULT NULL,
  FC373_CNT bigint(20) DEFAULT NULL,
  FC374_CNT bigint(20) DEFAULT NULL,
  FC9563_CNT bigint(20) DEFAULT NULL,
  FC8501_CNT bigint(20) DEFAULT NULL,
  FC417_CNT bigint(20) DEFAULT NULL,
  FC8210_CNT bigint(20) DEFAULT NULL,
  BIZ_HQ_CD varchar(20) DEFAULT NULL,
  OPER_TEAM_CD varchar(20) DEFAULT NULL,
  NEW_HQ_NM varchar(50) DEFAULT NULL,
  NEW_CENTER_NM varchar(50) DEFAULT NULL,
  KEY idx_volte_fail_date (BASE_DATE),
  KEY idx_volte_fail_team (AREA_JO_NM),
  KEY idx_volte_fail_center (BIZ_HQ_NM)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

CREATE TABLE UPDATED_TABLES (
  UPDATE_DATE varchar(10) DEFAULT NULL,
  UPDATE_TYPE varchar(10) DEFAULT NULL,
  TABLE_NAME varchar(64) DEFAULT NULL,
  UPDATE_TIME datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;