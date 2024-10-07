import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the data
st.title("Sales and Customer Analysis Dashboard")
st.write("This dashboard provides insights into sales performance, customer demographics, and product preferences.")

# Check if the file exists
all_df = pd.read_csv("all_data.csv")

if not os.path.exists(file_path):
    st.error(f"File '{file_path}' not found. Please upload it.")
else:
    # Load the data
    all_df = pd.read_csv(file_path)

    # Sidebar for filtering
    st.sidebar.header("Filters")
    product_type = st.sidebar.multiselect("Select Product Type", options=all_df['product_type'].unique(), default=all_df['product_type'].unique())
    start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(all_df['order_date']).min())
    end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(all_df['order_date']).max())

    # Ensure consistent date formats
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the data based on selections
    filtered_df = all_df[(all_df['product_type'].isin(product_type)) &
                          (pd.to_datetime(all_df['order_date']) >= start_date) &
                          (pd.to_datetime(all_df['order_date']) <= end_date)]

    # Convert 'order_date' to datetime if it’s not already
    filtered_df['order_date'] = pd.to_datetime(filtered_df['order_date'])

    # Set 'order_date' as the index
    filtered_df.set_index('order_date', inplace=True)

    # Section 1: Sales Performance
    st.subheader("Sales Performance and Revenue")
    monthly_orders_df = filtered_df.resample('M').agg({
        'order_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()

    # Plotting sales data
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders_df['order_date'], monthly_orders_df['order_id'], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Number of Orders per Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Orders")
    st.pyplot(plt)

    # Plot revenue data
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders_df['order_date'], monthly_orders_df['total_price'], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Total Revenue per Month")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    st.pyplot(plt)

    # Section 2: Top and Bottom Performing Products
    st.subheader("Top and Bottom Performing Products")

    # Get top and bottom products
    top_products = filtered_df.groupby("product_name")['quantity_x'].sum().sort_values(ascending=False).head(5)
    bottom_products = filtered_df.groupby("product_name")['quantity_x'].sum().sort_values().head(5)

    fig, ax = plt.subplots(1, 2, figsize=(15, 5))
    sns.barplot(x=top_products.values, y=top_products.index, ax=ax[0], palette="Blues_d")
    ax[0].set_title("Top Performing Products")
    sns.barplot(x=bottom_products.values, y=bottom_products.index, ax=ax[1], palette="Reds_d")
    ax[1].set_title("Bottom Performing Products")
    st.pyplot(fig)

    # Section 3: Customer Demographics
    st.subheader("Customer Demographics")

    # Gender distribution
    gender_distribution = filtered_df.groupby("gender")['customer_id'].nunique().reset_index()
    st.bar_chart(gender_distribution.set_index("gender"))

    # Age group distribution
    age_group_distribution = filtered_df.groupby("age_group")['customer_id'].nunique().reset_index()
    st.bar_chart(age_group_distribution.set_index("age_group"))

    # State distribution
    state_distribution = filtered_df.groupby("state")['customer_id'].nunique().reset_index()
    st.bar_chart(state_distribution.set_index("state"))

    # RFM Analysis
    st.subheader("RFM Analysis")

    # Calculate RFM metrics
    rfm_df = all_df.groupby('customer_id').agg({
        'order_date': 'max',
        'order_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()

    # Calculate recency
    rfm_df['recency'] = (pd.to_datetime(all_df['order_date'].max()) - pd.to_datetime(rfm_df['order_date'])).dt.days

    # Plot top 5 customers by recency, frequency, and monetary
    fig, ax = plt.subplots(1, 3, figsize=(18, 5))

    # Top 5 Customers by Recency
    top_recency = rfm_df.sort_values(by='recency', ascending=True).head(5)
    sns.barplot(x=top_recency['recency'], y=top_recency['customer_id'], ax=ax[0], palette='Blues_d')
    ax[0].set_title("Top 5 Customers by Recency")

    # Top 5 Customers by Frequency
    top_frequency = rfm_df.sort_values(by='order_id', ascending=False).head(5)
    sns.barplot(x=top_frequency['order_id'], y=top_frequency['customer_id'], ax=ax[1], palette='Greens_d')
    ax[1].set_title("Top 5 Customers by Frequency")

    # Top 5 Customers by Monetary Value
    top_monetary = rfm_df.sort_values(by='total_price', ascending=False).head(5)
    sns.barplot(x=top_monetary['total_price'], y=top_monetary['customer_id'], ax=ax[2], palette='Reds_d')
    ax[2].set_title("Top 5 Customers by Monetary Value")
    st.pyplot(fig)
