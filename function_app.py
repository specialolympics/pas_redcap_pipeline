import os
import logging
import azure.functions as func
import pandas as pd
from dotenv import load_dotenv
import time
load_dotenv(dotenv_path=".env")

app = func.FunctionApp()

@app.timer_trigger(schedule="0 33 11 * * *", 
                   arg_name="myTimer", 
                   run_on_startup=False,
                   use_monitor=True)

def PAS_RC_Upload(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due! -PAS_RC')

    logging.info('Python timer trigger function executed. -PAS_RC')

## Runs redcap_pipeline.py to export data from REDCap API, 
##      set datatypes (referencing columns.py), 
##      add age and PAS year columns, 
##      create dataframes specific to each survey,
##      convert to JSONs,
##      upload to Azure datalake

start = time.time()

from redcap_pipeline import *

total = build_total()
logging.info("Total data exported from REDCap servers. -PAS_RC")

total = set_col_types(total)
logging.info("Data types set for pipeline. -PAS_RC")

total = add_age_year(total)
logging.info("Year and age variables added. -PAS_RC")

## Filter to those started before today
t2 = total[(total['admin_start_date'] < pd.Timestamp.today())].copy()
total = total[total['record_id'].isin(t2['record_id'])].copy()

# Build survey-specific tables
admin = build_admin(total)
idkey = build_id_key(total)
ieq = build_ieq(total)
icf = build_icf(total)
ipfa = build_ipfa(total)
ipfas = build_ipfasurvey(total)
as1 = build_as1(total)
as2 = build_as2(total)
phys = build_ph(total)
socemo = build_se(total)
prtcp = build_prtcp(total)
pasn = build_notes(total)
ex = build_exit(total)

logging.info("All survey dfs created, ready to upload. -PAS_RC")

## Runs uploads.py to upload into datalake
storage_acct = os.getenv('storage_account')
cont = os.getenv('container')

hoy = pd.Timestamp.today().strftime("%Y-%m-%d")

## Upload Functions
from uploads import (upload_RC_df_to_az_datalake)

adm_file_ext = f"/hot/admin/Admin_{hoy}.json"
upload_RC_df_to_az_datalake(admin, "Admin", adm_file_ext, storage_acct, cont)
 
idk_file_ext = f"/hot/idkey/ID_Key_{hoy}.json"
upload_RC_df_to_az_datalake(idkey, "IDKey", idk_file_ext, storage_acct, cont)
 
ieq_file_ext = f"/hot/ieq/IEQ_{hoy}.json"
upload_RC_df_to_az_datalake(ieq, "IEQ", ieq_file_ext, storage_acct, cont)
 
icf_file_ext = f"/hot/icf/ICF_{hoy}.json"
upload_RC_df_to_az_datalake(icf, "ICF", icf_file_ext, storage_acct, cont)
 
ipfa_file_ext = f"/hot/ipfaphys/IPFAphys_{hoy}.json"
upload_RC_df_to_az_datalake(ipfa, "IPFA", ipfa_file_ext, storage_acct, cont)
 
ipfas_file_ext = f"/hot/ipfasvy/IPFA_svy_{hoy}.json"
upload_RC_df_to_az_datalake(ipfas, "IPFA_Survey", ipfas_file_ext, storage_acct, cont)
 
as1_file_ext = f"/hot/annualpt1/Annual_pt1_{hoy}.json"
upload_RC_df_to_az_datalake(as1, "AS1", as1_file_ext, storage_acct, cont)
 
as2_file_ext = f"/hot/annualpt2/Annual_pt2_{hoy}.json"
upload_RC_df_to_az_datalake(as2, "AS2", as2_file_ext, storage_acct, cont)
 
phys_file_ext = f"/hot/physhealth/Physical_Health_{hoy}.json"
upload_RC_df_to_az_datalake(phys, "Physical", phys_file_ext, storage_acct, cont)
 
se_file_ext = f"/hot/socemothealth/Soc_Emot_Health_{hoy}.json"
upload_RC_df_to_az_datalake(socemo, "Soc_Emot", se_file_ext, storage_acct, cont)
 
prtcp_file_ext = f"/hot/participation/Participation_{hoy}.json"
upload_RC_df_to_az_datalake(prtcp, "Participation", prtcp_file_ext, storage_acct, cont)
 
pasn_file_ext = f"/hot/notes/PAS_notes_{hoy}.json"
upload_RC_df_to_az_datalake(pasn, "PAS_Notes", pasn_file_ext, storage_acct, cont)
 
ex_file_ext = f"/hot/exit/Exit_{hoy}.json"
upload_RC_df_to_az_datalake(ex, "Exit", ex_file_ext, storage_acct, cont)

end = time.time()

fulltime = end - start
logging.info(f"Elapsed time in seconds: {fulltime}")
print("Elapsed seconds: ", fulltime)
