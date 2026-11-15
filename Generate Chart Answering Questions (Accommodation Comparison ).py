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
