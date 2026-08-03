## Upload each of the survey-specific dfs to Azure

import logging
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
import traceback

def upload_RC_df_to_az_datalake(
    df: pd.DataFrame,
    df_name: str,
    FileExt: str,
    # key_vault_uri: str,
    # secret_name: str,
    storage_account: str,
    container: str
):
    """
    Convert REDCap dataframes to JSONs and upload to Azure Blob Storage.
    Returns None if no uploads succeeded.
    """
    df = df.copy() 
    try:
        if df is None or df.empty:
            logging.info(f"Nothing in {df_name} to upload. -PAS_RC")
            return None
 
        if "id" not in df.columns:
            logging.error(f"{df_name} missing 'id' columns for Azure. -PAS_RC")
            return None
 
        logging.info(f"Found {len(df)} rows in {df_name}.  -PAS_RC")

        # Replace NA in string columns with ""
        str_cols = df.select_dtypes(include=["object", "string"]).columns
        df[str_cols] = df[str_cols].fillna("")
        # Leave non-string NA -> will become null in JSON

        from columns import (DATE_COLS)
        dat_cols = [c for c in DATE_COLS if c in df.columns]    
        df[dat_cols] = df[dat_cols].apply(lambda col: col.dt.strftime("%Y-%m-%d"))

        # --- Step 2: Convert to JSON ---
        json_str = df.to_json(
            orient="records",   # equivalent to dataframe="rows"
            lines=False,
            date_format="iso")

        logging.info(f"Step 1: {df_name} converted to JSON. -PAS_RC")
        print(f"{df_name} converted to JSON.")

        credential = DefaultAzureCredential()

        # vault_url = key_vault_uri
        # secret_client = SecretClient(
        #     vault_url=vault_url,
        #     credential=credential
        # )

        # sastoken = secret_client.get_secret(secret_name).value

        account_url = f"https://{storage_account}.dfs.core.windows.net"

        service_client = DataLakeServiceClient(
            account_url=account_url,
            credential=credential
        )

        file_system_client = service_client.get_file_system_client(
            file_system=container
        )

        file_client = file_system_client.get_file_client(FileExt)

        file_client.upload_data(
            json_str,
            overwrite=True
        )

        logging.info(f"{df_name} successfully uploaded. -PAS_RC")
        print(f"{df_name} successfully uploaded.")

    except Exception as e:
        print("EXCEPTION TYPE:", type(e))
        print("EXCEPTION:", repr(e))
        traceback.print_exc()
        raise

### first draft exception (before copilot-assisted above):
    # except Exception as e:
    #     logging.exception(f"Error uploading {df_name}: {e}")
    #     print(f"Error uploading {df_name}: {e}")
    #     return None

