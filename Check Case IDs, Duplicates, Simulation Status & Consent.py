# 1. Check Case ID uniqueness and format (R-001 to R-059)
missing_ids = df["response_id"].isna().sum()
duplicate_ids = df["response_id"].duplicated().sum()
log_check(
    "2a-1", "Case ID Integrity",
    f"Missing IDs: {missing_ids}; Duplicate IDs: {duplicate_ids}",
    "Verify unique sequential IDs (R-001..R-059); drop exact duplicates if found.",
    len(df), len(df.drop_duplicates(subset=["response_id"]))
)

# 2. Check full-row exact duplicates
exact_dups = df.duplicated().sum()
log_check(
    "2a-2", "Exact Row Duplicates",
    f"{exact_dups} duplicate submission rows detected",
    "Retain unique submissions; drop exact duplicates.",
    len(df), len(df.drop_duplicates())
)

# 3. Check for simulation/test records (e.g., age < 16 or test tags in ID)
sim_rows = df["response_id"].astype(str).str.contains("TEST|SIM", case=False, na=False).sum()
log_check(
    "2a-3", "Simulation / Test Records",
    f"{sim_rows} pilot test/simulation records present in production export",
    "Remove any records tagged TEST/SIM prior to analysis.",
    len(df), len(df) - sim_rows
)

# 4. Consent screening status
df["consent"] = df["consent"].astype(str).str.strip().str.title()
n_total = len(df)
n_consent_yes = (df["consent"] == "Yes").sum()
n_consent_no = (df["consent"] == "No").sum()
log_check(
    "2a-4", "Informed Consent Status",
    f"{n_consent_no} respondents declined consent ('No'); {n_consent_yes} consented ('Yes')",
    "Retain all 59 rows in master tidy file with elig_consent=0 for 'No'; exclude elig_consent=0 from substantive denominators.",
    n_total, n_consent_yes
)
