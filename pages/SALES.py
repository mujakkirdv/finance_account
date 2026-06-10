import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64

# --- Page Configuration ---
st.set_page_config(page_title="Financial App / SALES", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 32px;
        font-weight: bold;
        color: #2E86C1;
        margin-bottom: 10px;
    }
    .feature-card {
        background-color: #248787;
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        font-size: 16px;
        font-weight: 500;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }
    .executive-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    """Load and prepare the financial data"""
    try:
        df = pd.read_csv("data/cosmetics_sales.csv")
        
        # Parse OrderDate
        if 'OrderDate' in df.columns:
            df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
            df['date'] = df['OrderDate']
        
        # Ensure numeric columns
        numeric_cols = ['UnitPrice', 'Quantity', 'OrderValue', 'DiscountValue', 'SalesValue', 
                       'SalesReturn', 'CreditedAmount', 'Commission', 'Year', 'Day', 'NetSales', 'DueAmount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

# Date Range Filter
if 'OrderDate' in df.columns and len(df) > 0:
    min_date = df['OrderDate'].min().date()
    max_date = df['OrderDate'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        mask = (df['OrderDate'] >= pd.to_datetime(date_range[0])) & (df['OrderDate'] <= pd.to_datetime(date_range[1]))
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
else:
    df_filtered = df.copy()

# Executive Filter
if 'SalesName' in df_filtered.columns:
    executives = ['All'] + sorted(df_filtered['SalesName'].dropna().unique().tolist())
    selected_executive = st.sidebar.selectbox("Sales Executive", executives)
    if selected_executive != 'All':
        df_filtered = df_filtered[df_filtered['SalesName'] == selected_executive]

# Customer Filter
if 'CustomerName' in df_filtered.columns:
    customers = ['All'] + sorted(df_filtered['CustomerName'].dropna().unique().tolist())
    selected_customer = st.sidebar.selectbox("Customer", customers)
    if selected_customer != 'All':
        df_filtered = df_filtered[df_filtered['CustomerName'] == selected_customer]

# Product Category Filter
if 'ProductCategory' in df_filtered.columns:
    categories = ['All'] + sorted(df_filtered['ProductCategory'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Product Category", categories)
    if selected_category != 'All':
        df_filtered = df_filtered[df_filtered['ProductCategory'] == selected_category]

# --- Main Header ---
st.markdown("<div class='main-header'>💰 Sales Analytics Dashboard</div>", unsafe_allow_html=True)

# --- KPI Metrics Row ---
if len(df_filtered) > 0:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_sales = df_filtered['NetSales'].sum()
        st.metric("💰 Total Sales", f"{total_sales:,.2f}")
    
    with col2:
        total_customers = df_filtered['CustomerID'].nunique()
        st.metric("👥 Total Customers", f"{total_customers:,}")
    
    with col3:
        total_executives = df_filtered['SalesName'].nunique()
        st.metric("👔 Total Executives", f"{total_executives:,}")
    
    with col4:
        total_orders = df_filtered['InvoiceNo'].nunique()
        st.metric("📦 Total Orders", f"{total_orders:,}")
    
    with col5:
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        st.metric("⭐ Avg Order Value", f"{avg_order_value:,.2f}")

    # Secondary Metrics
    col6, col7, col8, col9, col10 = st.columns(5)
    
    with col6:
        total_discount = df_filtered['DiscountValue'].sum()
        st.metric("🎯 Total Discount", f"{total_discount:,.2f}")
    
    with col7:
        total_commission = df_filtered['Commission'].sum()
        st.metric("💵 Total Commission", f"{total_commission:,.2f}")
    
    with col8:
        total_due = df_filtered['DueAmount'].sum()
        st.metric("⚠️ Total Due", f"{total_due:,.2f}")
    
    with col9:
        total_return = df_filtered['SalesReturn'].sum()
        st.metric("🔄 Sales Return", f"{total_return:,.2f}")
    
    with col10:
        collection_rate = ((total_sales - total_due) / total_sales * 100) if total_sales > 0 else 0
        st.metric("✅ Collection Rate", f"{collection_rate:.1f}%")
else:
    st.warning("No data available for the selected filters")

# --- Tabs for Different Views ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Dashboard", 
    "👥 Customer Dashboard", 
    "📈 Executive Behavior", 
    "👤 Customer Behavior",
    "🏆 Top Performers"
])

# ================= TAB 1: EXECUTIVE DASHBOARD =================
with tab1:
    st.subheader("👔 Sales Executive Dashboard")
    
    if len(df_filtered) > 0 and 'SalesName' in df_filtered.columns:
        # Executive Performance Summary
        executive_summary = df_filtered.groupby('SalesName').agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Commission': 'sum',
            'DueAmount': 'sum'
        }).reset_index()
        
        executive_summary.columns = ['Executive', 'Total Sales', 'Orders', 'Customers', 'Commission', 'Due Amount']
        executive_summary['Avg Order Value'] = executive_summary['Total Sales'] / executive_summary['Orders']
        executive_summary = executive_summary.sort_values('Total Sales', ascending=False)
        
        # Display executive metrics
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            # Bar chart - Sales by Executive
            fig_exec_sales = px.bar(
                executive_summary,
                x='Executive',
                y='Total Sales',
                title="Sales by Executive",
                text='Total Sales',
                color='Total Sales',
                color_continuous_scale='Viridis'
            )
            fig_exec_sales.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_exec_sales.update_layout(height=400)
            st.plotly_chart(fig_exec_sales, use_container_width=True)
        
        with col_e2:
            # Scatter plot - Orders vs Sales
            fig_exec_scatter = px.scatter(
                executive_summary,
                x='Orders',
                y='Total Sales',
                size='Customers',
                text='Executive',
                title="Orders vs Sales (Size = Customers)",
                labels={'Orders': 'Number of Orders', 'Total Sales': 'Total Sales (BDT)'}
            )
            fig_exec_scatter.update_traces(textposition='top center')
            st.plotly_chart(fig_exec_scatter, use_container_width=True)
        
        # Executive detailed table
        st.subheader("📋 Executive Performance Details")
        st.dataframe(
            executive_summary.style.format({
                'Total Sales': '{:,.2f}',
                'Commission': '{:,.2f}',
                'Due Amount': '{:,.2f}',
                'Avg Order Value': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Download executive report
        csv_exec = executive_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Executive Report",
            data=csv_exec,
            file_name=f"executive_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No executive data available")

# ================= TAB 2: CUSTOMER DASHBOARD =================
with tab2:
    st.subheader("👥 Customer Dashboard")
    
    if len(df_filtered) > 0 and 'CustomerName' in df_filtered.columns:
        # Customer Summary
        customer_summary = df_filtered.groupby(['CustomerName', 'CustomerType']).agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'DueAmount': 'sum'
        }).reset_index()
        
        customer_summary.columns = ['Customer', 'Customer Type', 'Total Purchase', 'Orders', 'Due Amount']
        customer_summary = customer_summary.sort_values('Total Purchase', ascending=False)
        
        # Top 10 Customers
        st.subheader("🏆 Top 10 Customers by Purchase Value")
        top_customers = customer_summary.head(10)
        
        fig_top_customers = px.bar(
            top_customers,
            x='Total Purchase',
            y='Customer',
            orientation='h',
            title="Top 10 Customers",
            text='Total Purchase',
            color='Total Purchase',
            color_continuous_scale='Plasma'
        )
        fig_top_customers.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_top_customers.update_layout(height=500)
        st.plotly_chart(fig_top_customers, use_container_width=True)
        
        # Customer Type Distribution
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            customer_type_summary = df_filtered.groupby('CustomerType')['NetSales'].sum().reset_index()
            fig_customer_type = px.pie(
                customer_type_summary,
                values='NetSales',
                names='CustomerType',
                title="Sales by Customer Type",
                hole=0.3
            )
            st.plotly_chart(fig_customer_type, use_container_width=True)
        
        with col_c2:
            # Customer with due amounts
            due_customers = customer_summary[customer_summary['Due Amount'] > 0].head(10)
            if len(due_customers) > 0:
                fig_due = px.bar(
                    due_customers,
                    x='Due Amount',
                    y='Customer',
                    orientation='h',
                    title="Top 10 Customers with Due Amount",
                    color='Due Amount',
                    color_continuous_scale='Reds'
                )
                fig_due.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig_due, use_container_width=True)
        
        # Customer detailed table
        with st.expander("📋 View All Customer Details"):
            st.dataframe(
                customer_summary.style.format({
                    'Total Purchase': 'BDT{:,.2f}',
                    'Due Amount': 'BDT{:,.2f}'
                }),
                use_container_width=True
            )
    else:
        st.info("No customer data available")

# ================= TAB 3: EXECUTIVE BEHAVIOR =================
with tab3:
    st.subheader("📈 Executive Behavior Analysis")
    
    if len(df_filtered) > 0 and 'SalesName' in df_filtered.columns:
        # Monthly trend by executive
        if 'OrderDate' in df_filtered.columns:
            df_filtered['Month'] = df_filtered['OrderDate'].dt.strftime('%Y-%m')
            
            monthly_executive = df_filtered.groupby(['Month', 'SalesName'])['NetSales'].sum().reset_index()
            
            # Line chart - Executive performance over time
            fig_exec_trend = px.line(
                monthly_executive,
                x='Month',
                y='NetSales',
                color='SalesName',
                title="Executive Sales Trend Over Time",
                markers=True,
                labels={'NetSales': 'Sales (BDT)', 'Month': 'Month', 'SalesName': 'Executive'}
            )
            fig_exec_trend.update_layout(height=450)
            st.plotly_chart(fig_exec_trend, use_container_width=True)
        
        # Executive performance metrics
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            # Average order value by executive
            exec_avg_order = df_filtered.groupby('SalesName').agg({
                'NetSales': 'sum',
                'InvoiceNo': 'nunique'
            }).reset_index()
            exec_avg_order['Avg Order Value'] = exec_avg_order['NetSales'] / exec_avg_order['InvoiceNo']
            
            fig_avg_order = px.bar(
                exec_avg_order,
                x='SalesName',
                y='Avg Order Value',
                title="Average Order Value by Executive",
                text='Avg Order Value',
                color='Avg Order Value',
                color_continuous_scale='Teal'
            )
            fig_avg_order.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig_avg_order, use_container_width=True)
        
        with col_b2:
            # Commission vs Sales
            exec_commission = df_filtered.groupby('SalesName')[['NetSales', 'Commission']].sum().reset_index()
            
            fig_commission = px.bar(
                exec_commission,
                x='SalesName',
                y=['NetSales', 'Commission'],
                barmode='group',
                title="Sales vs Commission by Executive",
                labels={'value': 'Amount (BDT)', 'SalesName': 'Executive', 'variable': 'Metric'}
            )
            st.plotly_chart(fig_commission, use_container_width=True)
        
        # Customer preference by executive
        st.subheader("🎯 Customer Preference by Executive")
        executive_customer = df_filtered.groupby(['SalesName', 'CustomerType'])['NetSales'].sum().reset_index()
        
        fig_exec_customer = px.bar(
            executive_customer,
            x='SalesName',
            y='NetSales',
            color='CustomerType',
            title="Customer Type Distribution by Executive",
            barmode='stack',
            labels={'NetSales': 'Sales (BDT)', 'SalesName': 'Executive'}
        )
        st.plotly_chart(fig_exec_customer, use_container_width=True)
        
    else:
        st.info("No executive behavior data available")

# ================= TAB 4: CUSTOMER BEHAVIOR =================
with tab4:
    st.subheader("👤 Customer Behavior Analysis")
    
    if len(df_filtered) > 0 and 'CustomerName' in df_filtered.columns:
        # Customer purchase frequency
        customer_frequency = df_filtered.groupby('CustomerName').agg({
            'InvoiceNo': 'nunique',
            'NetSales': 'sum'
        }).reset_index()
        customer_frequency['Avg Purchase Value'] = customer_frequency['NetSales'] / customer_frequency['InvoiceNo']
        
        col_cb1, col_cb2 = st.columns(2)
        
        with col_cb1:
            # Purchase frequency distribution
            fig_frequency = px.histogram(
                customer_frequency,
                x='InvoiceNo',
                nbins=30,
                title="Customer Purchase Frequency Distribution",
                labels={'InvoiceNo': 'Number of Purchases', 'count': 'Number of Customers'},
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig_frequency, use_container_width=True)
        
        with col_cb2:
            # Customer lifetime value
            fig_clv = px.box(
                customer_frequency,
                y='NetSales',
                title="Customer Lifetime Value Distribution",
                labels={'NetSales': 'Total Purchase Value (BDT)'},
                color_discrete_sequence=['#EF553B']
            )
            st.plotly_chart(fig_clv, use_container_width=True)
        
        # Product category preference by customer type
        st.subheader("🛍️ Product Category Preference")
        
        category_preference = df_filtered.groupby(['CustomerType', 'ProductCategory'])['NetSales'].sum().reset_index()
        
        fig_category_pref = px.bar(
            category_preference,
            x='CustomerType',
            y='NetSales',
            color='ProductCategory',
            title="Product Category Preference by Customer Type",
            barmode='group',
            labels={'NetSales': 'Sales (BDT)', 'CustomerType': 'Customer Type'}
        )
        st.plotly_chart(fig_category_pref, use_container_width=True)
        
        # Heatmap - Customer vs Product Category
        st.subheader("🔥 Customer-Product Category Heatmap")
        
        customer_category_matrix = df_filtered.groupby(['CustomerName', 'ProductCategory'])['NetSales'].sum().unstack().fillna(0)
        
        # Show top 20 customers for heatmap
        top_customers_for_heatmap = customer_category_matrix.sum(axis=1).nlargest(20).index
        heatmap_data = customer_category_matrix.loc[top_customers_for_heatmap]
        
        fig_heatmap = px.imshow(
            heatmap_data,
            title="Top 20 Customers - Product Category Heatmap",
            labels={'x': 'Product Category', 'y': 'Customer Name', 'color': 'Sales (BDT)'},
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        fig_heatmap.update_layout(height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    else:
        st.info("No customer behavior data available")

# ================= TAB 5: TOP PERFORMERS =================
with tab5:
    st.subheader("🏆 Top Performers Analysis")
    
    if len(df_filtered) > 0:
        # Top Products
        st.markdown("### 🌟 Top Selling Products")
        
        product_performance = df_filtered.groupby(['ProductName', 'ProductCategory']).agg({
            'Quantity': 'sum',
            'NetSales': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        product_performance = product_performance.sort_values('NetSales', ascending=False)
        
        col_tp1, col_tp2 = st.columns(2)
        
        with col_tp1:
            top_products = product_performance.head(10)
            fig_top_products = px.bar(
                top_products,
                x='NetSales',
                y='ProductName',
                orientation='h',
                title="Top 10 Products by Sales",
                text='NetSales',
                color='NetSales',
                color_continuous_scale='Greens'  # Fixed: Changed 'Green' to 'Greens'
            )
            fig_top_products.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_top_products.update_layout(height=500)
            st.plotly_chart(fig_top_products, use_container_width=True)
        
        with col_tp2:
            top_products_qty = product_performance.nlargest(10, 'Quantity')
            fig_top_qty = px.bar(
                top_products_qty,
                x='Quantity',
                y='ProductName',
                orientation='h',
                title="Top 10 Products by Quantity Sold",
                text='Quantity',
                color='Quantity',
                color_continuous_scale='Oranges'  # Fixed: Changed 'Orange' to 'Oranges'
            )
            fig_top_qty.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_top_qty.update_layout(height=500)
            st.plotly_chart(fig_top_qty, use_container_width=True)
        
        # Top Customers
        st.markdown("### 👑 Top Customers")
        
        top_customers_detail = df_filtered.groupby(['CustomerName', 'CustomerType']).agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'ProductName': lambda x: ', '.join(x.unique()[:5])
        }).reset_index()
        
        top_customers_detail.columns = ['Customer', 'Customer Type', 'Total Sales', 'Orders', 'Top Products']
        top_customers_detail = top_customers_detail.sort_values('Total Sales', ascending=False)
        
        st.dataframe(
            top_customers_detail.head(10).style.format({
                'Total Sales': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Top Executives
        st.markdown("### 👔 Top Executives")
        
        top_executives = df_filtered.groupby('SalesName').agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Commission': 'sum'
        }).reset_index()
        
        top_executives.columns = ['Executive', 'Total Sales', 'Orders', 'Unique Customers', 'Commission']
        top_executives = top_executives.sort_values('Total Sales', ascending=False)
        
        st.dataframe(
            top_executives.style.format({
                'Total Sales': '{:,.2f}',
                'Commission': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Category Performance
        st.markdown("### 📊 Category Performance")
        
        category_performance = df_filtered.groupby('ProductCategory').agg({
            'NetSales': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        fig_category = px.pie(
            category_performance,
            values='NetSales',
            names='ProductCategory',
            title="Sales Distribution by Category",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_category, use_container_width=True)
        
        # Download all reports
        st.markdown("---")
        st.subheader("📥 Download Reports")
        
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        
        with col_dl1:
            csv_products = product_performance.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Product Report",
                csv_products,
                f"product_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        with col_dl2:
            csv_customers = top_customers_detail.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Customer Report",
                csv_customers,
                f"customer_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        with col_dl3:
            csv_executives = top_executives.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Report",
                csv_executives,
                f"executive_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
    else:
        st.info("No data available for top performers analysis")

# --- Specific Customer/Executive Transaction Download ---
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Download Specific Transactions")

# Download by Customer
if 'CustomerName' in df.columns and len(df) > 0:
    selected_customer_download = st.sidebar.selectbox(
        "Select Customer for Download",
        [''] + sorted(df['CustomerName'].dropna().unique().tolist())
    )
    if selected_customer_download:
        customer_transactions = df[df['CustomerName'] == selected_customer_download]
        csv_customer = customer_transactions.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            f"📥 Download {selected_customer_download}'s Transactions",
            csv_customer,
            f"{selected_customer_download}_transactions.csv",
            "text/csv"
        )

# Download by Executive
if 'SalesName' in df.columns and len(df) > 0:
    selected_executive_download = st.sidebar.selectbox(
        "Select Executive for Download",
        [''] + sorted(df['SalesName'].dropna().unique().tolist())
    )
    if selected_executive_download:
        executive_transactions = df[df['SalesName'] == selected_executive_download]
        csv_executive = executive_transactions.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            f"📥 Download {selected_executive_download}'s Transactions",
            csv_executive,
            f"{selected_executive_download}_transactions.csv",
            "text/csv"
        )

# --- Footer ---
st.markdown("---")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}* | Total Records: {len(df_filtered):,}")

# View Dataset Expander
with st.expander("📊 View Raw Dataset"):
    st.dataframe(df_filtered, use_container_width=True, height=400)
    st.info(f"Dataset Shape: {df_filtered.shape[0]} rows × {df_filtered.shape[1]} columns")