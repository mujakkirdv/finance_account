import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64

# --- Page Configuration ---
st.set_page_config(page_title="Financial App / Vendor Analytics", layout="wide")

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
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }
    .vendor-card {
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
        df = pd.read_csv("data/purchase_transactions.csv")
        
        # Parse PostedDate
        if 'PostedDate' in df.columns:
            df['PostedDate'] = pd.to_datetime(df['PostedDate'], errors='coerce')
            df['date'] = df['PostedDate']
        
        # Ensure numeric columns
        numeric_cols = ['UnitPrice', 'Quantity', 'OrderValue', 'DiscountValue', 'SalesValue',
                        'SalesReturn', 'DebitedAmount', 'Commission', 'Year', 'Day',
                        'NetSales', 'DueAmount']
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
if 'PostedDate' in df.columns and len(df) > 0:
    min_date = df['PostedDate'].min().date()
    max_date = df['PostedDate'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        mask = (df['PostedDate'] >= pd.to_datetime(date_range[0])) & (df['PostedDate'] <= pd.to_datetime(date_range[1]))
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
else:
    df_filtered = df.copy()

# Vendor Filter
if 'VendorName' in df_filtered.columns:
    vendors = ['All'] + sorted(df_filtered['VendorName'].dropna().unique().tolist())
    selected_vendor = st.sidebar.selectbox("Select Vendor", vendors, key="vendor_filter")
    if selected_vendor != 'All':
        df_filtered = df_filtered[df_filtered['VendorName'] == selected_vendor]

# Product Filter
if 'ProductName' in df_filtered.columns:
    products = ['All'] + sorted(df_filtered['ProductName'].dropna().unique().tolist())
    selected_product = st.sidebar.selectbox("Select Product", products, key="product_filter")
    if selected_product != 'All':
        df_filtered = df_filtered[df_filtered['ProductName'] == selected_product]

# Product Category Filter
if 'ProductCategory' in df_filtered.columns:
    categories = ['All'] + sorted(df_filtered['ProductCategory'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Product Category", categories, key="category_filter")
    if selected_category != 'All':
        df_filtered = df_filtered[df_filtered['ProductCategory'] == selected_category]

# Payment Method Filter
if 'PaymentMethods' in df_filtered.columns:
    payment_methods = ['All'] + sorted(df_filtered['PaymentMethods'].dropna().unique().tolist())
    selected_payment = st.sidebar.selectbox("Payment Method", payment_methods, key="payment_filter")
    if selected_payment != 'All':
        df_filtered = df_filtered[df_filtered['PaymentMethods'] == selected_payment]

# --- Main Header ---
st.markdown("<div class='main-header'>🏢 Vendor & Purchase Analytics Dashboard</div>", unsafe_allow_html=True)

# --- KPI Metrics Row ---
if len(df_filtered) > 0:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_purchase = df_filtered['NetSales'].sum()
        st.metric("💰 Total Purchase", f"{total_purchase:,.2f}")
    
    with col2:
        total_vendor = df_filtered['VendorID'].nunique()
        st.metric("👥 Total Vendors", f"{total_vendor:,}")
    
    with col3:
        total_items = df_filtered['ProductName'].nunique()
        st.metric("📦 Total Products", f"{total_items:,}")
    
    with col4:
        total_orders = df_filtered['InvoiceNo'].nunique()
        st.metric("📋 Total Orders", f"{total_orders:,}")
    
    with col5:
        avg_order_value = total_purchase / total_orders if total_orders > 0 else 0
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
        st.metric("🔄 Purchase Return", f"{total_return:,.2f}")
    
    with col10:
        payment_rate = ((total_purchase - total_due) / total_purchase * 100) if total_purchase > 0 else 0
        st.metric("✅ Payment Rate", f"{payment_rate:.1f}%")
else:
    st.warning("No data available for the selected filters")

# --- Tabs for Different Views ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Vendor Dashboard",
    "📦 Product Analysis",
    "💳 Payment Analytics",
    "📈 Purchase Trends",
    "🏆 Top Performers"
])

# ================= TAB 1: VENDOR DASHBOARD =================
with tab1:
    st.subheader("🏢 Vendor Performance Dashboard")
    
    if len(df_filtered) > 0 and 'VendorName' in df_filtered.columns:
        # Vendor Performance Summary
        vendor_summary = df_filtered.groupby('VendorName').agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'ProductName': 'nunique',
            'DueAmount': 'sum',
            'DiscountValue': 'sum',
            'Commission': 'sum'
        }).reset_index()
        
        vendor_summary.columns = ['Vendor', 'Total Purchase', 'Orders', 'Products', 'Due Amount', 'Discount', 'Commission']
        vendor_summary['Avg Order Value'] = vendor_summary['Total Purchase'] / vendor_summary['Orders']
        vendor_summary['Payment Rate'] = ((vendor_summary['Total Purchase'] - vendor_summary['Due Amount']) / vendor_summary['Total Purchase'] * 100).round(1)
        vendor_summary = vendor_summary.sort_values('Total Purchase', ascending=False)
        
        # Vendor Charts
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            # Bar chart - Purchase by Vendor
            fig_vendor_purchase = px.bar(
                vendor_summary.head(10),
                x='Vendor',
                y='Total Purchase',
                title="Top 10 Vendors by Purchase Value",
                text='Total Purchase',
                color='Total Purchase',
                color_continuous_scale='Viridis'
            )
            fig_vendor_purchase.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_vendor_purchase.update_layout(height=450)
            st.plotly_chart(fig_vendor_purchase, use_container_width=True)
        
        with col_v2:
            # Payment Rate by Vendor
            fig_payment_rate = px.bar(
                vendor_summary.head(10),
                x='Vendor',
                y='Payment Rate',
                title="Payment Rate by Vendor (%)",
                text='Payment Rate',
                color='Payment Rate',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig_payment_rate.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_payment_rate.update_layout(height=450)
            st.plotly_chart(fig_payment_rate, use_container_width=True)
        
        # Vendor Detailed Table
        st.subheader("📋 Vendor Performance Details")
        st.dataframe(
            vendor_summary.style.format({
                'Total Purchase': '{:,.2f}',
                'Due Amount': '{:,.2f}',
                'Discount': '{:,.2f}',
                'Commission': '{:,.2f}',
                'Avg Order Value': '{:,.2f}',
                'Payment Rate': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        # Vendor Due Analysis
        st.subheader("⚠️ Vendor Due Analysis")
        due_vendors = vendor_summary[vendor_summary['Due Amount'] > 0].sort_values('Due Amount', ascending=False)
        
        if len(due_vendors) > 0:
            fig_due = px.bar(
                due_vendors.head(10),
                x='Due Amount',
                y='Vendor',
                orientation='h',
                title="Top 10 Vendors with Due Amount",
                text='Due Amount',
                color='Due Amount',
                color_continuous_scale='Reds'
            )
            fig_due.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_due.update_layout(height=400)
            st.plotly_chart(fig_due, use_container_width=True)
        else:
            st.info("No due amounts for any vendor")
        
        # Download Vendor Report
        csv_vendor = vendor_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Vendor Report",
            data=csv_vendor,
            file_name=f"vendor_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_vendor_report"
        )
    else:
        st.info("No vendor data available")

# ================= TAB 2: PRODUCT ANALYSIS =================
with tab2:
    st.subheader("📦 Product Performance Analysis")
    
    if len(df_filtered) > 0 and 'ProductName' in df_filtered.columns:
        # Product Summary
        product_summary = df_filtered.groupby(['ProductName', 'ProductCategory']).agg({
            'NetSales': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'nunique',
            'DiscountValue': 'sum',
            'DueAmount': 'sum'
        }).reset_index()
        
        product_summary.columns = ['Product', 'Category', 'Total Purchase', 'Quantity', 'Orders', 'Discount', 'Due Amount']
        product_summary['Avg Price'] = product_summary['Total Purchase'] / product_summary['Quantity']
        product_summary = product_summary.sort_values('Total Purchase', ascending=False)
        
        # Product Charts
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            # Top Products by Purchase
            top_products = product_summary.head(10)
            fig_top_products = px.bar(
                top_products,
                x='Total Purchase',
                y='Product',
                orientation='h',
                title="Top 10 Products by Purchase Value",
                text='Total Purchase',
                color='Total Purchase',
                color_continuous_scale='Greens'
            )
            fig_top_products.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_top_products.update_layout(height=500)
            st.plotly_chart(fig_top_products, use_container_width=True)
        
        with col_p2:
            # Top Products by Quantity
            top_quantity = product_summary.nlargest(10, 'Quantity')
            fig_top_quantity = px.bar(
                top_quantity,
                x='Quantity',
                y='Product',
                orientation='h',
                title="Top 10 Products by Quantity Purchased",
                text='Quantity',
                color='Quantity',
                color_continuous_scale='Oranges'
            )
            fig_top_quantity.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_top_quantity.update_layout(height=500)
            st.plotly_chart(fig_top_quantity, use_container_width=True)
        
        # Category Performance
        st.subheader("📊 Category Performance")
        category_summary = product_summary.groupby('Category').agg({
            'Total Purchase': 'sum',
            'Quantity': 'sum',
            'Orders': 'sum'
        }).reset_index()
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            fig_category_pie = px.pie(
                category_summary,
                values='Total Purchase',
                names='Category',
                title="Purchase Distribution by Category",
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_category_pie, use_container_width=True)
        
        with col_c2:
            fig_category_bar = px.bar(
                category_summary,
                x='Category',
                y='Total Purchase',
                title="Purchase by Category",
                text='Total Purchase',
                color='Category'
            )
            fig_category_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig_category_bar, use_container_width=True)
        
        # Product Detailed Table
        with st.expander("📋 View All Product Details"):
            st.dataframe(
                product_summary.style.format({
                    'Total Purchase': '{:,.2f}',
                    'Discount': '{:,.2f}',
                    'Due Amount': '{:,.2f}',
                    'Avg Price': '{:,.2f}'
                }),
                use_container_width=True
            )
        
        # Download Product Report
        csv_product = product_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Product Report",
            data=csv_product,
            file_name=f"product_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_product_report"
        )
    else:
        st.info("No product data available")

# ================= TAB 3: PAYMENT ANALYTICS =================
with tab3:
    st.subheader("💳 Payment Method Analytics")
    
    if len(df_filtered) > 0 and 'PaymentMethods' in df_filtered.columns:
        # Payment Method Summary
        payment_summary = df_filtered.groupby('PaymentMethods').agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'DueAmount': 'sum'
        }).reset_index()
        
        payment_summary.columns = ['Payment Method', 'Total Purchase', 'Orders', 'Due Amount']
        payment_summary['Avg Order'] = payment_summary['Total Purchase'] / payment_summary['Orders']
        
        col_pay1, col_pay2 = st.columns(2)
        
        with col_pay1:
            fig_payment_pie = px.pie(
                payment_summary,
                values='Total Purchase',
                names='Payment Method',
                title="Purchase Distribution by Payment Method",
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_payment_pie, use_container_width=True)
        
        with col_pay2:
            fig_payment_bar = px.bar(
                payment_summary,
                x='Payment Method',
                y='Total Purchase',
                title="Purchase Value by Payment Method",
                text='Total Purchase',
                color='Payment Method'
            )
            fig_payment_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig_payment_bar, use_container_width=True)
        
        # Bank-wise Analysis (for Bank Transfers)
        if 'BankName' in df_filtered.columns:
            st.subheader("🏦 Bank-wise Analysis")
            bank_data = df_filtered[df_filtered['PaymentMethods'].isin(['Bank Transfer', 'Cheque'])]
            
            if len(bank_data) > 0:
                bank_summary = bank_data.groupby('BankName').agg({
                    'NetSales': 'sum',
                    'InvoiceNo': 'nunique'
                }).reset_index()
                bank_summary.columns = ['Bank', 'Total Purchase', 'Orders']
                
                fig_bank = px.bar(
                    bank_summary,
                    x='Bank',
                    y='Total Purchase',
                    title="Bank-wise Purchase Distribution",
                    text='Total Purchase',
                    color='Total Purchase',
                    color_continuous_scale='Blues'
                )
                fig_bank.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig_bank, use_container_width=True)
        
        # Payment Method Detailed Table
        st.subheader("📋 Payment Method Details")
        st.dataframe(
            payment_summary.style.format({
                'Total Purchase': '{:,.2f}',
                'Due Amount': '{:,.2f}',
                'Avg Order': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Download Payment Report
        csv_payment = payment_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Payment Report",
            data=csv_payment,
            file_name=f"payment_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_payment_report"
        )
    else:
        st.info("No payment method data available")

# ================= TAB 4: PURCHASE TRENDS =================
with tab4:
    st.subheader("📈 Purchase Trends Over Time")
    
    if len(df_filtered) > 0 and 'PostedDate' in df_filtered.columns:
        # Monthly Trend
        df_filtered['Month'] = df_filtered['PostedDate'].dt.strftime('%Y-%m')
        monthly_trend = df_filtered.groupby('Month').agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'DueAmount': 'sum'
        }).reset_index()
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            fig_monthly = px.line(
                monthly_trend,
                x='Month',
                y='NetSales',
                title="Monthly Purchase Trend",
                markers=True,
                labels={'NetSales': 'Purchase Value (BDT)', 'Month': 'Month'}
            )
            fig_monthly.update_layout(height=400)
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col_t2:
            fig_orders = px.line(
                monthly_trend,
                x='Month',
                y='InvoiceNo',
                title="Monthly Orders Trend",
                markers=True,
                labels={'InvoiceNo': 'Number of Orders', 'Month': 'Month'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig_orders.update_layout(height=400)
            st.plotly_chart(fig_orders, use_container_width=True)
        
        # Vendor-wise Monthly Trend
        st.subheader("🏢 Vendor-wise Monthly Trend")
        
        # Select top 5 vendors for trend analysis
        top_vendors = df_filtered.groupby('VendorName')['NetSales'].sum().nlargest(5).index
        vendor_trend = df_filtered[df_filtered['VendorName'].isin(top_vendors)]
        vendor_monthly = vendor_trend.groupby(['Month', 'VendorName'])['NetSales'].sum().reset_index()
        
        fig_vendor_trend = px.line(
            vendor_monthly,
            x='Month',
            y='NetSales',
            color='VendorName',
            title="Top 5 Vendors - Monthly Purchase Trend",
            markers=True,
            labels={'NetSales': 'Purchase Value (BDT)', 'Month': 'Month'}
        )
        fig_vendor_trend.update_layout(height=450)
        st.plotly_chart(fig_vendor_trend, use_container_width=True)
        
        # Category-wise Monthly Trend
        st.subheader("📦 Category-wise Monthly Trend")
        category_monthly = df_filtered.groupby(['Month', 'ProductCategory'])['NetSales'].sum().reset_index()
        
        fig_category_trend = px.area(
            category_monthly,
            x='Month',
            y='NetSales',
            color='ProductCategory',
            title="Category-wise Purchase Trend",
            labels={'NetSales': 'Purchase Value (BDT)', 'Month': 'Month'}
        )
        fig_category_trend.update_layout(height=450)
        st.plotly_chart(fig_category_trend, use_container_width=True)
        
        # Due Trend
        st.subheader("⚠️ Due Amount Trend")
        fig_due_trend = px.bar(
            monthly_trend,
            x='Month',
            y='DueAmount',
            title="Monthly Due Amount Trend",
            text='DueAmount',
            color='DueAmount',
            color_continuous_scale='Reds'
        )
        fig_due_trend.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_due_trend.update_layout(height=400)
        st.plotly_chart(fig_due_trend, use_container_width=True)
        
    else:
        st.info("No date data available for trend analysis")

# ================= TAB 5: TOP PERFORMERS =================
with tab5:
    st.subheader("🏆 Top Performers Analysis")
    
    if len(df_filtered) > 0:
        # Top Vendors
        st.markdown("### 🏢 Top Performing Vendors")
        
        top_vendors_detail = df_filtered.groupby(['VendorName', 'VendorID']).agg({
            'NetSales': 'sum',
            'InvoiceNo': 'nunique',
            'ProductName': 'nunique',
            'DiscountValue': 'sum',
            'Commission': 'sum'
        }).reset_index()
        
        top_vendors_detail.columns = ['Vendor', 'Vendor ID', 'Total Purchase', 'Orders', 'Products', 'Total Discount', 'Commission']
        top_vendors_detail = top_vendors_detail.sort_values('Total Purchase', ascending=False)
        
        st.dataframe(
            top_vendors_detail.head(10).style.format({
                'Total Purchase': '{:,.2f}',
                'Total Discount': '{:,.2f}',
                'Commission': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Top Products
        st.markdown("### 🌟 Top Products")
        
        top_products_detail = df_filtered.groupby(['ProductName', 'ProductCategory']).agg({
            'NetSales': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        top_products_detail.columns = ['Product', 'Category', 'Total Purchase', 'Quantity', 'Orders']
        top_products_detail = top_products_detail.sort_values('Total Purchase', ascending=False)
        
        st.dataframe(
            top_products_detail.head(10).style.format({
                'Total Purchase': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        # Best Selling Categories
        st.markdown("### 📊 Best Selling Categories")
        
        top_categories = df_filtered.groupby('ProductCategory').agg({
            'NetSales': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        top_categories.columns = ['Category', 'Total Purchase', 'Quantity', 'Orders']
        
        fig_category_performance = px.bar(
            top_categories,
            x='Category',
            y='Total Purchase',
            title="Category Performance",
            text='Total Purchase',
            color='Category'
        )
        fig_category_performance.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_category_performance, use_container_width=True)
        
        # Download All Reports
        st.markdown("---")
        st.subheader("📥 Download Complete Reports")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            csv_all_vendors = top_vendors_detail.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download All Vendors Report",
                csv_all_vendors,
                f"all_vendors_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="download_all_vendors"
            )
        
        with col_d2:
            csv_all_products = top_products_detail.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download All Products Report",
                csv_all_products,
                f"all_products_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="download_all_products"
            )
        
        with col_d3:
            csv_filtered = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Filtered Data",
                csv_filtered,
                f"filtered_purchase_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="download_filtered_data"
            )
    else:
        st.info("No data available for top performers analysis")

# --- Footer ---
st.markdown("---")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}* | Total Records: {len(df_filtered):,} | Total Vendors: {df_filtered['VendorName'].nunique() if 'VendorName' in df_filtered.columns else 0}")

# View Dataset Expander
with st.expander("📊 View Raw Dataset"):
    st.dataframe(df_filtered, use_container_width=True, height=400)
    st.info(f"Dataset Shape: {df_filtered.shape[0]} rows × {df_filtered.shape[1]} columns")