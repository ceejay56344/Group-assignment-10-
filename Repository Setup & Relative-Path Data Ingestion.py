
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define relative paths anchored to the project root
ROOT_DIR = Path(__file__).resolve().parent.parent if "__file__" in globals() else Path("..").resolve()
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "tertiary_student_food_insecurity_59_responses-v3.xlsx"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
OUTPUTS_DIR = ROOT_DIR / "outputs"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Load original digital export without modifying the source file
raw_df = pd.read_excel(RAW_DATA_PATH, sheet_name="Survey Responses")
print(f"Loaded raw dataset: {raw_df.shape[0]} rows x {raw_df.shape[1]} columns")

# Initialize quality audit log list
quality_log = []

def log_check(step_id, check_name, issue_found, rule_applied, before_count, after_count):
    """Records every inspection rule and before/after count, even when 0 issues exist."""
    quality_log.append({
        "Step": step_id,
        "Check_Category": check_name,
        "Issue_Description": issue_found,
        "Handling_Rule": rule_applied,
        "Count_Before": before_count,
        "Count_After": after_count
    })

# Standardize column names to snake_case for programmatic checks
df = raw_df.copy()
df.columns = [str(c).strip().lower() for c in df.columns]
