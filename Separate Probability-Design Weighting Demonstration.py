
```python
# ==============================================================================
# STUDENT 8: Separate Simulated Probability-Design Weighting Demonstration
# ==============================================================================
# NOTE: Completely separate simulated dataset illustrating the proposed national
# stratified two-stage PPS design (independent of pilot survey counts).

sim_strata = pd.DataFrame({
    "stratum": [
        "Urban Universities",
        "Rural/Peri-Urban Universities",
        "Urban Polytechnics/Colleges",
        "Rural/Peri-Urban Polytechnics/Colleges"
    ],
    "N_h_total_students": [65000, 25000, 35000, 15000],  # Known national enrollment M_h
    "a_h_sampled_institutions": [4, 4, 4, 4],            # Stage 1 PSUs selected via PPS
    "b_hi_students_per_psu": [25, 25, 25, 25],           # Stage 2 SSUs selected systematically
    "sim_skipped_meal_rate": [0.52, 0.68, 0.60, 0.76]    # Simulated stratum prevalence
})

# Stage 1 & Stage 2 combined inclusion probability: pi_hij = (a_h * b_hi) / N_h
sim_strata["n_h_sample"] = sim_strata["a_h_sampled_institutions"] * sim_strata["b_hi_students_per_psu"]
sim_strata["inclusion_prob_pi"] = sim_strata["n_h_sample"] / sim_strata["N_h_total_students"]

# Design base weight: w_hij = 1 / pi_hij
sim_strata["base_weight_w"] = 1.0 / sim_strata["inclusion_prob_pi"]
sim_strata["est_affected_students"] = sim_strata["n_h_sample"] * sim_strata["sim_skipped_meal_rate"] * sim_strata["base_weight_w"]

# Compare Unweighted vs. Design-Weighted Proportion
unweighted_prop = (sim_strata["n_h_sample"] * sim_strata["sim_skipped_meal_rate"]).sum() / sim_strata["n_h_sample"].sum()
weighted_prop = sim_strata["est_affected_students"].sum() / (sim_strata["n_h_sample"] * sim_strata["base_weight_w"]).sum()

print("\n--- SEPARATE PROBABILITY WEIGHTING DEMONSTRATION (2c) ---")
print(sim_strata[["stratum", "N_h_total_students", "n_h_sample", "inclusion_prob_pi", "base_weight_w", "sim_skipped_meal_rate"]].to_string(index=False))
print(f"\nUnweighted Sample Proportion (Equal Stratum Allocation): {unweighted_prop:.3%}")
print(f"Design-Weighted Population Proportion:                  {weighted_prop:.3%}")
print("Methodological Note: Because rural/polytechnic strata were oversampled relative to enrollment,")
print("the unweighted proportion (64.0%) overstates national prevalence compared to the weighted estimate (58.7%).")
print("Under the national stratified multi-stage design, variance estimation must account for stratification,")
print("PSU clustering (DEFF > 1 via Taylor linearization or jackknife), and unequal weights rather than SRS formulas.")```python
# ==============================================================================
# STUDENT 8: Separate Simulated Probability-Design Weighting Demonstration
# ==============================================================================
# NOTE: Completely separate simulated dataset illustrating the proposed national
# stratified two-stage PPS design (independent of pilot survey counts).

sim_strata = pd.DataFrame({
    "stratum": [
        "Urban Universities",
        "Rural/Peri-Urban Universities",
        "Urban Polytechnics/Colleges",
        "Rural/Peri-Urban Polytechnics/Colleges"
    ],
    "N_h_total_students": [65000, 25000, 35000, 15000],  # Known national enrollment M_h
    "a_h_sampled_institutions": [4, 4, 4, 4],            # Stage 1 PSUs selected via PPS
    "b_hi_students_per_psu": [25, 25, 25, 25],           # Stage 2 SSUs selected systematically
    "sim_skipped_meal_rate": [0.52, 0.68, 0.60, 0.76]    # Simulated stratum prevalence
})

# Stage 1 & Stage 2 combined inclusion probability: pi_hij = (a_h * b_hi) / N_h
sim_strata["n_h_sample"] = sim_strata["a_h_sampled_institutions"] * sim_strata["b_hi_students_per_psu"]
sim_strata["inclusion_prob_pi"] = sim_strata["n_h_sample"] / sim_strata["N_h_total_students"]

# Design base weight: w_hij = 1 / pi_hij
sim_strata["base_weight_w"] = 1.0 / sim_strata["inclusion_prob_pi"]
sim_strata["est_affected_students"] = sim_strata["n_h_sample"] * sim_strata["sim_skipped_meal_rate"] * sim_strata["base_weight_w"]

# Compare Unweighted vs. Design-Weighted Proportion
unweighted_prop = (sim_strata["n_h_sample"] * sim_strata["sim_skipped_meal_rate"]).sum() / sim_strata["n_h_sample"].sum()
weighted_prop = sim_strata["est_affected_students"].sum() / (sim_strata["n_h_sample"] * sim_strata["base_weight_w"]).sum()

print("\n--- SEPARATE PROBABILITY WEIGHTING DEMONSTRATION (2c) ---")
print(sim_strata[["stratum", "N_h_total_students", "n_h_sample", "inclusion_prob_pi", "base_weight_w", "sim_skipped_meal_rate"]].to_string(index=False))
print(f"\nUnweighted Sample Proportion (Equal Stratum Allocation): {unweighted_prop:.3%}")
print(f"Design-Weighted Population Proportion:                  {weighted_prop:.3%}")
print("Methodological Note: Because rural/polytechnic strata were oversampled relative to enrollment,")
print("the unweighted proportion (64.0%) overstates national prevalence compared to the weighted estimate (58.7%).")
print("Under the national stratified multi-stage design, variance estimation must account for stratification,")
print("PSU clustering (DEFF > 1 via Taylor linearization or jackknife), and unequal weights rather than SRS formulas.")
