import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Fungsi untuk membaca data
@st.cache_data
def load_data():
    file_path = "all_data.csv"  # Pastikan file ini berada di direktori yang sama dengan dashboard.py
    if not os.path.exists(file_path):
        st.error(f"File '{file_path}' tidak ditemukan. Pastikan file ada di direktori yang benar.")
        return None
    return pd.read_csv(file_path)

# Memuat data
st.title("Dashboard Interaktif: Analisis Penyewaan Sepeda Berdasarkan Faktor Cuaca")
data = load_data()

# Menampilkan Dataframe
st.header("Data Penyewaan Sepeda")
st.dataframe(data)

# Sidebar untuk interaksi pengguna
st.sidebar.header("Filter Data")
temp_filter = st.sidebar.slider("Temperatur", float(data['temp'].min()), float(data['temp'].max()), (float(data['temp'].min()), float(data['temp'].max())))
humidity_filter = st.sidebar.slider("Kelembaban", float(data['humidity'].min()), float(data['humidity'].max()), (float(data['humidity'].min()), float(data['humidity'].max())))
windspeed_filter = st.sidebar.slider("Kecepatan Angin", float(data['windspeed'].min()), float(data['windspeed'].max()), (float(data['windspeed'].min()), float(data['windspeed'].max())))

# Filter Data
filtered_data = data[(data['temp'] >= temp_filter[0]) & (data['temp'] <= temp_filter[1]) &
                     (data['humidity'] >= humidity_filter[0]) & (data['humidity'] <= humidity_filter[1]) &
                     (data['windspeed'] >= windspeed_filter[0]) & (data['windspeed'] <= windspeed_filter[1])]

# Menampilkan data yang sudah difilter
st.subheader("Data Setelah Filter")
st.dataframe(filtered_data)

# Analisis Korelasi antara Faktor Cuaca dan Penyewaan Sepeda
st.header("Korelasi antara Faktor Cuaca dan Penyewaan Sepeda")
selected_columns = st.multiselect("Pilih variabel untuk korelasi", options=['temp', 'humidity', 'windspeed', 'total_count'], default=['temp', 'humidity', 'windspeed', 'total_count'])
correlation = filtered_data[selected_columns].corr()

# Menampilkan Korelasi dalam bentuk tabel
st.write(correlation)

# Visualisasi Korelasi
st.subheader("Heatmap Korelasi")
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlation, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# Visualisasi tambahan
st.subheader("Tren Penyewaan Sepeda Berdasarkan Faktor Cuaca")

# Pilihan untuk jenis grafik
chart_type = st.selectbox("Pilih tipe grafik", ["Line Chart", "Scatter Plot", "Histogram"])

# Line Chart
if chart_type == "Line Chart":
    st.line_chart(filtered_data[['temp', 'total_count']])

# Scatter Plot
elif chart_type == "Scatter Plot":
    x_axis = st.selectbox("Pilih variabel X untuk Scatter Plot", options=selected_columns, index=0)
    y_axis = st.selectbox("Pilih variabel Y untuk Scatter Plot", options=selected_columns, index=3)
    fig2, ax2 = plt.subplots()
    sns.scatterplot(data=filtered_data, x=x_axis, y=y_axis, ax=ax2)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    st.pyplot(fig2)

# Histogram
elif chart_type == "Histogram":
    hist_variable = st.selectbox("Pilih variabel untuk histogram", options=selected_columns, index=0)
    fig3, ax3 = plt.subplots()
    sns.histplot(filtered_data[hist_variable], kde=True, ax=ax3)
    ax3.set_xlabel(hist_variable)
    ax3.set_ylabel("Frekuensi")
    st.pyplot(fig3)

# Perbandingan Distribusi
st.subheader("Distribusi Jumlah Penyewaan Sepeda Berdasarkan Variabel Cuaca")
fig4, ax4 = plt.subplots()
sns.boxplot(data=filtered_data, x='temp', y='total_count', ax=ax4)
plt.xlabel("Temperatur")
plt.ylabel("Jumlah Penyewaan Sepeda")
st.pyplot(fig4)
