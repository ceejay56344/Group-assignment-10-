
import pandas as pd
import numpy as np
from pathlib import Path

# =====================================================
# STUDENT FOOD INSECURITY PROJECT
# COMPLETE DATA CLEANING AND ANALYSIS
# =====================================================

# 1. LOAD THE CSV FILE
file_path = Path(
    r"C:\Users\vchir\Desktop\Food Insecurities (Responses).csv"
)

df = pd.read_csv(file_path, encoding="utf-8-sig")

print("DATA SUCCESSFULLY LOADED")
print("Original dataset size:", df.shape)


# 2. RENAME THE 12 QUESTIONNAIRE COLUMNS
column_names = [
    "case_id",
    "timestamp",
    "consent",
    "accommodation",
    "uz_meals_provided",
    "meal_frequency",
    "meals_sufficient",
    "buy_additional_food",
    "skipped_meal_7days",
    "prepare_own_meals",
    "ran_out_food_30days",
    "whole_day_without_food"
]

if len(df.columns) != len(column_names):
    raise ValueError(
        f"Expected 12 columns but found {len(df.columns)}. "
        "Check your CSV questionnaire columns."
    )

df.columns = column_names


# 3. STANDARDISE MISSING VALUES
df = df.replace(
    ["<null>", "NULL", "null", "N/A", "n/a", ""],
    np.nan
)

# Remove unnecessary spaces from text responses
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )

# Convert timestamp to date/time
df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)


# 4. REMOVE DUPLICATES
print("\nDuplicates before cleaning:", df.duplicated().sum())

df = df.drop_duplicates()

# Remove repeated case IDs, keeping the first record
df = df.drop_duplicates(
    subset=["case_id"],
    keep="first"
)


# 5. STANDARDISE YES, NO AND SOMETIMES RESPONSES
def clean_response(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    responses = {
        "yes": "Yes",
        "no": "No",
        "sometimes": "Sometimes"
    }

    return responses.get(value, value.title())


response_columns = [
    "consent",
    "uz_meals_provided",
    "meal_frequency",
    "meals_sufficient",
    "buy_additional_food",
    "skipped_meal_7days",
    "prepare_own_meals",
    "ran_out_food_30days",
    "whole_day_without_food"
]

for col in response_columns:
    df[col] = df[col].apply(clean_response)


# 6. EXCLUDE RESPONDENTS WHO DID NOT CONSENT
total_submissions = len(df)

df = df[
    df["consent"].str.lower() == "yes"
].copy()

print("\nDATA AFTER CONSENT FILTER")
print("Total submissions:", total_submissions)
print("Consenting respondents:", len(df))
print("Excluded respondents:", total_submissions - len(df))


# 7. STANDARDISE ACCOMMODATION CATEGORIES
def clean_accommodation(value):
    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    if "on-campus" in value:
        return "On-campus"

    if "off-campus" in value:
        return "Off-campus"

    return value.title()


df["accommodation"] = df["accommodation"].apply(
    clean_accommodation
)


# 8. CREATE FOOD INSECURITY INDICATORS

# Meal skipping:
# Yes = 1, Sometimes = 1, No = 0

df["meal_skipping"] = df[
    "skipped_meal_7days"
].map({
    "Yes": 1,
    "Sometimes": 1,
    "No": 0
})

# Running out of food
df["ran_out_food"] = df[
    "ran_out_food_30days"
].map({
    "Yes": 1,
    "No": 0
})

# Going a whole day without food
df["whole_day_without_food_flag"] = df[
    "whole_day_without_food"
].map({
    "Yes": 1,
    "No": 0
})


# 9. CREATE A SUMMARY FUNCTION
def calculate_summary(column):

    counts = df[column].value_counts(
        dropna=True
    )

    percentages = df[column].value_counts(
        normalize=True,
        dropna=True
    ) * 100

    summary = pd.DataFrame({
        "Response": counts.index,
        "Frequency": counts.values,
        "Percentage": percentages.loc[counts.index].values
    })

    return summary.round(2)


# 10. CALCULATE OVERALL FOOD INSECURITY STATISTICS
def calculate_rate(column):

    valid = df[column].dropna()

    if len(valid) == 0:
        return {
            "Affected_Students": 0,
            "Valid_Responses": 0,
            "Percentage": 0
        }

    affected = int(valid.sum())

    return {
        "Affected_Students": affected,
        "Valid_Responses": len(valid),
        "Percentage": round(
            (affected / len(valid)) * 100, 2
        )
    }


meal_skipping_stats = calculate_rate("meal_skipping")

ran_out_stats = calculate_rate("ran_out_food")

whole_day_stats = calculate_rate(
    "whole_day_without_food_flag"
)

print("\nOVERALL FOOD INSECURITY RESULTS")

print("Meal skipping:", meal_skipping_stats)

print("Ran out of food:", ran_out_stats)

print("Whole day without food:", whole_day_stats)


# 11. COMPARE ON-CAMPUS AND OFF-CAMPUS STUDENTS

comparison = df.groupby(
    "accommodation",
    dropna=True
).agg(
    Total_Students=("case_id", "nunique"),

    Meal_Skipping=("meal_skipping", "mean"),

    Ran_Out_Of_Food=("ran_out_food", "mean"),

    Whole_Day_Without_Food=(
        "whole_day_without_food_flag", "mean"
    )
)

# Convert rates to percentages
comparison[
    [
        "Meal_Skipping",
        "Ran_Out_Of_Food",
        "Whole_Day_Without_Food"
    ]
] = comparison[
    [
        "Meal_Skipping",
        "Ran_Out_Of_Food",
        "Whole_Day_Without_Food"
    ]
] * 100

comparison = comparison.round(2)

print("\nON-CAMPUS VS OFF-CAMPUS COMPARISON")

print(comparison)


# 12. GENERATE RESPONSE DISTRIBUTION TABLES
accommodation_summary = calculate_summary(
    "accommodation"
)

meal_skipping_summary = calculate_summary(
    "skipped_meal_7days"
)

ran_out_summary = calculate_summary(
    "ran_out_food_30days"
)

whole_day_summary = calculate_summary(
    "whole_day_without_food"
)

meal_provision_summary = calculate_summary(
    "uz_meals_provided"
)

meal_sufficiency_summary = calculate_summary(
    "meals_sufficient"
)

additional_food_summary = calculate_summary(
    "buy_additional_food"
)

meal_preparation_summary = calculate_summary(
    "prepare_own_meals"
)

meal_frequency_summary = calculate_summary(
    "meal_frequency"
)


# 13. GENERATE CROSS-TABULATIONS
meal_skipping_comparison = pd.crosstab(
    df["accommodation"],
    df["skipped_meal_7days"],
    margins=True
)

food_shortage_comparison = pd.crosstab(
    df["accommodation"],
    df["ran_out_food_30days"],
    margins=True
)

whole_day_comparison = pd.crosstab(
    df["accommodation"],
    df["whole_day_without_food"],
    margins=True
)


# 14. CREATE DATA QUALITY REPORT
data_quality = pd.DataFrame({
    "Column": df.columns,
    "Missing_Values": df.isnull().sum().values,
    "Missing_Percentage": (
        df.isnull().mean().values * 100
    ).round(2)
})


# 15. EXPORT CLEANED DATA AND ANALYSIS TO EXCEL
output_file = (
    Path(r"C:\Users\vchir\Desktop")
    / "Food_Insecurity_Cleaned_Analysis.xlsx"
)

with pd.ExcelWriter(
    output_file,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Cleaned_Data",
        index=False
    )

    comparison.to_excel(
        writer,
        sheet_name="Accommodation_Comparison"
    )

    accommodation_summary.to_excel(
        writer,
        sheet_name="Accommodation_Summary",
        index=False
    )

    meal_skipping_summary.to_excel(
        writer,
        sheet_name="Meal_Skipping",
        index=False
    )

    ran_out_summary.to_excel(
        writer,
        sheet_name="Food_Shortages",
        index=False
    )

    whole_day_summary.to_excel(
        writer,
        sheet_name="Whole_Day_Without_Food",
        index=False
    )

    meal_provision_summary.to_excel(
        writer,
        sheet_name="Meal_Provision",
        index=False
    )

    meal_frequency_summary.to_excel(
        writer,
        sheet_name="Meal_Frequency",
        index=False
    )

    meal_sufficiency_summary.to_excel(
        writer,
        sheet_name="Meal_Sufficiency",
        index=False
    )

    additional_food_summary.to_excel(
        writer,
        sheet_name="Additional_Food",
        index=False
    )

    meal_preparation_summary.to_excel(
        writer,
        sheet_name="Meal_Preparation",
        index=False
    )

    meal_skipping_comparison.to_excel(
        writer,
        sheet_name="Skip_Meal_Comparison"
    )

    food_shortage_comparison.to_excel(
        writer,
        sheet_name="Food_Shortage_Comparison"
    )

    whole_day_comparison.to_excel(
        writer,
        sheet_name="Whole_Day_Comparison"
    )

    data_quality.to_excel(
        writer,
        sheet_name="Data_Quality",
        index=False
    )


# 16. EXPORT CLEANED DATA AS CSV FOR POWER BI
csv_output = (
    Path(r"C:\Users\vchir\Desktop")
    / "Food_Insecurity_Cleaned_Data.csv"
)

df.to_csv(csv_output, index=False)

# =====================================================
# FINAL RESULTS
# =====================================================

print("\n===================================")
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("===================================")

print("Final consenting respondents:", len(df))

print("Excel analysis saved to:", output_file)

print("Power BI CSV saved to:", csv_output)

print("\nYou can now import the cleaned CSV into Power BI.")
