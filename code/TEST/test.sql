SELECT WORK_DT
     , DEPT_ID
     , SCUST_ID
     , ITEM_L_CD
     , MNG_AMT
     , OPR_AMT
     , MOD_AMT
     , MYPM_AMT
     , N_ITEM_L_CD
     , EMP_ID
  FROM dbo.F_SGG_T_��������ǥ
    /*JOIN DW..���̺�
    JOIN aaaa
    
    
    */
 WHERE WORK_DT BETWEEN SUBSTRING('#$ETL_STR_DT#', 1, 4)+'-'+SUBSTRING('#$ETL_STR_DT#', 5, 2)+'-'+SUBSTRING('#$ETL_STR_DT#', 7, 2)
                  AND SUBSTRING('#$ETL_END_DT#', 1, 4)+'-'+SUBSTRING('#$ETL_END_DT#', 5, 2)+'-'+SUBSTRING('#$ETL_END_DT#', 7, 2)
;
