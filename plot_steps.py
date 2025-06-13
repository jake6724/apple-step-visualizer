import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.ticker as mticker
import mplcursors

# Path to the sample data
input_path = "export.xml"

# Parse the XML and extract step data
records = []
tree = ET.parse(input_path)
root = tree.getroot()
for elem in root.findall("Record"):
    if elem.attrib.get("type") == "HKQuantityTypeIdentifierStepCount":
        start = elem.attrib.get("startDate")
        end = elem.attrib.get("endDate")
        value = int(elem.attrib.get("value"))
        records.append({
            "startDate": start,
            "endDate": end,
            "value": value
        })

# Create DataFrame
if not records:
    print("No step records found.")
    exit(1)
df = pd.DataFrame(records)
# Convert endDate to datetime
# Apple Health format: '2025-06-08 17:24:06 -0400'
df["endDate"] = pd.to_datetime(df["endDate"], errors="coerce")

# Group by date (ignore time) and sum values
# Create a new column for just the date
if not df.empty:
    df["date"] = df["endDate"].dt.date
    daily_totals = df.groupby("date")["value"].sum().reset_index()
else:
    print("No valid step records found.")
    exit(1)

# Calculate monthly averages
if not daily_totals.empty:
    daily_totals["year"] = pd.to_datetime(daily_totals["date"]).dt.year
    daily_totals["month"] = pd.to_datetime(daily_totals["date"]).dt.month
    monthly_avg = daily_totals.groupby(["year", "month"])['value'].mean().reset_index()
    # Create a datetime column for plotting
    monthly_avg["month_start"] = pd.to_datetime(monthly_avg["year"].astype(str) + '-' + monthly_avg["month"].astype(str) + '-01')
else:
    print("No valid daily totals found.")
    exit(1)

# Sort by month_start
dates = monthly_avg["month_start"]

plt.figure(figsize=(12, 6), facecolor="#0D1117", num="Apple Step Count Visualizer")
# Plot the line and points separately
plt.plot(dates, monthly_avg["value"], linestyle="-", color="#58A6FF")
scatter = plt.scatter(dates, monthly_avg["value"], color="#58A6FF", s=40, zorder=3)
plt.title("Average Daily Step Count Per Month", color="#C9D1D9")
plt.xlabel("Year", color="#C9D1D9")
plt.ylabel("Average Daily Step Count", color="#C9D1D9")
# Format y-axis ticks with commas
ax = plt.gca()
ax.set_facecolor("#161B22")
ax.tick_params(colors="#8B949E")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
# Set y-axis limits based on min and max of monthly averages
min_steps = 0
max_steps = monthly_avg["value"].max() + 1000
plt.ylim(min_steps, max_steps)
# Add medium padding to the left x-axis
left_pad = dates.min() - pd.DateOffset(months=1)
plt.xlim(left=left_pad)

# Add vertical dashed lines at the start of each year, except the first year
if not monthly_avg.empty:
    year_starts = monthly_avg.groupby("year")['month_start'].min()
    # Skip the first year
    for year_start in year_starts.iloc[1:]:
        plt.axvline(year_start, color="#30363D", linestyle="--", alpha=0.5)
    # Only include years with at least 3 months of data for the trend line
    months_per_year = monthly_avg.groupby("year")["month"].count().reset_index()
    valid_years = months_per_year[months_per_year["month"] >= 3]["year"]
    yearly_avg = monthly_avg[monthly_avg["year"].isin(valid_years)].groupby("year")["value"].mean().reset_index()
    yearly_avg["month_start"] = pd.to_datetime(yearly_avg["year"].astype(str) + '-01-01')
    if not yearly_avg.empty:
        plt.plot(yearly_avg["month_start"], yearly_avg["value"], color="#8B949E", linestyle="-", linewidth=2, marker="s", markersize=8, markerfacecolor="#8B949E", markeredgecolor="#8B949E", alpha=0.7, label="Yearly Trend")

# Add labels for the highest and lowest points
if not monthly_avg.empty:
    max_idx = monthly_avg["value"].idxmax()
    min_idx = monthly_avg["value"].idxmin()
    for idx in [max_idx, min_idx]:
        val = monthly_avg.loc[idx, "value"]
        date = monthly_avg.loc[idx, "month_start"]
        label = f"{val:,.0f}"
        month_str = pd.to_datetime(date).strftime('%b')
        # Place the label very close to the point
        va = 'bottom' if idx == max_idx else 'top'
        y_offset = 8 if idx == max_idx else -8
        plt.annotate(f"{label}\n{month_str}",
                     (date, val),
                     textcoords="offset points",
                     xytext=(0, y_offset),
                     ha='center', va=va,
                     fontsize=8, fontweight='normal', color='#C9D1D9')

# Add interactivity with custom hover behavior
fig = plt.gcf()
ax = plt.gca()

# Create annotation object but don't show it yet
annot = ax.annotate("", xy=(0,0), xytext=(10,10),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.5",
                            facecolor="#161B22",
                            edgecolor="#30363D",
                            alpha=0.9),
                    color="#C9D1D9",
                    fontsize=9)
annot.set_visible(False)

def hover(event):
    if event.inaxes == ax:
        cont, ind = scatter.contains(event)
        if cont:
            pos = scatter.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            
            # Get the current x-axis limits
            xlim = ax.get_xlim()
            # Calculate the position relative to the x-axis range
            x_range = xlim[1] - xlim[0]
            x_pos = pos[0]
            x_relative = (x_pos - xlim[0]) / x_range
            
            # If point is in the right 30% of the graph, flip the annotation to the left
            if x_relative > 0.7:
                annot.set_x(-10)  # Negative offset moves it to the left
            else:
                annot.set_x(10)   # Positive offset moves it to the right
                
            text = f"Month: {monthly_avg.iloc[ind['ind'][0]]['month_start'].strftime('%b %Y')}\n" \
                   f"Avg Steps: {monthly_avg.iloc[ind['ind'][0]]['value']:,.0f}"
            annot.set_text(text)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

plt.tight_layout()
plt.show() 