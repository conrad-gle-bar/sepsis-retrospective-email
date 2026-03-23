

# placeholders for :alert_date and :encounter_id to find correct team members
treatment_team_query = """select
	cast(tt.PAT_ENC_CSN_ID as varchar(20)) PAT_ENC_CSN_ID
	, demo.EMAIL
    , emp.SYSTEM_LOGIN 
from TREATMENT_TEAM tt
	inner join CLARITY_EMP emp on emp.PROV_ID = tt.TR_TEAM_ID
	inner join CLARITY_EMP_DEMO demo on demo.USER_ID = emp.USER_ID
	inner join ZC_TRTMT_TEAM_REL zrole on zrole.TRTMNT_TEAM_REL_C = tt.TR_TEAM_REL_C
		and zrole.NAME <> 'Provider Team'
	INNER JOIN PAT_ENC_HSP hsp on tt.PAT_ENC_CSN_ID = hsp.PAT_ENC_CSN_ID
where tt.TR_TEAM_REL_C in ('13','2','40','1','100061','100080','108','112000202','147','23','33','7')
	and tt.PAT_ENC_CSN_ID = :encounter_id
	and :alert_date between convert(date, tt.TR_TEAM_BEG_DTTM) and CASE WHEN convert(date, tt.TR_TEAM_END_DTTM) IS NULL	
														                    THEN convert(date, hsp.HOSP_DISCH_TIME)
														                ELSE convert(date, tt.TR_TEAM_END_DTTM)
														            END
union														            
select  
    cast(attnd.PAT_ENC_CSN_ID as varchar(20)) PAT_ENC_CSN_ID
    , demo.EMAIL
    , emp.SYSTEM_LOGIN 
from Clarity..HSP_ATND_PROV	 attnd
    INNER JOIN PAT_ENC_HSP hsp on attnd.PAT_ENC_CSN_ID = hsp.PAT_ENC_CSN_ID
    inner join CLARITY_EMP emp on emp.PROV_ID = attnd.PROV_ID
	inner join CLARITY_EMP_DEMO demo on demo.USER_ID = emp.USER_ID
where attnd.PAT_ENC_CSN_ID = :encounter_id
	and :alert_date between convert(date, attnd.ATTEND_FROM_DATE) and CASE WHEN convert(date, attnd.ATTEND_TO_DATE) IS NULL	
														                    THEN convert(date, hsp.HOSP_DISCH_TIME)
														                ELSE convert(date, attnd.ATTEND_TO_DATE)
														            END """

emrn_query = '''SELECT DISTINCT TOP 1 cast(hsp.PAT_ENC_CSN_ID as varchar(20)) PAT_ENC_CSN_ID, pat.PAT_MRN_ID FROM PAT_ENC_HSP hsp 
	inner join PATIENT pat on pat.PAT_ID = hsp.PAT_ID
where hsp.PAT_ENC_CSN_ID = :encounter_id
'''