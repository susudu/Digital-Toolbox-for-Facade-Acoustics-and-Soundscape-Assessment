import sys, json, pandas as pd, os
from fastapi.responses import JSONResponse
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from soundscapy.plotting import density_plot
import soundscapy.surveys as surveys
import seaborn as sns

# =====================================================
# GLOBAL NORMALIZATION MAXIMUM
# =====================================================
FIXED_MAX = 7.0   # freely change to 6, 6.5, 7, etc.

def process_file(file_path):
    df = pd.read_csv(file_path)
    summary = df.describe(include='all').to_dict()
    
    result = {
        "filename": os.path.basename(file_path),
        "processed_at": datetime.now().isoformat(),
        "summary": summary
    }
    
    os.makedirs("results", exist_ok=True)
    result_path = os.path.join("results", os.path.basename(file_path) + ".json")

    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Processed {file_path}, saved to {result_path}")
    
    return JSONResponse({
        "message": "File uploaded and saved successfully.",
        "processed_path": file_path,
        "saved_path": result_path
    })

# =====================================================
# CORE COMPUTATION
# =====================================================
def calculate_coordinates(e, v, p, ca, u, m, a, ch):
    """Compute Pleasantness (P) and Eventfulness (E) based on formula."""
    P = (p - a) + np.cos(np.deg2rad(45)) * (ca - ch) + np.cos(np.deg2rad(45)) * (v - m)
    E = (e - u) + np.cos(np.deg2rad(45)) * (ch - ca) + np.cos(np.deg2rad(45)) * (v - m)
    return P, E

def compute_P_E(locations):
    """Compute raw P and E values (no normalization)."""
    P_values, E_values = [], []
    for _, values in locations.items():
        e, v, p, ca, u, m, a, ch = values
        P, E = calculate_coordinates(e, v, p, ca, u, m, a, ch)
        P_values.append(P)
        E_values.append(E)
    return np.array(P_values), np.array(E_values)

# =====================================================
# FIXED-MAX SIGNED NORMALIZATION ( −1 to 1 )
# =====================================================
def signed_normalize_fixed(arr, fixed_max):
    """
    Normalize using a *fixed chosen maximum*:
      +fixed_max → +1.0
      -fixed_max → -1.0

    This ensures all datasets share the same scale.
    """
    arr = np.array(arr, dtype=float)
    norm_arr = arr / fixed_max

    # Limit values within [-1, 1] just in case
    norm_arr = np.clip(norm_arr, -1, 1)
    return norm_arr


# ===============================================================================
# PLOTTING FUNCTION (for normalized plot only) (AXIS FIXED TO ±1, ENHANCED STYLE)
# ===============================================================================
def plot_PE(ax, P_values, E_values):
    used_labels = set()
    for i, location in enumerate(locations.keys()):
        style = SCENE_STYLES.get(location, {'color': 'gray', 'marker': 'o'})
        label = SCENE_LABELS.get(location, location) if location not in used_labels else None
        used_labels.add(location)
        ax.scatter(
            P_values[i], E_values[i],
            marker=style['marker'],
            color=style['color'],
            label=label,
            s=45,
            alpha=0.8,
            edgecolor='black',
            linewidth=0.6,
            zorder=3
        )
        
    if TITLE == "VR Region View ~ Away – Pleasantness vs Eventfulness":
        # Build coordinates dictionary for easier access
        coordinates_dict = {
            scene: (P_values[i], E_values[i])
            for i, scene in enumerate(locations.keys())
        }

        # Define which points should be connected
        pairs_to_connect = [
            ('VR-E1-0v', 'VR-E1-0a'),
            ('VR-E1-1v', 'VR-E1-1a'),
            ('VR-E2-0v', 'VR-E2-0a'),
            ('VR-E2-1v', 'VR-E2-1a'),
            ('VR-W1-0v', 'VR-W1-0a'),
            ('VR-W1-1v', 'VR-W1-1a'),
            ('VR-W2-0v', 'VR-W2-0a'),
            ('VR-W2-1v', 'VR-W2-1a'),
        ]

        # Draw clean pair-to-pair lines
        for loc1, loc2 in pairs_to_connect:
            if loc1 in coordinates_dict and loc2 in coordinates_dict:
                P1, E1 = coordinates_dict[loc1]
                P2, E2 = coordinates_dict[loc2]
                ax.plot(
                    [P1, P2], [E1, E2],
                    color='gray',linestyle='-',linewidth=0.8,alpha=0.5,zorder=2)
    else :     
        # Connect paired points
        for i in range(0, len(P_values) - 1, 2):
            ax.plot([P_values[i], P_values[i + 1]], [E_values[i], E_values[i + 1]],
                    linestyle='-', color='gray', linewidth=0.8, alpha=0.5, zorder=2)

    # Fixed axis and quadrant labels
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xticks(np.arange(-1, 1.05, 0.25))
    ax.set_yticks(np.arange(-1, 1.05, 0.25))
    ax.tick_params(axis='both', labelsize=8)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=1)
    ax.set_aspect('equal', 'box')
    ax.axhline(0, color='black', linewidth=1.5, alpha=0.4, zorder=2)
    ax.axvline(0, color='black', linewidth=1.5, alpha=0.4, zorder=2)

    # Quadrant labels
    ax.text(-0.56, 0.56, 'Chaotic', color='gray', fontsize=9,
            ha='center', va='center', alpha=0.8, fontweight='bold')
    ax.text(0.56, 0.56, 'Vibrant', color='gray', fontsize=9,
            ha='center', va='center', alpha=0.8, fontweight='bold')
    ax.text(-0.56, -0.56, 'Monotonous', color='gray', fontsize=9,
            ha='center', va='center', alpha=0.8, fontweight='bold')
    ax.text(0.56, -0.56, 'Calm', color='gray', fontsize=9,
            ha='center', va='center', alpha=0.8, fontweight='bold')

    ax.set_title("Fixed-Max Normalized (−1 to 1)", fontsize=10, fontweight='bold')
    ax.set_xlabel("Pleasantness (P)", fontsize=9)
    ax.set_ylabel("Eventfulness (E)", fontsize=9)

def show_normalized_scene_plot(TITLE, P_norm, E_norm):
    fig, ax = plt.subplots(figsize=(4, 5))
    plt.suptitle(f"{TITLE}", fontsize=12, fontweight='bold', y=0.9)

    # Your existing custom plotting function
    plot_PE(ax, P_norm, E_norm)

    # Shared legend
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles, labels,
        title="Scenes",
        loc='upper left',
        bbox_to_anchor=(1.02, 0.82),
        prop={'size': 9}
    )

    plt.tight_layout(rect=[0, 0, 0, 0])
    plt.show()

if __name__ == "__main__":
    process_file(sys.argv[1])

    # =====================================================
    # CONFIGURATION
    # =====================================================
    excel_path = r"C:\Users\Rion Shimuchi\Documents\code\X1\data_X1\data_using\With_Average\East_combinedaverage_all.xlsx"
    TITLE = "East Region – Pleasantness vs Eventfulness"
    
    # =====================================================
    # LOAD DATA
    # =====================================================
    df = pd.read_excel(excel_path)
    df_areas = df.set_index("scene").T
    locations = {area: tuple(df_areas.loc[area]) for area in df_areas.index}
    
    # Compute raw values
    P_raw, E_raw = compute_P_E(locations)
    
    # Apply fixed normalization
    P_norm = signed_normalize_fixed(P_raw, FIXED_MAX)
    E_norm = signed_normalize_fixed(E_raw, FIXED_MAX)
    
    # =====================================================
    # SCENE STYLE & LABEL DEFINITIONS
    # =====================================================

    SCENE_STYLES = {
        'SW-E1-0': {'color': '#5da5c3', 'marker': 'o'},
        'SW-E1-1': {'color': '#3b5b92', 'marker': 'o'},
        'VR-E1-0v': {'color': '#9dcf75', 'marker': 'o'},
        'VR-E1-1v': {'color': '#66a61e', 'marker': 'o'},
        'VR-E1-0a': {'color': '#f6b686', 'marker': 'o'},
        'VR-E1-1a': {'color': '#e6ab02', 'marker': 'o'},
        'SW-E2-0': {'color': '#5da5c3', 'marker': 'X'},
        'SW-E2-1': {'color': '#3b5b92', 'marker': 'X'},
        'VR-E2-0v': {'color': '#9dcf75', 'marker': 'X'},
        'VR-E2-1v': {'color': '#66a61e', 'marker': 'X'},
        'VR-E2-0a': {'color': '#f6b686', 'marker': 'X'},
        'VR-E2-1a': {'color': '#e6ab02', 'marker': 'X'},
    }
    
    SCENE_LABELS = {
        'SW-E1-0':  'SW – façade still | noiseless',
        'SW-E1-1':  'SW – façade still | noise',
        'VR-E1-0v': 'VR – façade still | noiseless-view',
        'VR-E1-1v': 'VR – façade still | noise-view',
        'VR-E1-0a': 'VR – façade still | noiseless-away',
        'VR-E1-1a': 'VR – façade still | noise-away',
        'SW-E2-0':  'SW – façade move | noiseless',
        'SW-E2-1':  'SW – façade move | noise',
        'VR-E2-0v': 'VR – façade move | noiseless-view',
        'VR-E2-1v': 'VR – façade move | noise-view',
        'VR-E2-0a': 'VR – façade move | noiseless-away',
        'VR-E2-1a': 'VR – façade move | noise-away',
    }
    
    fig = show_normalized_scene_plot(TITLE,P_norm=P_norm,E_norm=E_norm)
