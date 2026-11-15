tidy_df = df.copy()

# Construct explicit binary eligibility flags (1 = Eligible, 0 = Ineligible/

Inapplicable)

tidy_df["elig_consent"]

= (tidy_df["consent"] ==

"Yes").astype(int)

tidy_df["elig_on_campus"] =

((tidy_df["elig_consent"] == 1) &

(tidy_df["primary_accommodation"]

== "On-Campus

Resident")).astype(int) tidy_df["elig_off_campus"] = ((tidy_df["elig_consent"] == 1) & (tidy_df["primary_accommodation"] == "Off-Campus

Accommodation")).astype(int)

# Construct coded binary core indicators (1 = Yes, 0 = No, NaN = Ineligible)

def encode_yes_no(series,

elig_series):

mapped = series.map({"Yes": 1,

"No": 0}
return np.where(elig_series == 1, mapped, np.nan)

tidy_df["ind1_whole_day_no_food_3 Od"] = encode_yes_no(tidy_df["wh ole_day_without_eating_30days"], tidy_df["elig_consent"]) tidy_df["ind2_skipped_meal_7d"] = encode_yes_no(tidy_ df["skip_meal_7days"], tidy_df["elig_consent"]) tidy_df["ind3_cheaper_food_7d"] = encode_yes_no(tidy_df["s witch_cheaper_food_7days"], tidy_df["elig_consent"])

# Export tidy case-level dataset (N 59 rows)

tidy_output_path =

PROCESSED_DIR /

"tidy_case_level_food_insecurity.csv" tidy_df.to_csv(tidy_output_path, index=False)

print(f"\nSaved tidy case-level file ({len(tidy_df)} rows) to: {tidy_output_path}")