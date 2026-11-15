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
