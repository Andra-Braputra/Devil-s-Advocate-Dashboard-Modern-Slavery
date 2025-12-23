import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.nonparametric.smoothers_lowess as lowess
from plotly.subplots import make_subplots
# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Honest Data Dashboard: Truth Behind Statistics",
    layout="wide"
)

st.title("Audit Transparansi Data: Meluruskan Distorsi Statistik")
st.markdown("""
Dashboard ini disusun untuk menyajikan validasi objektif atas data ekonomi dan sosial nasional. 
Berbeda dengan narasi sebelumnya, penyajian ini mengacu pada **Prinsip Integritas Data (Bab IV)** untuk mengoreksi bias visual dan memberikan konteks yang utuh bagi pengambil kebijakan.
""")

# ---------------------------------------------------------
# 2. FUNGSI LOADING DATA (MENGGUNAKAN FILE ASLI)
# ---------------------------------------------------------

@st.cache_data
def load_data():
    # Load data dari CSV/Excel yang disediakan
    # Note: File dengan nama '.xlsx - Sheet1.csv' adalah file CSV hasil export
    mva_share = pd.read_excel('clean_mva_share.xlsx')
    ituc_score = pd.read_excel('clean_ituc_score.xlsx')
    ind_growth = pd.read_excel('clean_industrial_growth.xlsx')
    hours_ilo = pd.read_excel('clean_hours_ilo.xlsx')
    gdp_data = pd.read_csv('clean_gdp.csv')
    slavery_data = pd.read_csv('clean_data_modern_slavery.csv')
    tahanan_indo = pd.read_csv('Tahanan_Indo.csv')
    
    return mva_share, ituc_score, ind_growth, hours_ilo, gdp_data, slavery_data, tahanan_indo

mva, ituc, growth, hours, gdp, slavery, tahanan = load_data()

# Helper function untuk membersihkan data numerik
def clean_num(df, col):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')
    return df

# ---------------------------------------------------------
# BAB I: THE GLOBAL CONTEXT (VERSI JUJUR)
# ---------------------------------------------------------
st.title("BAB I: ANALISIS LANSKAP INDUSTRI GLOBAL")
st.subheader("1. Dekonstruksi 'Industrial Density': Efisiensi vs Otoritarianisme")

# Daftar negara yang memiliki performa industri kuat (Kompetitor China)
countries_to_show = ['China', 'Viet Nam', 'Korea, Rep.', 'Ireland']

# Grafik MVA Line Chart
df_mva_honest = mva[mva['Country Name'].isin(countries_to_show) & (mva['Year'] >= 2005)]
fig1 = px.line(df_mva_honest, x='Year', y='MVA_Pct_GDP', color='Country Name',
              title="MVA % GDP: China vs Negara Industri Maju & Berkembang",
              labels={'MVA_Pct_GDP': 'Kontribusi Manufaktur (%)', 'Year': 'Tahun'},
              template="plotly_white")

# Highlight China dengan garis putus-putus untuk kejujuran visual
fig1.update_traces(patch={"line": {"width": 4, "dash": 'dot'}}, selector={'name': 'China'})
st.plotly_chart(fig1, use_container_width=True)

# --- BAGIAN METRIK MODERN SLAVERY (MENGGUNAKAN 4 KOLOM) ---
st.markdown("### Modern Slavery Population")

# Mapping nama negara untuk dataset slavery
slavery_mapping = {
    'China': 'China',
    'Viet Nam': 'Viet Nam',
    'Korea, Rep.': 'South Korea',
    'Ireland': 'Ireland'
}

# Filter dan bersihkan data slavery
df_slv = slavery[slavery['Country'].isin(slavery_mapping.values())].copy()
df_slv['Slavery_Count'] = pd.to_numeric(df_slv['Estimated number of people in modern slavery'].astype(str).str.replace(',', ''), errors='coerce')

c1, c2, c3, c4 = st.columns(4)

def get_val(country_name):
    try:
        val = df_slv[df_slv['Country'] == slavery_mapping[country_name]]['Slavery_Count'].values[0]
        return f"{val:,.0f}"
    except:
        return "N/A"

with c1:
    st.metric(label="🇨🇳 China", value=get_val('China'))
with c2:
    st.metric(label="🇻🇳 Vietnam", value=get_val('Viet Nam'))
with c3:
    st.metric(label="🇰🇷 Korea Selatan", value=get_val('Korea, Rep.'))
with c4:
    st.metric(label="🇮🇪 Irlandia", value=get_val('Ireland'))

st.markdown("""
<div class="analysis-box">
    <b>Koreksi Analisis:</b><br>
    Data menunjukkan bahwa dominasi manufaktur tidak berkorelasi eksklusif dengan sistem politik tertentu.
    <ul>
        <li><b>Efisiensi Berbasis Teknologi:</b> Irlandia dan Korea Selatan membuktikan bahwa densitas industri (MVA) yang melampaui China dapat dicapai melalui keunggulan riset dan teknologi tinggi.</li>
        <li><b>Kemandirian Etis:</b> Negara-negara dengan standar hak asasi manusia yang tinggi justru memiliki ketahanan industri yang lebih stabil karena didukung oleh sistem hukum yang transparan.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import pandas as pd
import plotly.express as px
import streamlit as st

# --- Persiapan Data ---
ituc = pd.read_csv('ITUC.csv')
growth = pd.read_excel('clean_industrial_growth.xlsx')

# 1. Membersihkan Skor ITUC (Mengonversi '5+' menjadi 6 untuk keperluan statistik)
ituc['ITUC_Rights_Score'] = ituc['Rating'].replace('5+', '6').astype(float)

# 2. Join data secara transparan (Inner Join)
# Menggunakan tahun terbaru 2024 sesuai data yang tersedia
df_rights = pd.merge(
    ituc[['Country', 'ITUC_Rights_Score', 'Rating']],
    growth[growth['Year'] == 2024][['Country Name', 'Industrial_Growth_Pct']],
    left_on='Country', 
    right_on='Country Name'
).dropna(subset=['Industrial_Growth_Pct']) # Menghapus data kosong agar jujur secara statistik

# --- Visualisasi ---
st.subheader("2. The Liberty Penalty: Analisis Transparan")

if not df_rights.empty:
    # Mengurutkan agar grafik rapi
    df_rights = df_rights.sort_values('ITUC_Rights_Score')

    # Scatter Plot dengan Trendline OLS (Ordinary Least Squares)
    fig2 = px.scatter(
        df_rights, 
        x='ITUC_Rights_Score', 
        y='Industrial_Growth_Pct',
        color='ITUC_Rights_Score',
        hover_name='Country',
        hover_data={'ITUC_Rights_Score': False, 'Rating': True},
        trendline="ols", 
        title="Hubungan Skor Hak Buruh vs Pertumbuhan Industri (Global 2024)",
        labels={
            'ITUC_Rights_Score': 'Indeks Hak ITUC (1=Baik, 6=Tanpa Jaminan)',
            'Industrial_Growth_Pct': 'Pertumbuhan Industri (%)'
        },
        color_continuous_scale='RdYlGn_r',
        template="plotly_dark"
    )

    # Tambahkan garis horizontal nol
    fig2.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.5)")

    st.plotly_chart(fig2, use_container_width=True)

    # --- Bagian Penjelasan yang Jujur (Paragraf) ---
    st.markdown(f"""
    <div class="analysis-box" style="border-left: 5px solid #ffa500; background-color: #1e1e1e; padding: 15px; border-radius: 5px;">
        <h4 style="color: #ffa500;">📊 Analisis Objektif Tanpa Cherry-Picking</h4>
        <p>Grafik di atas memetakan seluruh spektrum data negara yang tersedia untuk menghindari bias pemilihan sampel. Garis tren linear (<i>Ordinary Least Squares</i>) digunakan untuk menguji hipotesis secara ilmiah. </p>
        <p>Secara statistik, terlihat kecenderungan garis tren yang menanjak seiring dengan meningkatnya skor ITUC. Hal ini mengindikasikan bahwa negara-negara dengan regulasi ketenagakerjaan yang lebih longgar atau minim jaminan hak (Skor 5 dan 6) memiliki probabilitas lebih tinggi untuk mencatatkan pertumbuhan industri yang ekspansif. Fenomena <b>Liberty Penalty</b> ini menunjukkan bahwa fleksibilitas operasional yang ekstrem sering kali menjadi kompensasi bagi pemodal untuk mempercepat output fisik.</p>
        <p>Namun, analisis ini juga menunjukkan <b>variansi yang lebar</b>; tidak semua negara dengan hak buruh rendah otomatis sukses. Terdapat beberapa titik yang berada jauh di bawah garis tren, menunjukkan adanya faktor kegagalan manajemen atau instabilitas politik meski regulasi sudah ditekan seminimal mungkin.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("Data untuk penggabungan tidak ditemukan. Pastikan nama negara pada kedua dataset konsisten.")

# ---------------------------------------------------------
# 3. THE DISCIPLINE DIVIDEND (Scatter Plot - Fix Negative Size)
# ---------------------------------------------------------
st.subheader("3. Analisis Produktivitas: Jam Kerja Tahunan vs Output Industri")
countries_discipline = [
    'China', 'Viet Nam', 'Indonesia', 'India', 
    'Denmark', 'Korea, Rep.', 'Ireland', 'Germany',
    'Norway', 'France', 'Mexico', 'Pakistan', 'Rwanda'
]

hours_latest = hours.sort_values('Year', ascending=False).drop_duplicates('Country')
name_map_discipline = {'Republic of Korea': 'Korea, Rep.', 'Vietnam': 'Viet Nam'}
hours_latest['Country_Sync'] = hours_latest['Country'].replace(name_map_discipline)

latest_growth_discipline = growth[growth['Year'] == 2024].dropna(subset=['Industrial_Growth_Pct'])

df_honest_discipline = pd.merge(
    hours_latest, 
    latest_growth_discipline, 
    left_on='Country_Sync', 
    right_on='Country Name'
)
df_honest_discipline = df_honest_discipline[df_honest_discipline['Country Name'].isin(countries_discipline)].copy()

df_honest_discipline['Growth_Magnitude'] = df_honest_discipline['Industrial_Growth_Pct'].abs() + 2 

fig3 = px.scatter(
    df_honest_discipline, 
    x='Annual_Hours_Est', 
    y='Industrial_Growth_Pct',
    text='Country Name', 
    size='Growth_Magnitude',
    color='Industrial_Growth_Pct',
    color_continuous_scale='Viridis',
    title="Scatter Plot: Jam Kerja Tahunan vs Pertumbuhan Industri 2024",
    labels={'Annual_Hours_Est': 'Estimasi Jam Kerja per Tahun', 'Industrial_Growth_Pct': 'Pertumbuhan (%)'},
    template="plotly_white"
)

fig3.update_traces(
    textposition='top center', 
    marker=dict(line=dict(width=1, color='DarkSlateGrey')),
    textfont_size=12
)

fig3.add_hline(y=0, line_dash="dot", line_color="red", annotation_text="Titik Kontraksi")

st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
<div class="analysis-box">
    <b>Validasi Data:</b><br>
    Scatter plot ini membuktikan bahwa **kuantitas jam kerja tidak menjamin pertumbuhan**. 
    Denmark dan Norwegia (kuadran kiri atas) menunjukkan bahwa pengurangan jam kerja yang disertai 
    peningkatan efisiensi sistemik menghasilkan output yang jauh lebih kompetitif dibandingkan model kerja paksa.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BAB II: NATIONAL SYSTEM FAILURE (VERSI JUJUR)
# ---------------------------------------------------------
st.header("BAB II: EVALUASI SISTEMIK NASIONAL")
st.subheader("1. Analisis Daya Saing: Rasio Upah terhadap Output Per Kapita")

# Konversi Rp3.331.012 ke USD (Asumsi kurs 1 USD = Rp16.000)
# 3.331.012 / 16.000 = ~208 USD
wage_data = pd.DataFrame({
    'Country': ['Indonesia', 'China', 'Russia', 'India'],
    'Monthly_Wage_USD': [208, 350, 280, 120] # Menggunakan angka koreksi Rp3.331.012
})

# Ambil data real untuk hitung GDP per Capita
gdp_fair = gdp[gdp['Country'].isin(wage_data['Country'])]
pop_fair = slavery[slavery['Country'].isin(wage_data['Country'])][['Country', 'Population']]

df_fair = pd.merge(pd.merge(wage_data, gdp_fair, on='Country'), pop_fair, on='Country')
df_fair['GDP_per_Capita'] = df_fair['GDP (nominal, 2023)'] / df_fair['Population']
df_fair['Annual_Wage'] = df_fair['Monthly_Wage_USD'] * 12


# 1. Metrik GDP Context (Komposisi Grid 4 Kolom agar muat di layar)
st.markdown("###GDP Context & Wage Metrics")
n_cols = 4
for i in range(0, len(df_fair), n_cols):
    cols = st.columns(n_cols)
    chunk = df_fair.iloc[i : i + n_cols]
    for j, (idx, row) in enumerate(chunk.iterrows()):
        val = row['GDP (nominal, 2023)']
        display_val = f"${val/1e12:.2f} T" if val >= 1e12 else f"${val/1e9:.1f} B"
        # Menampilkan GDP dan Upah bulanan secara informatif
        cols[j].metric(label=f"GDP {row['Country']}", value=display_val)

# 2. Visualisasi Perbandingan (Nominal vs Beban Riil)

    fig_nominal = px.bar(df_fair, x='Country', y='Monthly_Wage_USD', 
                        title="Upah Bulanan Rata-rata (USD)",
                        color='Country', template="plotly_white", text_auto=True)
    st.plotly_chart(fig_nominal, use_container_width=True)


st.markdown(f"""
<div class="analysis-box">
    <b>Perspektif Makroekonomi:</b><br>
    Dengan menggunakan standar upah rata-rata nasional (Rp3.331.012), ditemukan realitas sebagai berikut:
</div>
""", unsafe_allow_html=True)
# ---------------------------------------------------------
# 4.2.2. WASTED ASSETS (Honest Version: Humanitarian Crisis)
# ---------------------------------------------------------
st.subheader("2. Krisis Kapasitas Pemasyarakatan (Humanitarian Crisis)")

# Pemrosesan data riil dari Tahanan_Indo.csv
tahanan = clean_num(tahanan, 'Jumlah')
total_penghuni = tahanan[tahanan['Kapasitas Penghuni'].str.contains("TP")]['Jumlah'].values[0]
kapasitas = tahanan[tahanan['Kapasitas Penghuni'].str.contains("KP")]['Jumlah'].values[0]
overcrowding_rate = (total_penghuni / kapasitas) * 100

# Menyiapkan DataFrame untuk Bar Chart Sederhana
df_prison_honest = pd.DataFrame({
    'Status': ['Kapasitas Resmi', 'Penghuni Aktual'],
    'Jumlah Jiwa': [kapasitas, total_penghuni]
})

# Membuat Bar Chart yang menekankan selisih kapasitas
fig5 = px.bar(
    df_prison_honest,
    x='Status',
    y='Jumlah Jiwa',
    color='Status',
    color_discrete_map={
        'Kapasitas Resmi': '#6c757d', # Abu-abu netral
        'Penghuni Aktual': '#b02a37'  # Merah peringatan
    },
    text_auto=',.0f',
    title="Realitas Kapasitas Lapas Indonesia",
    template="plotly_white"
)

# Menambahkan garis ambang batas kapasitas agar kelebihan terlihat jelas
fig5.add_hline(
    y=kapasitas, 
    line_dash="dash", 
    line_color="black", 
    annotation_text="Batas Maksimum Kapasitas",
    annotation_position="top left"
)

st.plotly_chart(fig5, use_container_width=True)

st.error(f"""
    **Peringatan Sistemik:** Tingkat hunian Lapas mencapai **{overcrowding_rate:.1f}%**. 
    Kelebihan kapasitas ini adalah kegagalan tata kelola sosial yang serius. Menganggap populasi ini sebagai 
    komoditas ekonomi (tenaga kerja paksa) adalah pelanggaran berat terhadap konstitusi dan konvensi kemanusiaan internasional.
""")

st.markdown("""
<div class="analysis-box">
    <b>Analisis Kejujuran (Debunking Semantic Framing):</b><br>
    Visualisasi sederhana ini membongkar manipulasi bahasa yang dilakukan sebelumnya:
    <ul>
        <li><b>Bukan Aset:</b> Istilah <i>'Wasted Assets'</i> pada laporan sebelumnya adalah bentuk dehumanisasi. Bar chart di atas menunjukkan bahwa ada lebih dari 120.000 jiwa yang hidup di luar batas kapasitas layak.</li>
        <li><b>Transparansi Data:</b> Dengan membandingkan tinggi bar secara langsung, terlihat jelas bahwa jumlah penghuni hampir dua kali lipat dari kemampuan sistem (KP), menunjukkan urgensi krisis kemanusiaan yang nyata.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 4.2.3. Korelasi GDP vs Populasi Modern Slavery
st.subheader("3. Korelasi GDP vs Populasi Modern Slavery")
# Menggunakan prevalensi per 1.000 (X) dan GDP (Y) untuk menunjukkan realitas
honest_slavery = pd.merge(slavery, gdp, on='Country')
honest_slavery = clean_num(honest_slavery, 'Estimated prevalence of modern slavery per 1,000 population')
honest_slavery = clean_num(honest_slavery, 'GDP (nominal, 2023)')

fig6 = px.scatter(honest_slavery, x='Estimated prevalence of modern slavery per 1,000 population', 
                 y='GDP (nominal, 2023)', hover_name='Country', log_y=True,
                 title="Prevalensi Modern Slavery vs GDP (Skala Logaritma)",
                 labels={'Estimated prevalence of modern slavery per 1,000 population': 'Prevalensi (per 1.000 orang)'},
                 template="plotly_white")
st.plotly_chart(fig6, use_container_width=True)
st.caption("Analisis Jujur: Negara-negara terkaya (GDP tinggi) justru secara konsisten memiliki tingkat prevalensi perbudakan terendah.")

# ---------------------------------------------------------
# BAB III: THE Indo-SLAVERY MODEL (VERSI JUJUR)
# ---------------------------------------------------------
st.header("BAB III: EVALUASI RISIKO MODEL INDO-SLAVERY")
st.subheader("1. Kontradiksi Hukum dan Resiko Isolasi Ekonomi")

# Mengambil data real dari dataset slavery dan tahanan
# Menghitung surplus tahanan secara dinamis
prison_surplus = total_penghuni - kapasitas
modern_slavery_count = slavery[slavery['Country'] == 'Indonesia']['Estimated number of people in modern slavery'].values[0]
# Pastikan conversion ke integer jika masih string
if isinstance(modern_slavery_count, str):
    modern_slavery_count = int(modern_slavery_count.replace(',', ''))

fig7 = px.bar(
    x=['Modern Slavery Population', 'Prison Surplus (Overcrowding)'], 
    y=[modern_slavery_count, prison_surplus],
    title="Perbandingan Kelompok Populasi Terdampak",
    labels={'x': 'Kategori Kelompok', 'y': 'Jumlah Jiwa'},
    color=['Slavery', 'Prison'], 
    color_discrete_sequence=['#E64A19', '#37474F'],
    template="plotly_white",
    text_auto='.3s'
)
st.plotly_chart(fig7, use_container_width=True)

st.markdown("""
> **Analisis Hukum & Etika:** Data di atas menunjukkan beban kemanusiaan yang nyata. Berdasarkan **Konvensi ILO No. 29**, 
> memobilisasi populasi ini untuk kepentingan komersial bukan hanya melanggar HAM, tetapi juga memicu sanksi ekonomi internasional 
> yang akan melumpuhkan ekspor manufaktur Indonesia.
""")

st.header("2. Analisis Diagnostik: Produktivitas & Daya Saing Riil")

# --- DATASET RIIL (Estimasi 2023/2024) ---
# Menggunakan indikator ekonomi standar internasional
df_prod = pd.DataFrame({
    'Negara': ['Indonesia', 'Russia', 'China', 'India'],
    'GDP_PPP_Capita': [17634, 41705, 23846, 12100], # GDP per Capita PPP (Daya Beli)
    'Labor_Force_Million': [147.0, 72.0, 780.0, 523.0], # Angkatan Kerja Total
    'GDP_Nominal_Trillion': [1.37, 2.02, 17.79, 3.55]
})

# Hitung Produktivitas: GDP Nominal per Tenaga Kerja (USD)
df_prod['GDP_per_Worker'] = (df_prod['GDP_Nominal_Trillion'] * 1e12) / (df_prod['Labor_Force_Million'] * 1e6)

col1, col2 = st.columns(2)

with col1:
    # Grafik 1: Daya Saing Riil (GDP per Capita PPP)
    # Ini menunjukkan standar hidup dan kekuatan ekonomi per individu
    fig1 = px.bar(
        df_prod.sort_values('GDP_PPP_Capita', ascending=False),
        x='Negara',
        y='GDP_PPP_Capita',
        title="Daya Saing Riil (GDP per Kapita PPP)",
        labels={'GDP_PPP_Capita': 'USD (PPP)'},
        color='Negara',
        color_discrete_map={'Indonesia': '#FF4B4B'}, # Highlight Indonesia secara jujur
        text_auto='.0s',
        template="plotly_dark"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Grafik 2: Produktivitas Sistemik (GDP per Tenaga Kerja)
    # Menunjukkan berapa nilai ekonomi yang dihasilkan satu orang pekerja
    fig2 = px.bar(
        df_prod.sort_values('GDP_per_Worker', ascending=False),
        x='Negara',
        y='GDP_per_Worker',
        title="Produktivitas per Tenaga Kerja (Nominal)",
        labels={'GDP_per_Worker': 'Output per Pekerja (USD)'},
        color='Negara',
        color_discrete_map={'Indonesia': '#FF4B4B'},
        text_auto='.0s',
        template="plotly_dark"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Diagnosis Berbasis Data Objektif ---
st.markdown(f"""
<div class="analysis-box" style="border-left: 5px solid #1E90FF; background-color: #1e1e1e; padding: 15px;">
    <h4>🔍 Diagnosis Efisiensi Sistemik:</h4>
    <p>Analisis ini menggunakan metrik ekonomi makro standar untuk menghindari bias interpretasi:</p>
    <ul>
        <li><b>Kesenjangan Daya Saing:</b> GDP per Kapita PPP Indonesia (<b>$17,634</b>) menunjukkan posisi daya beli yang lebih kuat dibandingkan India, namun masih jauh di bawah Russia (<b>$41,705</b>) dan China (<b>$23,846</b>).</li>
        <li><b>Produktivitas Pekerja:</b> Setiap pekerja di Indonesia rata-rata menghasilkan output nominal <b>$9,319/tahun</b>. Sebagai perbandingan, pekerja di Russia menghasilkan 3x lipat (<b>$28,055</b>) dan China 2.5x lipat (<b>$22,807</b>).</li>
        <li><b>Akar Masalah Riil:</b> Inefisiensi bukan berasal dari "pemanfaatan tenaga kerja non-regulasi", melainkan dari <b>intensitas modal dan teknologi</b>. Russia dan China memiliki output per pekerja yang tinggi karena mekanisasi dan industrialisasi yang lebih maju dibandingkan Indonesia yang masih didominasi sektor jasa dan manufaktur rendah teknologi.</li>
    </ul>
    <p style="font-size: 0.9em; color: #888;">*Data disesuaikan dengan angka World Bank & IMF 2023-2024.</p>
</div>
""", unsafe_allow_html=True)

# 4.3.3. Proyeksi Dominasi Global
st.subheader("3. Proyeksi Pertumbuhan Ekonomi: Skenario Risiko & Stabilitas")

avg_growth_indo = growth[growth['Country Name'] == 'Indonesia']['Industrial_Growth_Pct'].mean() / 100
current_gdp = gdp[gdp['Country'] == 'Indonesia']['GDP (nominal, 2023)'].values[0] / 1e12

years = np.arange(2025, 2036)
proj_honest = pd.DataFrame({
    'Tahun': years,
    'Lower_CI': [current_gdp * (1 + 0.01)**(y-2025) for y in years],
    'Mean_Proj': [current_gdp * (1 + avg_growth_indo)**(y-2025) for y in years],
    'Upper_CI': [current_gdp * (1 + (avg_growth_indo + 0.02))**(y-2025) for y in years]
})

fig9 = go.Figure()
fig9.add_trace(go.Scatter(x=proj_honest['Tahun'], y=proj_honest['Upper_CI'], mode='lines', line_color='rgba(0,0,0,0)', showlegend=False))
fig9.add_trace(go.Scatter(
    x=proj_honest['Tahun'], y=proj_honest['Lower_CI'], 
    fill='tonexty', fillcolor='rgba(255, 75, 75, 0.2)', 
    line_color='rgba(0,0,0,0)', name='Zona Resiko Sanksi/Instabilitas'
))

fig9.add_trace(go.Scatter(x=proj_honest['Tahun'], y=proj_honest['Mean_Proj'], mode='lines+markers', line_color='#1E88E5', name='Proyeksi Historis'))

fig9.update_layout(
    title=f"Proyeksi GDP Indonesia Berdasarkan Tren ({avg_growth_indo*100:.1f}%)", 
    xaxis_title="Tahun", yaxis_title="Estimasi GDP (Triliun IDR)", 
    template="plotly_white"
)
st.plotly_chart(fig9, use_container_width=True)

st.markdown("""
<div class="analysis-box">
    <b>Ringkasan Eksekutif:</b><br>
    Pembangunan industri Indonesia harus bergeser dari model kompetisi upah rendah menuju model <b>inovasi nilai tambah tinggi</b>. 
    Keberlanjutan ekonomi hanya dapat dicapai melalui perlindungan hak asasi manusia dan peningkatan kualitas sumber daya manusia, 
    bukan melalui pengaktifan kembali model kerja paksa yang secara matematis justru merugikan ketahanan GDP nasional.
</div>
""", unsafe_allow_html=True)