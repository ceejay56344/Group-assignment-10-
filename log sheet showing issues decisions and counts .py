
import pandas as pd
import numpy as np

# ==========================================
# 1. LOAD DATASET
# ==========================================

file_path = r"C:\Users\vchir\Desktop\tertiary_student_food_insecurity_59_responses-v3.csv"

output_path = r"C:\Users\vchir\Desktop\tertiary_student_food_insecurity_cleaned.csv"

quality_log_path = r"C:\Users\vchir\Desktop\food_insecurity_quality_log.csv"

df = pd.read_csv(file_path)

# Preserve original dataset
original_df = df.copy()

# Quality log
quality_log = []

initial_rows = len(df)


# ==========================================
# 2. FUNCTION TO RECORD QUALITY CHECKS
# ==========================================

def log_quality(check, issue, before, decision, after, status):

    quality_log.append({
        "Check": check,
        "Issue identified": issue,
        "Count before": before,
        "Decision": decision,
        "Count after": after,
        "Status": status
    })


# ==========================================
# 3. INITIAL DATASET CHECK
# ==========================================

print("INITIAL DATASET")
print("Rows:", len(df))
print("Columns:", len(df.columns))

log_quality(
    "Initial dataset",
    "Original dataset loaded",
    len(df),
    "Retain original responses",
    len(df),
    "Recorded"
)


# ==========================================
# 4. CHECK MISSING VALUES
# ==========================================

missing_before = int(df.isnull().sum().sum())

log_quality(
    "Missing values",
    f"{missing_before} missing cells identified",
    missing_before,
    "Retain missing values for review; do not impute automatically",
    int(df.isnull().sum().sum()),
    "Issue found" if missing_before > 0 else "No issue found"
)


# ==========================================
# 5. CHECK DUPLICATE ROWS
# ==========================================

duplicates_before = int(df.duplicated().sum())

df = df.drop_duplicates()

duplicates_after = int(df.duplicated().sum())

log_quality(
    "Duplicate records",
    f"{duplicates_before} duplicate rows identified",
    duplicates_before,
    "Remove exact duplicate rows",
    duplicates_after,
    "Cleaned" if duplicates_before > 0 else "No issue found"
)


# ==========================================
# 6. CLEAN COLUMN NAMES
# ==========================================

old_columns = df.columns.tolist()

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)

changed_columns = sum(
    old != new for old, new in zip(old_columns, df.columns)
)

log_quality(
    "Column names",
    f"{changed_columns} column names standardised",
    changed_columns,
    "Standardise column names",
    0,
    "Cleaned" if changed_columns > 0 else "No changes required"
)


# ==========================================
# 7. CLEAN TEXT SPACES
# ==========================================

text_columns = df.select_dtypes(include=["object"]).columns

whitespace_changes = 0

for column in text_columns:

    original_values = df[column].copy()

    df[column] = df[column].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )

    whitespace_changes += int(
        (original_values != df[column]).sum()
    )

log_quality(
    "Leading/trailing spaces",
    f"{whitespace_changes} text cells had unnecessary spaces",
    whitespace_changes,
    "Remove leading and trailing spaces",
    0,
    "Cleaned" if whitespace_changes > 0 else "No issue found"
)


# ==========================================
# 8. CHECK EMPTY TEXT RESPONSES
# ==========================================

empty_text_before = int(
    df.select_dtypes(include=["object"])
    .apply(lambda col: col.str.strip().eq("").sum())
    .sum()
)

# Convert blank text responses to missing values
for column in df.select_dtypes(include=["object"]).columns:
    df[column] = df[column].replace(r"^\s*$", np.nan, regex=True)

empty_text_after = int(
    df.select_dtypes(include=["object"])
    .apply(lambda col: col.str.strip().eq("").sum())
    .sum()
)

log_quality(
    "Empty text responses",
    f"{empty_text_before} blank text cells identified",
    empty_text_before,
    "Convert blank text cells to missing values",
    empty_text_after,
    "Cleaned" if empty_text_before > 0 else "No issue found"
)


# ==========================================
# 9. CHECK NUMERICAL DATA
# ==========================================

numeric_columns = df.select_dtypes(include=["number"]).columns

for column in numeric_columns:

    invalid_count = int(
        df[column].isin([np.inf, -np.inf]).sum()
    )

    log_quality(
        f"Invalid numerical values: {column}",
        f"{invalid_count} infinite values identified",
        invalid_count,
        "Flag for investigation; do not automatically delete",
        invalid_count,
        "Review required" if invalid_count > 0 else "No issue found"
    )


# ==========================================
# 10. CHECK FINAL MISSING VALUES
# ==========================================

missing_after = int(df.isnull().sum().sum())

log_quality(
    "Final missing values",
    f"{missing_after} missing cells remain",
    missing_after,
    "Retain missing values for documented statistical handling",
    missing_after,
    "Review required" if missing_after > 0 else "No issue found"
)


# ==========================================
# 11. CHECK FINAL DUPLICATES
# ==========================================

final_duplicates = int(df.duplicated().sum())

log_quality(
    "Final duplicate records",
    f"{final_duplicates} duplicate rows remain",
    final_duplicates,
    "Verify that no exact duplicate rows remain",
    final_duplicates,
    "Review required" if final_duplicates > 0 else "No issue found"
)


# ==========================================
# 12. SAVE CLEANED DATASET
# ==========================================

df.to_csv(output_path, index=False)


# ==========================================
# 13. SAVE QUALITY LOG
# ==========================================

quality_df = pd.DataFrame(quality_log)

quality_df.to_csv(quality_log_path, index=False)


# ==========================================
# 14. FINAL REPORT
# ==========================================

print("\n===================================")
print("DATA CLEANING SUMMARY")
print("===================================")

print("Original records:", initial_rows)
print("Final records:", len(df))
print("Records removed:", initial_rows - len(df))
print("Original columns:", len(original_df.columns))
print("Final columns:", len(df.columns))

print("\nQUALITY LOG")
print(quality_df.to_string(index=False))

print("\nFILES SAVED SUCCESSFULLY")
print("Cleaned dataset:", output_path)
print("Quality log:", quality_log_path)
