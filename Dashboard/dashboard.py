import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Judul aplikasi
st.title("Sales and Customer Analysis Dashboard")
st.write("This dashboard provides insights into sales performance, customer demographics, and product preferences.")

# Tentukan path ke file CSV
file_path = "Dashboard/all_data.csv"  # Path relatif ke file all_data.csv

# Cek apakah file ada
if os.path.exists(file_path):
    # Load the data
    all_df = pd.read_csv(file_path)

    # Sidebar untuk filter
    st.sidebar.header("Filters")
    product_type = st.sidebar.multiselect("Select Product Type", options=all_df['product_type'].unique(), default=all_df['product_type'].unique())
    start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(all_df['order_date']).min())
    end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(all_df['order_date']).max())

    # Memastikan format tanggal konsisten
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data berdasarkan pilihan
    filtered_df = all_df[(all_df['product_type'].isin(product_type)) &
                          (pd.to_datetime(all_df['order_date']) >= start_date) &
                          (pd.to_datetime(all_df['order_date']) <= end_date)]

    # Mengonversi 'order_date' ke datetime jika belum
    filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])

    # Menetapkan 'order_date' sebagai indeks
    filtered_df.set_index('order_date', inplace=True)

    # Bagian 1: Kinerja Penjualan
    st.subheader("Sales Performance and Revenue")
    monthly_orders_df = filtered_df.resample('M').agg({
        'order_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()

    # Memplot data penjualan
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders_df['order_date'], monthly_orders_df['order_id'], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Number of Orders per Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Orders")
    st.pyplot(plt)

    # Memplot data pendapatan
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders_df['order_date'], monthly_orders_df['total_price'], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Total Revenue per Month")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    st.pyplot(plt)

    # Bagian 2: Produk Terbaik dan Terburuk
    st.subheader("Top and Bottom Performing Products")

    # Mendapatkan produk teratas dan terbawah
    top_products = filtered_df.groupby("product_name")['quantity_x'].sum().sort_values(ascending=False).head(5)
    bottom_products = filtered_df.groupby("product_name")['quantity_x'].sum().sort_values().head(5)

    fig, ax = plt.subplots(1, 2, figsize=(15, 5))
    sns.barplot(x=top_products.values, y=top_products.index, ax=ax[0], palette="Blues_d")
    ax[0].set_title("Top Performing Products")
    sns.barplot(x=bottom_products.values, y=bottom_products.index, ax=ax[1], palette="Reds_d")
    ax[1].set_title("Bottom Performing Products")
    st.pyplot(fig)

    # Bagian 3: Demografi Pelanggan
    st.subheader("Customer Demographics")

    # Distribusi gender
    gender_distribution = filtered_df.groupby("gender")['customer_id'].nunique().reset_index()
    st.bar_chart(gender_distribution.set_index("gender"))

    # Distribusi kelompok usia
    age_group_distribution = filtered_df.groupby("age_group")['customer_id'].nunique().reset_index()
    st.bar_chart(age_group_distribution.set_index("age_group"))

    # Distribusi negara bagian
    state_distribution = filtered_df.groupby("state")['customer_id'].nunique().reset_index()
    st.bar_chart(state_distribution.set_index("state"))

    # Analisis RFM
    st.subheader("RFM Analysis")

    # Menghitung metrik RFM
    rfm_df = all_df.groupby('customer_id').agg({
        'order_date': 'max',
        'order_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()

    # Menghitung recency
    rfm_df['recency'] = (pd.to_datetime(all_df['order_date'].max()) - pd.to_datetime(rfm_df['order_date'])).dt.days

    # Memplot pelanggan teratas berdasarkan recency, frequency, dan monetary
    fig, ax = plt.subplots(1, 3, figsize=(18, 5))

    # Pelanggan Teratas berdasarkan Recency
    top_recency = rfm_df.sort_values(by='recency', ascending=True).head(5)
    sns.barplot(x=top_recency['recency'], y=top_recency['customer_id'], ax=ax[0], palette='Blues_d')
    ax[0].set_title("Top 5 Customers by Recency")

    # Pelanggan Teratas berdasarkan Frequency
    top_frequency = rfm_df.sort_values(by='order_id', ascending=False).head(5)
    sns.barplot(x=top_frequency['order_id'], y=top_frequency['customer_id'], ax=ax[1], palette='Greens_d')
    ax[1].set_title("Top 5 Customers by Frequency")

    # Pelanggan Teratas berdasarkan Monetary Value
    top_monetary = rfm_df.sort_values(by='total_price', ascending=False).head(5)
    sns.barplot(x=top_monetary['total_price'], y=top_monetary['customer_id'], ax=ax[2], palette='Reds_d')
    ax[2].set_title("Top 5 Customers by Monetary Value")
    st.pyplot(fig)

else:
    st.error(f"File '{file_path}' not found. Please upload it.")
