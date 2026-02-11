import pandas as pd
import os

# ==============================================================================
# 2. DATA LOADING & INITIAL CLEANING
# ==============================================================================
def load_and_clean_data(file_name):
    df = pd.read_csv(
        "data/"+file_name, 
        sep=";", 
        encoding="utf-8-sig"
        )

    # Metadata for UI
    total_records = len(df)
    month_name = os.path.splitext(file_name)[0].capitalize()

    # Basic Normalization
    df["Data Protection State"] = df["Data Protection State"].fillna("No Protection")
    df["Techniques Used"] = df["Techniques Used"].fillna("Unknown")
    df["Techniques Used"] = df["Techniques Used"].astype(str).str.split(",")

    # Exploded dataframe for technique-specific analysis
    df_exploded = df.explode("Techniques Used")
    df_exploded["Techniques Used"] = df_exploded["Techniques Used"].str.strip()

    # Sensitivity Labeling
    df_exploded["Sensitivity_Label"] = df_exploded["Data Sensitivity score"].astype(str)
    df_exploded.loc[df_exploded["Data Sensitivity score"] == -1, "Sensitivity_Label"] = "-1 (Score Unknown)"

    return df, df_exploded, total_records, month_name

# ==============================================================================
# 3. HELPER FUNCTIONS
# ==============================================================================
def get_sophistication_signal(val):
    if pd.isna(val) is True or val is None:
        return "Unknown Technique"
    
    text = ",".join(val) if isinstance(val, list) else str(val)
    text = text.strip().lower()
    
    if text in ['', 'nan', 'unknown', 'none']:
        return "Unknown Technique"
    
    techs = [t.strip() for t in text.split(",") if t.strip()]
    count = len(techs)
    
    if count == 0:
        return "Unknown Technique"
    elif count == 1:
        return "Single Technique"
    elif 2 <= count <= 3:
        return "Multi-Technique (2–3)"
    else:
        return "Multi-Stage (4+)"

def format_combo(val):
    if pd.isna(val) is True: return "Unknown"
    if isinstance(val, list):
        techs = sorted([str(t).strip() for t in val if str(t).strip()])
    else:
        techs = sorted([t.strip() for t in str(val).split(",") if t.strip()])
    return " + ".join(techs) if techs else "Unknown"
