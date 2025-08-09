import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import ConnectionPatch

def render(filtered_df):
    st.subheader("Distribution of Property Types")
    type_counts = filtered_df["propertyType"].value_counts()
    labels = type_counts.index.tolist()
    sizes = type_counts.values
    total = sizes.sum()

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, _ = ax.pie(sizes, startangle=90, radius=1.2)
    ax.axis('equal')

    small_wedges = []
    small_angles = []
    small_labels = []
    small_percents = []

    for wedge, label, size in zip(wedges, labels, sizes):
        percent = size / total * 100
        angle = (wedge.theta2 + wedge.theta1) / 2
        x, y = np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))

        if percent >= 10:
            ax.text(x * 0.8, y * 0.8, f"{label}\n{percent:.1f}%", ha='center', va='center', fontsize=9)
        else:
            small_wedges.append((x, y))
            small_angles.append(angle)
            small_labels.append(label)
            small_percents.append(percent)

    if small_wedges:
        offset_ys = np.linspace(1, -1, len(small_wedges))
        for (x, y), label, percent, label_y in zip(small_wedges, small_labels, small_percents, offset_ys):
            label_x = 1.6 * np.sign(x)
            con = ConnectionPatch((x, y), (label_x, label_y), coordsA=ax.transData, coordsB=ax.transData,
                                  arrowstyle='-', lw=1, color='gray')
            ax.add_artist(con)
            ax.text(label_x, label_y, f"{label} ({percent:.1f}%)",
                    ha='left' if x >= 0 else 'right', va='center', fontsize=9)

    st.pyplot(fig)