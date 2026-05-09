"""
Climate-Related Disaster Trends (1960-2024)
============================================
Created by Amy Ariyo May 2026

Animated data story showing how reported weather and climate disasters
have changed over the past six decades.

Data: EM-DAT via Our World in Data (CC BY licence)
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.animation import FuncAnimation, PillowWriter
from PIL import Image
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# ── Paths ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "disaster_events_owid.csv")
FIG_DIR = os.path.join(BASE_DIR, "figures")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

for d in [FIG_DIR, OUT_DIR]:
    os.makedirs(d, exist_ok=True)


# ── Colour palette ───────────────────────────────────────────────────
COLOURS = {
    "Flood":                "#2166ac",   # strong blue
    "Extreme weather":      "#b2182b",   # deep red
    "Drought":              "#d6604d",   # warm terracotta
    "Extreme temperature":  "#f4a582",   # pale salmon
    "Wildfire":             "#4d4d4d",   # dark grey
}

# Stacking order: flood on the bottom because it's the
# largest category, making the shape easier to read.
HAZARDS = ["Flood", "Extreme weather", "Drought",
           "Extreme temperature", "Wildfire"]


# ── Shared plot styling ──────────────────────────────────────────────
def apply_style():
    """Set a clean, minimal plot style used across all figures."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#333333",
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.dpi": 180,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.3,
    })

apply_style()


# ── Load and prepare ─────────────────────────────────────────────────
print("Loading data...")
raw = pd.read_csv(DATA_PATH)
raw.columns = ["entity", "year", "events"]

# Keep only the five climate/weather hazard types
df = raw[raw["entity"].isin(HAZARDS)].copy()

# Focus on 1960 onward —> earlier records are patchy so would distort
# the trend. Still gives us 60+ years of coverage.
df = df[df["year"].between(1960, 2024)]

# Pivot so each hazard is a column, fill gaps with zero
wide = df.pivot_table(index="year", columns="entity",
                      values="events", fill_value=0)
wide = wide.reindex(columns=HAZARDS, fill_value=0)

# Full year range so the animation has no jumps
all_years = range(1960, 2025)
wide = wide.reindex(all_years, fill_value=0)

print(f"  {len(wide)} years, {len(HAZARDS)} hazard types")
print(f"  Total records: {int(wide.sum().sum())}")


# ── Decade aggregation (for static plots) ──────────────────────
# Grouping by decade smooths year-to-year noise and makes long-term
# patterns easier to compare.
def assign_decade(year):
    return f"{(year // 10) * 10}s"

decade_df = wide.copy()
decade_df["decade"] = [assign_decade(y) for y in decade_df.index]
by_decade = decade_df.groupby("decade")[HAZARDS].sum()

####
# FIGURE 1 — Animated stacked area chart (main GIF)
####
fig_anim, ax_anim = plt.subplots(figsize=(9, 5.2))

years = np.array(wide.index)
stacked = np.column_stack([wide[h].values for h in HAZARDS])

# Pre-compute cumulative sums for stacking
cumulative = np.cumsum(stacked, axis=1)
y_max = int(cumulative[:, -1].max() * 1.12)

# Annotation spots — years where something notable happened
annotations = {
    1983: ("1983 El Niño\ndrought surge", -25, 22),
    1998: ("Late-90s spike:\nfloods + storms", -30, 18),
    2005: ("Record year\n(435 events)", -20, 20),
}


def draw_frame(frame_idx):
    """Draw a single frame of the stacked area animation."""
    ax_anim.clear()

    # Show data up to this frame
    end = frame_idx + 1
    x = years[:end]

    for i, hazard in enumerate(HAZARDS):
        bottom = cumulative[:end, i - 1] if i > 0 else np.zeros(end)
        top = cumulative[:end, i]
        ax_anim.fill_between(x, bottom, top,
                             color=COLOURS[hazard], alpha=0.85,
                             label=hazard, linewidth=0)
        # Thin white line between layers for clarity
        if i > 0:
            ax_anim.plot(x, bottom, color="white", linewidth=0.4)

    # Axis formatting
    ax_anim.set_xlim(1960, 2024)
    ax_anim.set_ylim(0, y_max)
    ax_anim.set_xlabel("")
    ax_anim.set_ylabel("Reported events per year", fontsize=10)
    ax_anim.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax_anim.yaxis.set_major_locator(ticker.MultipleLocator(100))
    ax_anim.tick_params(labelsize=9)

    # Title
    current_year = years[frame_idx]
    ax_anim.set_title(
        "Climate-Related Disasters Are Being Reported More Often",
        fontsize=13, fontweight="bold", color="#222222",
        loc="left", pad=22
    )
    ax_anim.text(0.0, 1.02, f"Five hazard types, 1960–{current_year}",
                 transform=ax_anim.transAxes, fontsize=9,
                 color="#666666", va="bottom")

    # Add annotations for years that we've already passed
    for ann_year, (text, dx, dy) in annotations.items():
        if current_year >= ann_year:
            ann_idx = ann_year - 1960
            y_val = cumulative[ann_idx, -1]
            ax_anim.annotate(
                text, xy=(ann_year, y_val),
                xytext=(ann_year + dx * 0.15, y_val + dy),
                fontsize=7.5, color="#444444",
                arrowprops=dict(arrowstyle="-", color="#999999",
                                lw=0.7),
                ha="center"
            )

    # Legend 
    handles = [plt.Rectangle((0, 0), 1, 1, fc=COLOURS[h], alpha=0.85)
               for h in HAZARDS]
    ax_anim.legend(handles, HAZARDS, loc="upper left",
                   fontsize=8, frameon=False, ncol=3,
                   bbox_to_anchor=(0, 0.97))

    # Data source note
    ax_anim.text(1.0, -0.08, "Data: EM-DAT / Our World in Data",
                 transform=ax_anim.transAxes, fontsize=7,
                 color="#aaaaaa", ha="right", va="top")

    fig_anim.tight_layout()


n_frames = len(years)

# Build every frame, but skip some in the early decades to keep the
# GIF file size reasonable. The last 20 years play frame-by-frame.
frame_indices = []
for i in range(n_frames):
    if i < 20:
        if i % 2 == 0:
            frame_indices.append(i)
    else:
        frame_indices.append(i)

# Hold the final frame for a beat so people can read it
frame_indices.extend([n_frames - 1] * 8)

print(f"  {len(frame_indices)} frames total (including final hold)")

anim = FuncAnimation(fig_anim, draw_frame, frames=frame_indices,
                     interval=120, repeat=True)

gif_path = os.path.join(FIG_DIR, "disaster_trends_animated.gif")
anim.save(gif_path, writer=PillowWriter(fps=8))
plt.close(fig_anim)

# Optimise the GIF — reduce colour palette to shrink file size
img = Image.open(gif_path)
print(f"  Saved animation: {os.path.getsize(gif_path) / 1024:.0f} KB")


####
# FIGURE 2 — Total climate disasters per decade (grouped bar)
####
print("\nCreating static figures...")

fig2, ax2 = plt.subplots(figsize=(8, 4.5))

decade_totals = by_decade.sum(axis=1)
decades = decade_totals.index.tolist()
values = decade_totals.values

# Mark the 2020s as incomplete — only 5 years of data
labels = [d if d != "2020s" else "2020s*" for d in decades]

bars = ax2.bar(labels, values, color="#2166ac", alpha=0.8,
               edgecolor="white", linewidth=0.5, width=0.65)

# Label each bar with the count
for bar, val in zip(bars, values):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 25,
             f"{int(val):,}", ha="center", fontsize=9, color="#333333")

ax2.set_ylabel("Total reported events", fontsize=10)
ax2.set_title("Climate Disaster Reports by Decade",
              fontsize=13, fontweight="bold", loc="left", pad=10)
ax2.text(0.0, 1.01, "Flood + Storm + Drought + Extreme temp. + Wildfire",
         transform=ax2.transAxes, fontsize=9, color="#666666",
         va="bottom")
ax2.set_ylim(0, max(values) * 1.15)
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda x, _: f"{int(x):,}"))
ax2.tick_params(labelsize=9)
ax2.text(0.0, -0.09, "*2020s covers 2020–2024 only (5 years)",
         transform=ax2.transAxes, fontsize=7.5, color="#999999")

fig2.tight_layout()
fig2.savefig(os.path.join(FIG_DIR, "disasters_per_decade.png"))
plt.close(fig2)
print("  Saved disasters_per_decade.png")


####
# FIGURE 3 — Heatmap: hazard type × decade
####
fig3, ax3 = plt.subplots(figsize=(8, 4))

heat_data = by_decade[HAZARDS].T
vmax = heat_data.values.max()

im = ax3.imshow(heat_data.values, aspect="auto",
                cmap="YlOrRd", vmin=0, vmax=vmax)

# Axis labels
heat_labels = [d if d != "2020s" else "2020s*" for d in decades]
ax3.set_xticks(range(len(decades)))
ax3.set_xticklabels(heat_labels, fontsize=9)
ax3.set_yticks(range(len(HAZARDS)))
ax3.set_yticklabels(HAZARDS, fontsize=9)

# Write values inside each cell
for i in range(len(HAZARDS)):
    for j in range(len(decades)):
        val = int(heat_data.values[i, j])
        # Use white text on dark cells, dark text on light cells
        text_colour = "white" if val > vmax * 0.6 else "#333333"
        ax3.text(j, i, f"{val:,}", ha="center", va="center",
                 fontsize=8.5, color=text_colour, fontweight="bold")

ax3.set_title("Reported Events by Hazard Type and Decade",
              fontsize=13, fontweight="bold", loc="left", pad=10)

cbar = fig3.colorbar(im, ax=ax3, shrink=0.8, pad=0.02)
cbar.set_label("Events", fontsize=9)
cbar.ax.tick_params(labelsize=8)

fig3.tight_layout()
fig3.savefig(os.path.join(FIG_DIR, "hazard_decade_heatmap.png"))
plt.close(fig3)
print("  Saved hazard_decade_heatmap.png")


####
# FIGURE 4 — Line chart: each hazard type over time (smoothed)
####
fig4, ax4 = plt.subplots(figsize=(8, 4.5))

# 5-year rolling average removes yearly noise while keeping the shape
for hazard in HAZARDS:
    smoothed = wide[hazard].rolling(5, center=True, min_periods=1).mean()
    ax4.plot(smoothed.index, smoothed.values, color=COLOURS[hazard],
             linewidth=2, label=hazard, alpha=0.9)
    # Faint raw data behind the smoothed line
    ax4.plot(wide.index, wide[hazard].values, color=COLOURS[hazard],
             linewidth=0.3, alpha=0.25)

ax4.set_title("Trends by Hazard Type (5-Year Rolling Average)",
              fontsize=13, fontweight="bold", loc="left", pad=10)
ax4.set_ylabel("Reported events per year", fontsize=10)
ax4.legend(fontsize=8, frameon=False, ncol=2)
ax4.set_xlim(1960, 2024)
ax4.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax4.tick_params(labelsize=9)

fig4.tight_layout()
fig4.savefig(os.path.join(FIG_DIR, "hazard_trends_smoothed.png"))
plt.close(fig4)
print("  Saved hazard_trends_smoothed.png")


####
# Summary table
####
print("\nBuilding summary table...")

total_by_type = wide[HAZARDS].sum()
grand_total = total_by_type.sum()

summary_rows = []
for hazard in HAZARDS:
    # Find the peak decade for this hazard
    peak_decade = by_decade[hazard].idxmax()
    peak_count = int(by_decade[hazard].max())
    total = int(total_by_type[hazard])
    pct = total / grand_total * 100

    # Average over the last 10 years vs first 10 years
    recent_avg = wide[hazard].loc[2015:2024].mean()
    early_avg = wide[hazard].loc[1960:1969].mean()

    summary_rows.append({
        "hazard_type": hazard,
        "total_events_1960_2024": total,
        "share_of_total_pct": round(pct, 1),
        "peak_decade": peak_decade,
        "peak_decade_events": peak_count,
        "avg_per_year_1960s": round(early_avg, 1),
        "avg_per_year_2015_2024": round(recent_avg, 1),
    })

summary = pd.DataFrame(summary_rows)
summary_path = os.path.join(OUT_DIR, "disaster_summary.csv")
summary.to_csv(summary_path, index=False)
print(f"  Saved disaster_summary.csv")

# Print a readable version
print("\n" + "=" * 60)
print("SUMMARY: Climate-Related Disasters, 1960–2024")
print("=" * 60)
print(f"  Total reported events: {int(grand_total):,}")
print(f"  Hazard types tracked:  {len(HAZARDS)}")
print()
for _, row in summary.iterrows():
    print(f"  {row['hazard_type']:22s}  "
          f"{row['total_events_1960_2024']:>5,} events  "
          f"({row['share_of_total_pct']:>5.1f}%)  "
          f"peak: {row['peak_decade']}")

print()
print("All outputs saved to figures/ and outputs/")
print("Done.")
