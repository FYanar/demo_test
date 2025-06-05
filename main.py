

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

# Excel dosyasını oku
file_path = "/mnt/data/test4.xlsx"
df = pd.read_excel(file_path, sheet_name="Sayfa1")
df.columns = df.columns.str.strip()
df['Organism_Label'] = df['OrganismIdentity']
df['Source_Label'] = df['Source']
df_clean = df.applymap(lambda x: x.strip().upper() if isinstance(x, str) else x)

# Kategoriler
antibiotics_cols = ['TE', 'FEP', 'SXT', 'PTZ', 'CAZ', 'GM', 'AMC', 'CTX', 'C', 'AMP', 'CRO', 'MEM', 'CIP', 'FOX', 'CZ', 'AK']
resist_mech_cols = ['Carbapenemases', 'ESBL']
resist_genes_cols = ['Sul1', 'Sul2', 'tetA,tetB', 'qnrA,qnrB,qnrS', 'AmpC', 'blaTEM', 'blaCTX-M', 'bla-SHV', 'NDM', 'KPC', 'VIM', 'OXA-48', 'IMP']

# Kodlama fonksiyonları
def recode_antibiotics(val):
    val = str(val).strip().upper()
    if val == 'R': return 5
    elif val == 'I': return 4
    elif val == 'S': return 3
    return np.nan

def recode_mech(val):
    val = str(val).strip().upper()
    if val in ['POS', 'POSITIVE']: return 2
    return 1

def recode_genes(val):
    val = str(val).strip().lower()
    if val in ['present', 'positive']: return 9
    return 8

# Kodlama uygulanıyor
ab_part = df_clean[antibiotics_cols].applymap(recode_antibiotics)
mech_part = df_clean[resist_mech_cols].applymap(recode_mech)
gene_part = df_clean[resist_genes_cols].applymap(recode_genes)

# Veriler birleştirilip ters çevrilir
heatmap_data = pd.concat([ab_part, mech_part, gene_part], axis=1).astype(float)[::-1]
org_labels = df['Organism_Label'][::-1].tolist()
src_labels = df['Source_Label'][::-1].tolist()

# Sütun başlıkları
column_labels = antibiotics_cols + resist_mech_cols + resist_genes_cols
column_labels_cleaned = [col.strip() for col in column_labels]

# Renk paleti (güncel renkler)
cmap = ListedColormap([
    '#ffffff',  # 0: boş/NA
    '#ffffff',  # 1: Negative (white)
    '#6ac6eb',  # 2: Positive (light blue)
    '#31e838',  # 3: Susceptible (green)
    '#f5ed05',  # 4: Intermediate (yellow)
    '#fc052e',  # 5: Resistant (red)
    '#ffffff',  # 6
    '#ffffff',  # 7
    '#ffffff',  # 8: Absent
    '#2e2e2e',  # 9: Present (dark gray / anthracite)
])
bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 7.5, 8.5, 9.5]
norm = BoundaryNorm(bounds, cmap.N)

# Legend tanımı
legend_elements = [
    Patch(facecolor='none', edgecolor='none', label='W = Water'),
    Patch(facecolor='none', edgecolor='none', label='P = Produce'),
    Patch(facecolor='none', edgecolor='none', label='S = Surface'),
    Patch(facecolor='#fc052e', label='Resistant'),
    Patch(facecolor='#f5ed05', label='Intermediate'),
    Patch(facecolor='#31e838', label='Susceptible'),
    Patch(facecolor='#6ac6eb', label='Positive'),
    Patch(facecolor='#ffffff', edgecolor='#999999', label='Negative'),
    Patch(facecolor='#2e2e2e', label='Present'),
    Patch(facecolor='#ffffff', edgecolor='#999999', label='Absent'),
]

# Grafik çizimi
fig_width = 16
fig_height = max(6, len(org_labels) * 0.33)
fig, ax = plt.subplots(figsize=(fig_width, fig_height))

sns.heatmap(heatmap_data, ax=ax, cmap=cmap, linewidths=0.2,
            linecolor='#999999', cbar=False, norm=norm)

ax.set_xticks([])
ax.set_yticks([])

# Tür ve kaynak (bold)
for idx, (org, src) in enumerate(zip(org_labels, src_labels)):
    ax.text(-3.8, idx + 0.5, org, va='center', ha='left',
            fontsize=10, fontweight='bold', clip_on=False)
    ax.text(-0.5, idx + 0.5, src, va='center', ha='center',
            fontsize=10, fontweight='bold', clip_on=False)

# Başlıkları yukarıdan sabit mesafeyle, dikey ve bold şekilde yaz
for i, col in enumerate(column_labels_cleaned):
    ax.text(i + 0.5, -1, col,
            va='top',
            ha='center',
            fontsize=8,
            fontweight='bold',
            rotation=90,
            clip_on=False,
            rotation_mode='anchor')

# Legend ekle
plt.legend(handles=legend_elements, loc='lower center',
           bbox_to_anchor=(0.5, -0.02), frameon=False, ncol=4)

plt.tight_layout()

# PDF olarak kaydet
output_path = "/mnt/data/heatmap_headers_va_top_y_fixed.pdf"
plt.savefig(output_path, format='pdf', bbox_inches='tight')
plt.close()
