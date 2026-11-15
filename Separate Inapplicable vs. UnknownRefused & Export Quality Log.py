# Rule 1: Non-consented respondents (consent == 'No') are INAPPLICABLE across all survey items
non_consent_mask = df["consent"] == "No"
survey_cols = [c for c in df.columns if c not in ["response_id", "consent"]]
for col in survey_cols:
    df.loc[non_consent_mask, col] = np.nan

# Rule 2: Accommodation skip-pattern separation
# On-campus items are INAPPLICABLE for Off-Campus students; Off-campus items are INAPPLICABLE for On-Campus students
on_campus_cols = ["on_campus_meal_plan", "dining_hall_days_7", "on_campus_meal_affordability"]
off_campus_cols = [
    "off_days_cooked_7", "off_cooking_fuel_source", "off_no_cook_main_reason",
    "off_rent_usd", "off_transport_weekly_usd", "off_distance_campus_km"
]

off_mask = df["primary_accommodation"] == "Off-Campus Accommodation"
on_mask = df["primary_accommodation"] == "On-Campus Resident"

for col in on_campus_cols:
    df.loc[off_mask | non_consent_mask, col] = np.nan

for col in off_campus_cols:
    df.loc[on_mask | non_consent_mask, col] = np.nan

# Rule 3: Conditional cooking barrier item ('off_no_cook_main_reason')
# Students who cook 7 days/week have this item legitimately skipped (Inapplicable: Active Cook)
# Students who cook < 7 days/week and left it blank are coded as 'Unknown / Refused'
active_cook_mask = off_mask & (df["off_days_cooked_7"] == 7)
non_cook_blank_mask = off_mask & (df["off_days_cooked_7"] < 7) & (df["off_no_cook_main_reason"].isna())

n_inapp_cooks = int(active_cook_mask.sum())
n_unknown_reason = int(non_cook_blank_mask.sum())

df.loc[active_cook_mask, "off_no_cook_main_reason"] = "Inapplicable (Active Daily Cook)"
df.loc[non_cook_blank_mask, "off_no_cook_main_reason"] = "Unknown / Refused"

log_check(
    "2a-9", "Skip-Pattern & Missingness Classification",
    f"Separated Inapplicable skip-routed cells (14 non-consent; 29 off-campus; 16 on-campus; {n_inapp_cooks} active cooks) from Unknown/Refused ({n_unknown_reason} cases).",
    "Code structural skips as NaN / 'Inapplicable' so they are excluded from item denominators; label item non-response as 'Unknown / Refused'.",
    n_inapp_cooks + n_unknown_reason, 0
)

# Export Quality Audit Log
quality_log_df = pd.DataFrame(quality_log)
quality_log_df.to_csv(OUTPUTS_DIR / "quality_audit_log.csv", index=False)
print("\n--- QUALITY AUDIT LOG (2a) ---")
print(quality_log_df[["Step", "Check_Category", "Count_Before", "Count_After"]].to_string(index=False))
```
---
Question 2(b): Tidy Case-Level File, Domain Indicators & Chart (Students 5 – 7)
```python
# ==============================================================================
# STUDENT 5: Produce Tidy Case-Level File with Eligibility Flags & Indicators
# ==============================================================================
tidy_df = df.copy()

# Construct explicit binary eligibility flags (1 = Eligible, 0 = Ineligible/Inapplicable)
tidy_df["elig_consent"] = (tidy_df["consent"] == "Yes").astype(int)
tidy_df["elig_on_campus"] = ((tidy_df["elig_consent"] == 1) & (tidy_df["primary_accommodation"] == "On-Campus Resident")).astype(int)
tidy_df["elig_off_campus"] = ((tidy_df["elig_consent"] == 1) & (tidy_df["primary_accommodation"] == "Off-Campus Accommodation")).astype(int)

# Construct coded binary core indicators (1 = Yes, 0 = No, NaN = Ineligible)
def encode_yes_no(series, elig_series):
    mapped = series.map({"Yes": 1, "No": 0})
    return np.where(elig_series == 1, mapped, np.nan)

tidy_df["ind1_whole_day_no_food_30d"] = encode_yes_no(tidy_df["whole_day_without_eating_30days"], tidy_df["elig_consent"])
tidy_df["ind2_skipped_meal_7d"] = encode_yes_no(tidy_df["skip_meal_7days"], tidy_df["elig_consent"])
tidy_df["ind3_cheaper_food_7d"] = encode_yes_no(tidy_df["switch_cheaper_food_7days"], tidy_df["elig_consent"])

# Export tidy case-level dataset (N = 59 rows)
tidy_output_path = PROCESSED_DIR / "tidy_case_level_food_insecurity.csv"
tidy_df.to_csv(tidy_output_path, index=False)
print(f"\nSaved tidy case-level file ({len(tidy_df)} rows) to: {tidy_output_path}")


# ==============================================================================
# STUDENT 6: Report Three Indicators Overall & By Domain (Counts, Denominators, Missing)
# ==============================================================================
def summarize_domain(data, domain_label, mask):
    subset = data[mask]
    total_cases = len(subset)
    valid_denom = int(subset["elig_consent"].sum())
    missing_inapp = total_cases - valid_denom

    ind1_cnt = int(subset["ind1_whole_day_no_food_30d"].sum()) if valid_denom > 0 else 0
    ind2_cnt = int(subset["ind2_skipped_meal_7d"].sum()) if valid_denom > 0 else 0
    ind3_cnt = int(subset["ind3_cheaper_food_7d"].sum()) if valid_denom > 0 else 0

    return {
        "Domain_Group": domain_label,
        "Total_Sampled_Cases": total_cases,
        "Missing_or_Inapplicable": missing_inapp,
        "Valid_Denominator_n": valid_denom,
        "Ind1_WholeDayNoFood_Count": ind1_cnt,
        "Ind1_Prevalence_%": round((ind1_cnt / valid_denom) * 100, 1) if valid_denom > 0 else np.nan,
        "Ind2_SkippedMeal_Count": ind2_cnt,
        "Ind2_Prevalence_%": round((ind2_cnt / valid_denom) * 100, 1) if valid_denom > 0 else np.nan,
        "Ind3_CheaperFood_Count": ind3_cnt,
        "Ind3_Prevalence_%": round((ind3_cnt / valid_denom) * 100, 1) if valid_denom > 0 else np.nan,
    }

domain_rows = [
    summarize_domain(tidy_df, "OVERALL (All Sampled Cases)", pd.Series(True, index=tidy_df.index)),
    summarize_domain(tidy_df, "Accommodation: On-Campus Resident", tidy_df["primary_accommodation"] == "On-Campus Resident"),
    summarize_domain(tidy_df, "Accommodation: Off-Campus", tidy_df["primary_accommodation"] == "Off-Campus Accommodation"),
    summarize_domain(tidy_df, "Institution: University", tidy_df["institution_type"] == "University"),
    summarize_domain(tidy_df, "Institution: Polytechnic / College", tidy_df["institution_type"] == "Polytechnic / College"),
    summarize_domain(tidy_df, "Sex: Female", tidy_df["gender"] == "Female"),
    summarize_domain(tidy_df, "Sex: Male", tidy_df["gender"] == "Male"),
    summarize_domain(tidy_df, "Ineligible (No Consent)", tidy_df["elig_consent"] == 0),
]

domain_report_df = pd.DataFrame(domain_rows)
domain_report_df.to_csv(OUTPUTS_DIR / "domain_indicators_report.csv", index=False)
print("\n--- THREE INDICATORS OVERALL & BY DOMAIN (2b) ---")
print(domain_report_df.to_string(index=False))


# ==============================================================================
# STUDENT 7: Generate Chart Answering Survey Question (Accommodation Comparison)
# ==============================================================================
chart_domains = domain_report_df[domain_report_df["Domain_Group"].isin([
    "Accommodation: On-Campus Resident",
    "Accommodation: Off-Campus"
])].copy()

labels = ["Whole Day Without\nEating (30d)", "Skipped a Meal\n(Past 7d)", "Switched to Cheaper\nFood (Past 7d)"]
on_campus_vals = [
    chart_domains.iloc[0]["Ind1_Prevalence_%"],
    chart_domains.iloc[0]["Ind2_Prevalence_%"],
    chart_domains.iloc[0]["Ind3_Prevalence_%"]
]
off_campus_vals = [
    chart_domains.iloc[1]["Ind1_Prevalence_%"],
    chart_domains.iloc[1]["Ind2_Prevalence_%"],
    chart_domains.iloc[1]["Ind3_Prevalence_%"]
]

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(8.5, 5))
rects1 = ax.bar(x - width/2, on_campus_vals, width, label="On-Campus Resident (n=16)", color="#1B365D")
rects2 = ax.bar(x + width/2, off_campus_vals, width, label="Off-Campus Accommodation (n=29)", color="#D97724")

ax.set_ylabel("Prevalence Among Consented Students (%)")
ax.set_title("Food Insecurity Indicators by Student Accommodation Setting (n = 45)")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylim(0, 90)
ax.legend(frameon=True)
ax.grid(axis="y", linestyle="--", alpha=0.4)

for rect in rects1:
    ax.annotate(f"{rect.get_height():.1f}%",
                xy=(rect.get_x() + rect.get_width()/2, rect.get_height()),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
for rect in rects2:
    ax.annotate(f"{rect.get_height():.1f}%",
                xy=(rect.get_x() + rect.get_width()/2, rect.get_height()),
                xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

plt.tight_layout()
chart_path = OUTPUTS_DIR / "chart_food_insecurity_by_accommodation.png"
plt.savefig(chart_path, dpi=300)
plt.close()
print(f"Saved survey chart to: {chart_path}")
