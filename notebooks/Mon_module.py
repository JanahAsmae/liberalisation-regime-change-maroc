import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

PERIODE_BANDS = [
    (2010, 2017, '#DBEAFE', 'Avant'),
    (2018, 2020, '#FEF3C7', 'Transition'),
    (2021, 2025, '#D1FAE5', 'Après'),
]

def add_bands(ax, is_date=True):
    for start, end, color, label in PERIODE_BANDS:
        if is_date:
            ax.axvspan(pd.Timestamp(f'{start}-01-01'),
                       pd.Timestamp(f'{end}-12-31'),
                       color=color, alpha=0.4, zorder=0)
        else:
            ax.axvspan(start, end + 0.9,
                       color=color, alpha=0.4, zorder=0)
    ax.axvline(
        pd.Timestamp('2018-01-15') if is_date else 2018,
        color='#DC2626', linewidth=1.2,
        linestyle='--', zorder=5
    )

def legend_periodes():
    return [
        mpatches.Patch(facecolor='#DBEAFE', label='Avant (2010–2017)'),
        mpatches.Patch(facecolor='#FEF3C7', label='Transition (2018–2020)'),
        mpatches.Patch(facecolor='#D1FAE5', label='Après (2021–2025)'),
        plt.Line2D([0],[0], color='#DC2626',
                   linestyle='--', label='Réforme 2018'),
    ]