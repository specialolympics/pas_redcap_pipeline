## Pipeline for converting RC
import logging
import requests
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

def build_total():
    ## Import data from each program through RC API
    ## AZ
    fields = {
        'token': os.getenv('api_token_AZ'),
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'exportSurveyFields': 'true'
    }

    r = requests.post(os.getenv('api_url'), data=fields)
    print('HTTP Status AZ: ' + str(r.status_code))

    # Convert the data to pandas data frame for easier manipulation.
    data = r.json()   
    dfaz = pd.DataFrame(data)  # 226 x 1173 !!

    ## CO
    fields = {
        'token': os.getenv('api_token_CO'),
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'exportSurveyFields': 'true'
    }

    r = requests.post(os.getenv('api_url'), data=fields)
    print('HTTP Status CO: ' + str(r.status_code))

    # Convert the data to pandas data frame for easier manipulation.
    data = r.json()   
    dfco = pd.DataFrame(data)  # 199 x 1173 

    ## MN
    fields = {
        'token': os.getenv('api_token_MN'),
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'exportSurveyFields': 'true'
    }

    r = requests.post(os.getenv('api_url'), data=fields)
    print('HTTP Status MN: ' + str(r.status_code))

    # Convert the data to pandas data frame for easier manipulation.
    data = r.json()   
    dfmn = pd.DataFrame(data)  # 78 x 1173

    ## NM
    fields = {
        'token': os.getenv('api_token_NM'),
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'exportSurveyFields': 'true'
    }

    r = requests.post(os.getenv('api_url'), data=fields)
    print('HTTP Status NM: ' + str(r.status_code))

    # Convert the data to pandas data frame for easier manipulation.
    data = r.json()   
    dfnm = pd.DataFrame(data)  # 134 x 1173

    ## PA
    fields = {
        'token': os.getenv('api_token_PA'),
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'exportSurveyFields': 'true'
    }

    r = requests.post(os.getenv('api_url'), data=fields)
    print('HTTP Status PA: ' + str(r.status_code))

    # Convert the data to pandas data frame for easier manipulation.
    data = r.json()   
    dfpa = pd.DataFrame(data)  # 129 x 1173

    ## WI
    fields = {
        'token': os.getenv('api_token_WI'),
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'exportSurveyFields': 'true'
    }

    r = requests.post(os.getenv('api_url'), data=fields)
    print('HTTP Status WI: ' + str(r.status_code))

    # Convert the data to pandas data frame for easier manipulation.
    data = r.json()   
    dfwi = pd.DataFrame(data)  # 133 x 1173

    logging.info("REDCap data imported from all programs. -PAS_RC")

    ## Add Program Column
    az2 = dfaz
    az2['Program'] = 'Arizona'
    co2 = dfco
    co2['Program'] = 'Colorado'
    mn2 = dfmn
    mn2['Program'] = 'Minnesota'
    nm2 = dfnm
    nm2['Program'] = 'New Mexico'
    pa2 = dfpa
    pa2['Program'] = 'Pennsylvania'
    wi2 = dfwi
    wi2['Program'] = 'Wisconsin'

    ## Add REDCap_ID
    az2['REDCap_ID'] = az2.record_id + "_AZ"
    co2['REDCap_ID'] = co2.record_id + "_CO"
    mn2['REDCap_ID'] = mn2.record_id + "_MN"
    nm2['REDCap_ID'] = nm2.record_id + "_NM"
    pa2['REDCap_ID'] = pa2.record_id + "_PA"
    wi2['REDCap_ID'] = wi2.record_id + "_WI"

    ## Combine them all
    tot = pd.concat([az2, co2, mn2, nm2, pa2, wi2])

    ## Azure id
    tot.insert(0, 'id', tot['REDCap_ID'])

    logging.info("REDCap data successfully concatenated. -PAS_RC")

    return tot

## Need to set data types, starting with column imports 
  ### UPDATE folder path:
from columns import (
    CHAR_COLS,
    INT_COLS_1,
    INT_COLS_2,
    FLOAT_COLS,
    BOOL_COLS,
    DATE_COLS,
    DT_COLS,
    ADMIN_COLS,
    EXIT_COLS,
    IEQ_COLS,
    ICF_COLS,
    IPFA_COLS,
    IPFA_SURVEY_COLS,
    ANNUAL_PT1_COLS,
    ANNUAL_PT2_COLS,
    PHYSICAL_HEALTH_COLS,
    SOCIAL_EMOTIONAL_COLS,
    PARTICIPATION_COLS,
    PAS_NOTES_COLS)

def set_col_types(tot):
    # --- Keep only columns present in the dataframe ---
    cha_cols = [c for c in CHAR_COLS if c in tot.columns]
    num_cols1  = [c for c in INT_COLS_1 if c in tot.columns]
    num_cols2  = [c for c in INT_COLS_2 if c in tot.columns]
    flt_cols = [c for c in FLOAT_COLS if c in tot.columns]
    boo_cols = [c for c in BOOL_COLS if c in tot.columns]
    dat_cols = [c for c in DATE_COLS if c in tot.columns]
    d_cols   = [c for c in DT_COLS if c in tot.columns]

    # --- Integers ---
    tot[num_cols1] = (tot[num_cols1].apply(pd.to_numeric, errors="coerce").astype("Int64"))
    tot[num_cols2] = (tot[num_cols2].apply(pd.to_numeric, errors="coerce").astype("Int64"))

    # --- Floats ---
    tot[flt_cols] = (tot[flt_cols].apply(pd.to_numeric, errors="coerce"))

    # --- Logical (override numeric → Int8 keeps 0/1/NA) ---
    tot[boo_cols] = (tot[boo_cols].apply(pd.to_numeric, errors="coerce").astype("Int8"))

    # --- Date ---
    tot[dat_cols] = (tot[dat_cols].apply(pd.to_datetime, errors="coerce"))

    # --- Datetime (POSIXct) ---    
    tot[d_cols] = (tot[d_cols].apply(pd.to_datetime, format="%m/%d/%Y %H:%M", errors="coerce"))

    # --- Character ---
    tot[cha_cols] = (tot[cha_cols].astype("string"))

    # --- Defragment (recommended after many assignments) ---
    tot = tot.copy()

    logging.info("Total df columns set to correct types. -PAS_RC")

    return tot

def add_age_year(tot):
    ## Fill in dob, gender
    tot[['dob', 'gender']] = (
        tot.groupby('REDCap_ID')[['dob', 'gender']]
        .transform(lambda x: x.ffill().bfill())
    )

    ## Age at start of PAS
    tot["Age_at_Start"] = (
        tot["admin_start_date"].dt.year - tot["dob"].dt.year
        - ((tot["admin_start_date"].dt.month < tot["dob"].dt.month) |
        ((tot["admin_start_date"].dt.month == tot["dob"].dt.month) &
            (tot["admin_start_date"].dt.day < tot["dob"].dt.day)))
    ).astype("Int8")

    ## Ordinal year in PAS
    today = pd.Timestamp.today()

    tot['Year_Ordinal'] = (
        1
        + (today.year - tot['admin_start_date'].dt.year
        - ((today.month < tot['admin_start_date'].dt.month) |
            ((today.month == tot['admin_start_date'].dt.month) &
            (today.day < tot['admin_start_date'].dt.day))))
    ).astype("Int8")

    logging.info("Successfully added age and PAS year. -PAS_RC")

    return tot

##############################
## Convert cleaned total REDCap data export into PAS-specific survey tables (June 26)

## Check for unique ids (to satisfy Azure reqs)
def check_unique_id(df):
    duplicates = df[df["id"].duplicated(keep=False)]

    if not duplicates.empty:
        raise ValueError(
            f"{len(duplicates)} duplicate ids found:\n"
            f"{duplicates['id'].tolist()[:20]}"
        )

    return True

## Calculate age at survey
def calculate_age(dob_col, event_col):
    dob = pd.to_datetime(dob_col)
    event = pd.to_datetime(event_col)

    age = (event.dt.year - dob.dt.year - 
           ((event.dt.month < dob.dt.month) | 
            ((event.dt.month == dob.dt.month) & 
             (event.dt.day < dob.dt.day)))).astype("Int8")

    return age


## Admin table
def build_admin(df):
    ad = (df.loc[df["redcap_event_name"] == "admin_arm_1"].copy())
    ad["id"] = ad["REDCap_ID"]
    ad = ad[ADMIN_COLS]
    ad["Days_since_start"] = (pd.Timestamp.today().normalize() - ad["admin_start_date"]).dt.days
    ad.insert(9, "Days_since_start", ad.pop("Days_since_start"))
    ad.insert(5, "Arm", 1)
    ad.insert(5, "Event_Name", "Admin")
    check_unique_id(ad)
    return ad

## ID Key
def build_id_key(df):
    key1 = df.loc[df["redcap_event_name"] == "admin_arm_1", ["id", "REDCap_ID", "admin_fitbit_id"]]
    ema1 = df.loc[df["redcap_event_name"] == "baseline_arm_1", ["REDCap_ID", "ema_mob_code"]]
    #ema1 = bl1[["REDCap_ID", "ema_mob_code"]]
    key = key1.merge(ema1, on="REDCap_ID", how="left")
    key = key.rename(columns={"admin_fitbit_id": "Fitbit_ID",
                              "ema_mob_code": "Illumivu_ID"})
    check_unique_id(key)
    return key

## IEQ
def build_ieq(df):
    iq = (df.loc[df["redcap_event_name"] == "baseline_arm_1"].copy())
    iq = iq[IEQ_COLS]
    iq.insert(4, "Age_at_Survey", (calculate_age(iq["dob"], iq["ieq_date"])))
    iq.insert(2, "Arm", 1)
    iq.insert(2, "Event_Name", "Baseline")
    iq.insert(0, "id", (iq["REDCap_ID"] + "_Baseline"))
    check_unique_id(iq)
    return iq

## ICF
def build_icf(df):
    ic = (df.loc[df["redcap_event_name"] == "baseline_arm_1"].copy())
    ic = ic[ICF_COLS]
    ic.insert(3, "Age_at_Survey", (calculate_age(ic["dob"], ic["icf_ath_sig_d"])))
    ic.drop(columns=["dob"], inplace=True)
    ic.insert(2, "Arm", 1)
    ic.insert(2, "Event_Name", "Baseline")
    ic.insert(0, "id", (ic["REDCap_ID"] + "_Baseline"))
    check_unique_id(ic)
    return ic

## IPFA
def build_ipfa(df):
    ip = df.loc[df["redcap_event_name"].isin(["baseline_arm_1",
        "y2_t1_annual_arm_1", "y3_t1_annual_arm_1"])]
    ip = ip[ip["ipa_date"].notna()]
    ip = ip[IPFA_COLS]
    ip.insert(4, "Age_at_Survey", (calculate_age(ip["dob"], ip["ipa_date"])))
    ip.drop(columns=["dob"], inplace=True)
    year_map = {"baseline_arm_1": "Y1", "y2_t1_annual_arm_1": "Y2", "y3_t1_annual_arm_1": "Y3"}
    ip["RC_year"] = (ip["redcap_event_name"].map(year_map))
    ip.insert(2, "Arm", 1)
    ip.insert(2, "Time_Period", 1)
    ip.insert(2, "Year", (ip["RC_year"].str.extract(r"Y(\d)").astype(int)))
    ip.insert(2, "Event_Name", (
        np.where(ip["redcap_event_name"].str.contains("baseline"),
                 "Baseline", "Annual")))
    ip.insert(0, "id", (ip["REDCap_ID"].astype(str) + "_" + 
                        ip["RC_year"] + "_T1"))
    ip.drop(columns=["RC_year"], inplace=True)
    check_unique_id(ip)
    return ip    

## IPFA Survey 
def build_ipfasurvey(df):
    ips = df.loc[df["redcap_event_name"].isin(["baseline_arm_1",
        "y2_t1_annual_arm_1", "y3_t1_annual_arm_1"])]
    ips = ips[ips["ipasvy_date"].notna()]
    ips = ips[IPFA_SURVEY_COLS]
    ips.insert(5, "Age_at_Survey", (calculate_age(ips["dob"], ips["ipasvy_date"])))
    ips.drop(columns=["dob"], inplace=True)
    year_map = {"baseline_arm_1": "Y1", "y2_t1_annual_arm_1": "Y2", "y3_t1_annual_arm_1": "Y3"}
    ips["RC_year"] = (ips["redcap_event_name"].map(year_map))
    ips.insert(2, "Arm", 1)
    ips.insert(2, "Time_Period", 1)
    ips.insert(2, "Year", (ips["RC_year"].str.extract(r"Y(\d)").astype(int)))
    ips.insert(2, "Event_Name", (
        np.where(ips["redcap_event_name"].str.contains("baseline"),
                 "Baseline", "Annual")))
    ips.insert(0, "id", (ips["REDCap_ID"].astype(str) + "_" + 
                        ips["RC_year"] + "_T1"))
    ips.drop(columns=["RC_year"], inplace=True)
    check_unique_id(ips)
    return ips    

## Annual Survey 1
def build_as1(df):
    a1 = df.loc[df["redcap_event_name"].isin(["y1_t1_annual_arm_1",
        "y2_t1_annual_arm_1", "y3_t1_annual_arm_1"])]
    a1 = a1.loc[a1["as1_date"].notna() | a1["as1_adjusted"].notna()]
    a1 = a1[ANNUAL_PT1_COLS]
    a1.insert(5, "Age_at_Survey", (calculate_age(a1["dob"], a1["as1_date"])))
    a1.drop(columns=["dob"], inplace=True)
    a1["RC_year"] = (a1["redcap_event_name"].str.extract(r"(y[1-3])", expand=False).str.upper())
    a1.insert(2, "Arm", 1)
    a1.insert(2, "Time_Period", 1)
    a1.insert(2, "Year", (a1["RC_year"].str.extract(r"Y(\d)").astype(int)))
    a1.insert(2, "Event_Name", "Annual")
    a1.insert(0, "id", (a1["REDCap_ID"].astype(str) + "_" + 
                        a1["RC_year"] + "_T1"))
    a1.drop(columns=["RC_year"], inplace=True)
    check_unique_id(a1)
    return a1 

## Annual Survey 2
def build_as2(df):
    a2 = df.loc[df["redcap_event_name"].isin(["y1_t1_annual_arm_1",
        "y2_t1_annual_arm_1", "y3_t1_annual_arm_1"])]
    a2 = a2[a2["as2_date"].notna()]
    a2 = a2[ANNUAL_PT2_COLS]
    a2.insert(5, "Age_at_Survey", (calculate_age(a2["dob"], a2["as2_date"])))
    a2.drop(columns=["dob"], inplace=True)
    a2["RC_year"] = (a2["redcap_event_name"].str.extract(r"(y[1-3])", expand=False).str.upper())
    a2.insert(2, "Arm", 1)
    a2.insert(2, "Time_Period", 1)
    a2.insert(2, "Year", (a2["RC_year"].str.extract(r"Y(\d)").astype(int)))
    a2.insert(2, "Event_Name", "Annual")
    a2.insert(0, "id", (a2["REDCap_ID"].astype(str) + "_" + 
                        a2["RC_year"] + "_T1"))
    a2.drop(columns=["RC_year"], inplace=True)
    check_unique_id(a2)
    return a2 

## Physical
def build_ph(df):
    ph = df.loc[df["redcap_event_name"].isin(["y1_t2_physical_arm_1",
        "y2_t2_physical_arm_1", "y3_t2_physical_arm_1"])]
    ph = ph[PHYSICAL_HEALTH_COLS]
    ph = ph.loc[ph["ph_date"].notna() | ph["ph_phys_act_lw"].notna()]
    ph.insert(5, "Age_at_Survey", (calculate_age(ph["dob"], ph["ph_date"])))
    ph.drop(columns=["dob"], inplace=True)
    ph["RC_year"] = (ph["redcap_event_name"].str.extract(r"(y[1-3])", expand=False).str.upper())
    ph.insert(2, "Arm", 1)
    ph.insert(2, "Time_Period", 2)
    ph.insert(2, "Year", (ph["RC_year"].str.extract(r"Y(\d)").astype(int)))
    ph.insert(2, "Event_Name", "Physical")
    ph.insert(0, "id", (ph["REDCap_ID"].astype(str) + "_" + 
                        ph["RC_year"] + "_T2"))
    ph.drop(columns=["RC_year"], inplace=True)
    check_unique_id(ph)
    return ph 

## Social-Emotional
def build_se(df):
    se = df.loc[df["redcap_event_name"].isin(["y1_t3_soc_emot_arm_1",
        "y2_t3_soc_emot_arm_1", "y3_t3_soc_emot_arm_1"])]
    se = se[SOCIAL_EMOTIONAL_COLS]
    se.insert(5, "Age_at_Survey", (calculate_age(se["dob"], se["se_date"])))
    se.drop(columns=["dob"], inplace=True)
    se["RC_year"] = (se["redcap_event_name"].str.extract(r"(y[1-3])", expand=False).str.upper())
    se.insert(2, "Arm", 1)
    se.insert(2, "Time_Period", 3)
    se.insert(2, "Year", (se["RC_year"].str.extract(r"Y(\d)").astype(int)))
    se.insert(2, "Event_Name", "Soc_Emot")
    se.insert(0, "id", (se["REDCap_ID"].astype(str) + "_" + 
                        se["RC_year"] + "_T3"))
    se.drop(columns=["RC_year"], inplace=True)
    check_unique_id(se)
    return se

## Participation
def build_prtcp(df):
    pt = df.loc[df["redcap_event_name"].isin(["y1_t1_annual_arm_1",
        "y2_t1_annual_arm_1", "y3_t1_annual_arm_1", "y1_t2_physical_arm_1",
        "y2_t2_physical_arm_1", "y3_t2_physical_arm_1", "y1_t3_soc_emot_arm_1",
        "y2_t3_soc_emot_arm_1", "y3_t3_soc_emot_arm_1"])]
    pt = pt.rename(columns = {'as1_date':'as_date'})
    pt = pt[PARTICIPATION_COLS].copy()
    pt.insert(2, "date", (pt["as_date"].combine_first(pt["ph_date"]).combine_first(pt["se_date"])))
    pt = pt.copy()
    pt.insert(3, "Age_at_Survey", (calculate_age(pt["dob"], pt["date"])))
    pt = pt.copy()
    pt_bases = (pd.Series(pt.columns).loc[lambda s: s.str.match(r"^(as|ph|se)_")].str.replace(r"^(as|ph|se)_", "", regex=True))
    pt_bases = (pt_bases[pt_bases != "date"].drop_duplicates().tolist())
    pt_bases = pt_bases.copy()
    for v in pt_bases:
        cols = [f"{p}_{v}" for p in ("as", "ph", "se") if f"{p}_{v}" in pt.columns]
        pt[v] = pt[cols[0]]
        for col in cols[1:]:
            pt[v] = pt[v].combine_first(pt[col])
    prefix_cols = pt.filter(regex=r"^(as|ph|se)_").columns
    first_cols = ["REDCap_ID", "redcap_event_name", "date","Age_at_Survey", *pt_bases,]
    remaining_cols = [c for c in pt.columns if c not in first_cols and c not in prefix_cols]
    pt = pt[first_cols + remaining_cols]
    pt = pt.copy()
    pt = pt[pt["pt_so_years"].notna()]
    pt["RC_year"] = (pt["redcap_event_name"].str.extract(r"(y[1-3])", expand=False).str.upper())
    pt = pt.copy()
    pt["RC_time"] = (pt["redcap_event_name"].str.extract(r"(t[1-3])", expand=False).str.upper())
    pt = pt.copy()
    pt.insert(0, "id", (pt["REDCap_ID"] + "_" + pt["RC_year"] + "_" + pt["RC_time"]))
    pt = pt.copy()
    pt.insert(3, "Arm", 1)
    pt = pt.copy()
    pt.insert(3, "Time_Period", (pt["RC_time"].str.extract(r"(\d+)", expand=False).astype("Int64")))
    pt = pt.copy()
    pt.insert(3, "Year", (pt["RC_year"].str.extract(r"(\d+)", expand=False).astype("Int64")))
    pt = pt.copy()
    pt.insert(3, "Event_Name", np.select([pt["redcap_event_name"].str.contains("_annual_", na=False),
                                pt["redcap_event_name"].str.contains("_physical_", na=False),
                                pt["redcap_event_name"].str.contains("_soc_emot_", na=False),],
                                ["Annual", "Physical", "Soc_Emot",], 
                                default="",))
    pt = pt.copy()
    pt = pt.drop(columns=["dob", "RC_year", "RC_time"])
    check_unique_id(pt)
    return pt

## PAS Notes
def build_notes(df):
    pn = (df.loc[df["redcap_event_name"] == "repeating_inst_arm_1"].copy())
    pn = pn[PAS_NOTES_COLS]
    pn.insert(2, "Age_at_Note", (calculate_age(pn["dob"], pn["pa_participant_notes_date"])))
    pn.drop(columns=["dob"], inplace=True)
    pn.insert(1, "Arm", 1)
    pn.insert(1, "Event_Name", "Repeating_Inst")
    pn = pn.copy()
    pn.insert(0, "id", (pn["REDCap_ID"] + "_" + pn["pa_participant_notes_date"].astype(str)))
    check_unique_id(pn)
    return pn

## Exit Survey
def build_exit(df):
    ex = df[EXIT_COLS]
    ex = ex[ex["exit_date"].notna()]
    ex.insert(4, "Age_at_Exit", (calculate_age(ex["dob"], ex["exit_date"])))
    ex.drop(columns=["dob"], inplace=True)
    ex.insert(1, "Arm", 1)
    ex.insert(1, "Event_Name", "Admin")
    ex.insert(0, "id", (ex["REDCap_ID"] + "_" + ex["exit_date"].astype(str)))
    check_unique_id(ex)
    return ex


