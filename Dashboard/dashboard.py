import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Judul dan deskripsi dashboard
st.title("Sales and Customer Analysis Dashboard")
st.write("This dashboard provides insights into sales performance, customer demographics, and product preferences.")

# Tentukan file_path
file_path = "Dashboard/all_data.csv"

# Cek apakah file ada
if not os.path.exists(file_path):
    st.error(f"File '{file_path}' tidak ditemukan. Silakan upload file yang sesuai.")
else:
    # Load the data
    all_df = pd.read_csv(file_path)

    # Tampilkan nama kolom untuk debugging
    st.write("Kolom yang tersedia dalam dataset:")
    st.write(all_df.columns)

    # Cek apakah 'product_type' atau kolom alternatif ada di dataset
    if 'product_type' in all_df.columns:
        filter_column = 'product_type'
    else:
        # Jika 'product_type' tidak ada, gunakan kolom lain yang relevan, misalnya 'category'
        # Anda bisa mengganti kolom 'category' sesuai dengan dataset Anda
        possible_columns = ['category', 'item_type', 'product_name']  # Kolom alternatif
        filter_column = None
        for col in possible_columns:
            if col in all_df.columns:
                filter_column = col
                break
        
        if filter_column:
            st.write(f"Menggunakan kolom '{filter_column}' untuk filter produk.")
        else:
            st.error("Tidak ada kolom yang sesuai untuk digunakan sebagai filter produk.")
            st.stop()

    # Sidebar untuk filter
    st.sidebar.header("Filters")
    product_type = st.sidebar.multiselect(f"Pilih {filter_column}", options=all_df[filter_column].unique(), default=all_df[filter_column].unique())
    start_date = st.sidebar.date_input("Tanggal Mulai", value=pd.to_datetime(all_df['order_date']).min())
    end_date = st.sidebar.date_input("Tanggal Selesai", value=pd.to_datetime(all_df['order_date']).max())

    # Pastikan format tanggal konsisten
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data berdasarkan pilihan
    filtered_df = all_df[(all_df[filter_column].isin(product_type)) &
                         (pd.to_datetime(all_df['order_date']) >= start_date) &
                         (pd.to_datetime(all_df['order_date']) <= end_date)]

    # Konversi 'order_date' ke datetime jika belum
    filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])

    # Set 'order_date' sebagai index
    filtered_df.set_index('order_date', inplace=True)

    # Bagian 1: Kinerja Penjualan
    st.subheader("Kinerja Penjualan dan Pendapatan")
    monthly_orders_df = filtered_df.resample('M').agg({
        'order_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()

    # Plotting data penjualan
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders_df['order_date'], monthly_orders_df['order_id'], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Jumlah Pesanan per Bulan")
    plt.xlabel("Bulan")
    plt.ylabel("Jumlah Pesanan")
    st.pyplot(plt)

    # Plot data pendapatan
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders_df['order_date'], monthly_orders_df['total_price'], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Total Pendapatan per Bulan")
    plt.xlabel("Bulan")
    plt.ylabel("Pendapatan")
    st.pyplot(plt)

    # Bagian 2: Produk Terbaik dan Terburuk
    st.subheader("Produk Terbaik dan Terburuk")

    # Dapatkan produk terbaik dan terburuk
    top_products = filtered_df.groupby("product_name")['quantity_x'].sum().sort_values(ascending=False).head(5)
    bottom_products = filtered_df.groupby("product_name")['quantity_x'].sum().sort_values().head(5)

    fig, ax = plt.subplots(1, 2, figsize=(15, 5))
    sns.barplot(x=top_products.values, y=top_products.index, ax=ax[0], palette="Blues_d")
    ax[0].set_title("Produk Terbaik")
    sns.barplot(x=bottom_products.values, y=bottom_products.index, ax=ax[1], palette="Reds_d")
    ax[1].set_title("Produk Terburuk")
    st.pyplot(fig)

    # Bagian 3: Demografi Pelanggan
    st.subheader("Demografi Pelanggan")

    # Distribusi gender
    gender_distribution = filtered_df.groupby("gender")['customer_id'].nunique().reset_index()
    st.bar_chart(gender_distribution.set_index("gender"))

    # Distribusi kelompok umur
    age_group_distribution = filtered_df.groupby("age_group")['customer_id'].nunique().reset_index()
    st.bar_chart(age_group_distribution.set_index("age_group"))

    # Distribusi wilayah
    state_distribution = filtered_df.groupby("state")['customer_id'].nunique().reset_index()
    st.bar_chart(state_distribution.set_index("state"))

    # Analisis RFM
    st.subheader("Analisis RFM")

    # Hitung metrik RFM
    rfm_df = all_df.groupby('customer_id').agg({
        'order_date': 'max',
        'order_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()

    # Hitung recency
    rfm_df['recency'] = (pd.to_datetime(all_df['order_date'].max()) - pd.to_datetime(rfm_df['order_date'])).dt.days

    # Plot 5 pelanggan teratas berdasarkan recency, frequency, dan monetary
    fig, ax = plt.subplots(1, 3, figsize=(18, 5))

    # 5 Pelanggan Teratas berdasarkan Recency
    top_recency = rfm_df.sort_values(by='recency', ascending=True).head(5)
    sns.barplot(x=top_recency['recency'], y=top_recency['customer_id'], ax=ax[0], palette='Blues_d')
    ax[0].set_title("5 Pelanggan Teratas berdasarkan Recency")

    # 5 Pelanggan Teratas berdasarkan Frequency
    top_frequency = rfm_df.sort_values(by='order_id', ascending=False).head(5)
    sns.barplot(x=top_frequency['order_id'], y=top_frequency['customer_id'], ax=ax[1], palette='Greens_d')
    ax[1].set_title("5 Pelanggan Teratas berdasarkan Frequency")

    # 5 Pelanggan Teratas berdasarkan Monetary Value
    top_monetary = rfm_df.sort_values(by='total_price', ascending=False).head(5)
    sns.barplot(x=top_monetary['total_price'], y=top_monetary['customer_id'], ax=ax[2], palette='Reds_d')
    ax[2].set_title("5 Pelanggan Teratas berdasarkan Monetary Value")
    st.pyplot(fig)
