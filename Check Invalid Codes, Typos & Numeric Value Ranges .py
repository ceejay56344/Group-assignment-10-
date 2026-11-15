
# Strip accidental leading/trailing whitespace across all string columns
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

# 1. Fix spelling/casing inconsistencies in categorical fields
accom_typos = (df["primary_accommodation"] == "Off-Campus Accomodation").sum()
df["primary_accommodation"] = df["primary_accommodation"].replace({
    "Off-Campus Accomodation": "Off-Campus Accommodation"
})
log_check(
    "2a-5", "Categorical Spelling Standardization",
    f"{accom_typos} instances of misspelled 'Off-Campus Accomodation'",
    "Recode to standard label 'Off-Campus Accommodation'.",
    accom_typos, 0
)

meal_typos = df["main_meal_source_7days"].isin([
    "Dinning hall or Canteen", "Bought Vendor or tuckshop", "Cooked myself"
]).sum()
df["main_meal_source_7days"] = df["main_meal_source_7days"].replace({
    "Dinning hall or Canteen": "Dining Hall or Canteen",
    "Bought Vendor or tuckshop": "Bought from Vendor or Tuckshop",
    "Cooked myself": "Cooked Myself"
})
log_check(
    "2a-6", "Meal Source Label Standardization",
    f"{meal_typos} non-standard casing/spelling entries in main_meal_source_7days",
    "Standardize to title-case codebook labels.",
    meal_typos, 0
)

# 2. Restore literal 'None' string parsed as NaN by pandas in meals_per_day_typical_7days
consent_mask = df["consent"] == "Yes"
none_parsed_as_nan = (consent_mask & df["meals_per_day_typical_7days"].isna()).sum()
df.loc[consent_mask & df["meals_per_day_typical_7days"].isna(), "meals_per_day_typical_7days"] = "None (0 Meals)"
log_check(
    "2a-7", "Literal 'None' String Restoration",
    f"{none_parsed_as_nan} valid responses with 'None' meals parsed as NaN by pandas",
    "Restore NaN among consenting students to explicit category 'None (0 Meals)'.",
    none_parsed_as_nan, 0
)

# 3. Check numeric range bounds (Age: 16-99, Monthly Money USD >= 0, Health: 1-5)
numeric_fields = [
    "age", "monthly_money_usd", "health_rating_1_5",
    "dining_hall_days_7", "off_days_cooked_7",
    "off_rent_usd", "off_transport_weekly_usd", "off_distance_campus_km"
]
for col in numeric_fields:
    df[col] = pd.to_numeric(df[col], errors="coerce")

invalid_age = (consent_mask & ((df["age"] < 16) | (df["age"] > 99) | df["age"].isna())).sum()
invalid_budget = (consent_mask & ((df["monthly_money_usd"] < 0) | df["monthly_money_usd"].isna())).sum()
invalid_health = (consent_mask & ((df["health_rating_1_5"] < 1) | (df["health_rating_1_5"] > 5))).sum()
total_range_issues = int(invalid_age + invalid_budget + invalid_health)

log_check(
    "2a-8", "Numeric Range Validation",
    f"Out-of-range values found — Age: {invalid_age}, Budget: {invalid_budget}, Health: {invalid_health}",
    "Enforce valid bounds (Age 16-99, Budget >= 0, Health 1-5); set out-of-range values to NaN.",
    total_range_issues, 0
)
