# ================= REPORTS DASHBOARD PAGE =================
# File: pages/REPORTS.py
# This is a standalone reports dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Reports Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 32px;
        font-weight: bold;
        color: #2E86C1;
        margin-bottom: 10px;
    }
    .report-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }
    .metric-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        color: #2E86C1;
        margin: 20px 0 10px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #2E86C1;
    }
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA FUNCTIONS =================

@st.cache_data
def load_financial_data():
    """Load financial transactions data"""
    file_path = "data/financial_transactions.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        for col in ['debit', 'credit', 'amount']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    else:
        st.warning(f"Financial data file not found: {file_path}")
        return pd.DataFrame()

@st.cache_data
def load_sales_data():
    """Load sales transactions data"""
    file_path = "data/cosmetics_sales.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'OrderDate' in df.columns:
            df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
        if 'invoice_date' in df.columns:
            df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')
        numeric_cols = ['UnitPrice', 'Quantity', 'OrderValue', 'DiscountValue', 'SalesValue', 
                       'SalesReturn', 'CreditedAmount', 'Commission', 'NetSales', 'DueAmount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    else:
        st.warning(f"Sales data file not found: {file_path}")
        return pd.DataFrame()

@st.cache_data
def load_purchase_data():
    """Load purchase transactions data"""
    file_path = "data/purchase_transactions.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'PostedDate' in df.columns:
            df['PostedDate'] = pd.to_datetime(df['PostedDate'], errors='coerce')
        if 'purchase_date' in df.columns:
            df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        numeric_cols = ['UnitPrice', 'Quantity', 'OrderValue', 'DiscountValue', 'SalesValue',
                       'SalesReturn', 'DebitedAmount', 'Commission', 'NetSales', 'DueAmount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    else:
        st.warning(f"Purchase data file not found: {file_path}")
        return pd.DataFrame()

# ================= LOAD ALL DATA =================
df_financial = load_financial_data()
df_sales = load_sales_data()
df_purchase = load_purchase_data()

# ================= MAIN REPORTS DASHBOARD =================
def main():
    st.markdown("<div class='main-header'>📊 Reports Dashboard</div>", unsafe_allow_html=True)
    
    # ================= DATE RANGE SELECTOR =================
    st.subheader("📅 Select Report Period")
    col_date1, col_date2, col_date3 = st.columns([2, 2, 1])
    
    # Initialize dates
    default_start = datetime.now() - timedelta(days=30)
    default_end = datetime.now()
    
    with col_date1:
        start_date = st.date_input("Start Date", value=default_start)
    with col_date2:
        end_date = st.date_input("End Date", value=default_end)
    with col_date3:
        preset_period = st.selectbox("Quick Select", 
                                     ["Custom", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Month", "Last Month", "This Year"])
        
        if preset_period == "Last 7 Days":
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
        elif preset_period == "Last 30 Days":
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
        elif preset_period == "Last 90 Days":
            start_date = datetime.now() - timedelta(days=90)
            end_date = datetime.now()
        elif preset_period == "This Month":
            start_date = datetime.now().replace(day=1)
            end_date = datetime.now()
        elif preset_period == "Last Month":
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = datetime.now().replace(day=1) - timedelta(days=1)
        elif preset_period == "This Year":
            start_date = datetime.now().replace(month=1, day=1)
            end_date = datetime.now()
    
    # Convert dates to datetime for filtering
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + timedelta(days=1)
    
    # ================= FILTER DATA BY DATE =================
    
    # Financial data filter
    if len(df_financial) > 0 and 'transaction_date' in df_financial.columns:
        fin_filtered = df_financial[
            (df_financial['transaction_date'] >= start_datetime) & 
            (df_financial['transaction_date'] <= end_datetime)
        ].copy()
    else:
        fin_filtered = pd.DataFrame()
    
    # Sales data filter - handle different date column names
    if len(df_sales) > 0:
        date_col = 'OrderDate' if 'OrderDate' in df_sales.columns else ('invoice_date' if 'invoice_date' in df_sales.columns else None)
        if date_col:
            sales_filtered = df_sales[
                (df_sales[date_col] >= start_datetime) & 
                (df_sales[date_col] <= end_datetime)
            ].copy()
        else:
            sales_filtered = pd.DataFrame()
    else:
        sales_filtered = pd.DataFrame()
    
    # Purchase data filter
    if len(df_purchase) > 0:
        date_col = 'PostedDate' if 'PostedDate' in df_purchase.columns else ('purchase_date' if 'purchase_date' in df_purchase.columns else None)
        if date_col:
            purchase_filtered = df_purchase[
                (df_purchase[date_col] >= start_datetime) & 
                (df_purchase[date_col] <= end_datetime)
            ].copy()
        else:
            purchase_filtered = pd.DataFrame()
    else:
        purchase_filtered = pd.DataFrame()
    
    # ================= KEY METRICS ROW =================
    st.markdown("<div class='section-header'>📊 Key Performance Indicators</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_income = fin_filtered['debit'].sum() if len(fin_filtered) > 0 else 0
        st.metric("💰 Total Income", f"{total_income:,.2f}")
    
    with col2:
        total_expense = fin_filtered['credit'].sum() if len(fin_filtered) > 0 else 0
        st.metric("💸 Total Expense", f"{total_expense:,.2f}")
    
    with col3:
        net_profit = total_income - total_expense
        st.metric("📈 Net Profit/Loss", f"{net_profit:,.2f}", 
                 delta="Profit" if net_profit > 0 else "Loss")
    
    with col4:
        profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
        st.metric("🎯 Profit Margin", f"{profit_margin:.1f}%")
    
    # Second row of metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        total_sales = sales_filtered['NetSales'].sum() if len(sales_filtered) > 0 and 'NetSales' in sales_filtered.columns else 0
        st.metric("🏷️ Total Sales", f"{total_sales:,.2f}")
    
    with col6:
        total_purchases = purchase_filtered['NetSales'].sum() if len(purchase_filtered) > 0 and 'NetSales' in purchase_filtered.columns else 0
        st.metric("📦 Total Purchases", f"{total_purchases:,.2f}")
    
    with col7:
        gross_profit = total_sales - total_purchases
        st.metric("💵 Gross Profit", f"{gross_profit:,.2f}")
    
    with col8:
        transaction_count = len(fin_filtered) + len(sales_filtered) + len(purchase_filtered)
        st.metric("📋 Total Transactions", f"{transaction_count:,}")
    
    # ================= FINANCIAL CHARTS =================
    st.markdown("<div class='section-header'>📈 Financial Analysis</div>", unsafe_allow_html=True)
    
    col_ch1, col_ch2 = st.columns(2)
    
    with col_ch1:
        # Income vs Expense Bar Chart
        if len(fin_filtered) > 0 and 'transaction_date' in fin_filtered.columns:
            fin_filtered['month'] = fin_filtered['transaction_date'].dt.to_period('M').astype(str)
            monthly_summary = fin_filtered.groupby('month', as_index=False).agg(
                income=('debit', 'sum'),
                expense=('credit', 'sum')
            )
            
            fig_income_expense = px.bar(
                monthly_summary, 
                x='month', 
                y=['income', 'expense'],
                barmode='group', 
                title="Monthly Income vs Expense",
                labels={'value': 'Amount (BDT)', 'month': 'Month', 'variable': 'Type'},
                color_discrete_map={'income': '#2ECC71', 'expense': '#E74C3C'}
            )
            fig_income_expense.update_layout(height=400)
            st.plotly_chart(fig_income_expense, use_container_width=True)
        else:
            st.info("No financial data available for chart")
    
    with col_ch2:
        # Cash Flow Trend
        if len(fin_filtered) > 0 and 'transaction_date' in fin_filtered.columns:
            # FIXED: Properly calculate net flow
            fin_filtered['date_only'] = fin_filtered['transaction_date'].dt.date
            daily_cashflow = fin_filtered.groupby('date_only').agg(
                total_debit=('debit', 'sum'),
                total_credit=('credit', 'sum')
            ).reset_index()
            daily_cashflow['net_flow'] = daily_cashflow['total_debit'] - daily_cashflow['total_credit']
            
            fig_cashflow = px.line(
                daily_cashflow,
                x='date_only',
                y='net_flow',
                title="Daily Cash Flow Trend",
                labels={'date_only': 'Date', 'net_flow': 'Net Cash Flow (BDT)'},
                markers=True
            )
            fig_cashflow.add_hline(y=0, line_dash="dash", line_color="red")
            fig_cashflow.update_layout(height=400)
            st.plotly_chart(fig_cashflow, use_container_width=True)
        else:
            st.info("No cash flow data available")
    
    # ================= SALES & PURCHASE ANALYSIS =================
    st.markdown("<div class='section-header'>📊 Sales & Purchase Analysis</div>", unsafe_allow_html=True)
    
    col_sp1, col_sp2 = st.columns(2)
    
    with col_sp1:
        # Payment Status Distribution
        if len(sales_filtered) > 0:
            # Check for payment status column
            payment_status_col = None
            for col in ['payment_status', 'PaymentStatus', 'PaymentMethods']:
                if col in sales_filtered.columns:
                    payment_status_col = col
                    break
            
            amount_col = 'NetSales' if 'NetSales' in sales_filtered.columns else ('net_amount' if 'net_amount' in sales_filtered.columns else None)
            
            if payment_status_col and amount_col:
                payment_summary = sales_filtered.groupby(payment_status_col)[amount_col].sum().reset_index()
                fig_payment = px.pie(
                    payment_summary, 
                    values=amount_col, 
                    names=payment_status_col,
                    title="Sales by Payment Status", 
                    hole=0.3,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_payment, use_container_width=True)
            else:
                st.info("No payment status data available")
        else:
            st.info("No sales data available")
    
    with col_sp2:
        # Sales vs Purchase Comparison
        if len(sales_filtered) > 0 or len(purchase_filtered) > 0:
            comparison_data = []
            
            if len(sales_filtered) > 0:
                date_col = 'OrderDate' if 'OrderDate' in sales_filtered.columns else ('invoice_date' if 'invoice_date' in sales_filtered.columns else None)
                amount_col = 'NetSales' if 'NetSales' in sales_filtered.columns else ('net_amount' if 'net_amount' in sales_filtered.columns else None)
                if date_col and amount_col:
                    sales_filtered['month'] = sales_filtered[date_col].dt.to_period('M').astype(str)
                    monthly_sales = sales_filtered.groupby('month')[amount_col].sum().reset_index()
                    monthly_sales.columns = ['month', 'Sales']
                    comparison_data.append(monthly_sales)
            
            if len(purchase_filtered) > 0:
                date_col = 'PostedDate' if 'PostedDate' in purchase_filtered.columns else ('purchase_date' if 'purchase_date' in purchase_filtered.columns else None)
                amount_col = 'NetSales' if 'NetSales' in purchase_filtered.columns else ('net_amount' if 'net_amount' in purchase_filtered.columns else None)
                if date_col and amount_col:
                    purchase_filtered['month'] = purchase_filtered[date_col].dt.to_period('M').astype(str)
                    monthly_purchases = purchase_filtered.groupby('month')[amount_col].sum().reset_index()
                    monthly_purchases.columns = ['month', 'Purchases']
                    comparison_data.append(monthly_purchases)
            
            if len(comparison_data) > 0:
                # Merge all dataframes
                import functools
                combined = functools.reduce(lambda left, right: pd.merge(left, right, on='month', how='outer'), comparison_data)
                combined = combined.fillna(0)
                
                # Get columns for y-axis (exclude 'month')
                y_columns = [col for col in combined.columns if col != 'month']
                
                if y_columns:
                    fig_comparison = px.bar(
                        combined,
                        x='month',
                        y=y_columns,
                        barmode='group',
                        title="Monthly Sales vs Purchase Comparison",
                        labels={'value': 'Amount (BDT)', 'month': 'Month', 'variable': 'Type'}
                    )
                    st.plotly_chart(fig_comparison, use_container_width=True)
                else:
                    st.info("No comparison data available")
            else:
                st.info("No comparison data available")
        else:
            st.info("No sales or purchase data available")
    
    # ================= ACCOUNTS RECEIVABLE & PAYABLE =================
    st.markdown("<div class='section-header'>📋 Accounts Receivable & Payable</div>", unsafe_allow_html=True)
    
    col_ar1, col_ar2 = st.columns(2)
    
    with col_ar1:
        # Accounts Receivable (Customer Dues)
        st.subheader("📥 Accounts Receivable")
        if len(df_sales) > 0:
            # Find due amount column
            due_col = None
            for col in ['DueAmount', 'due_amount', 'Due']:
                if col in df_sales.columns:
                    due_col = col
                    break
            
            # Find customer name column
            customer_col = None
            for col in ['CustomerName', 'customer_name', 'Customer']:
                if col in df_sales.columns:
                    customer_col = col
                    break
            
            # Find invoice column
            invoice_col = None
            for col in ['InvoiceNo', 'invoice_no', 'Invoice']:
                if col in df_sales.columns:
                    invoice_col = col
                    break
            
            if due_col and customer_col:
                # Filter due customers
                due_customers_df = df_sales[df_sales[due_col] > 0]
                
                if len(due_customers_df) > 0:
                    # Group by customer
                    if invoice_col:
                        due_customers = due_customers_df.groupby(customer_col).agg({
                            due_col: 'sum',
                            invoice_col: 'count'
                        }).reset_index()
                        due_customers.columns = ['Customer Name', 'Due Amount', 'Invoice Count']
                    else:
                        due_customers = due_customers_df.groupby(customer_col).agg({
                            due_col: 'sum'
                        }).reset_index()
                        due_customers.columns = ['Customer Name', 'Due Amount']
                    
                    due_customers = due_customers.sort_values('Due Amount', ascending=False)
                    st.dataframe(due_customers.head(10), use_container_width=True)
                    st.metric("Total Receivable", f"{due_customers['Due Amount'].sum():,.2f}")
                    st.caption("💡 Tip: Focus on collecting from top 5 customers first")
                else:
                    st.success("✅ No customer dues found! Great collections!")
            else:
                st.info("No due amount column found in sales data")
        else:
            st.info("No sales data available")
    
    with col_ar2:
        # Accounts Payable (Supplier Dues)
        st.subheader("📂 Accounts Payable")
        if len(df_purchase) > 0:
            # Find due amount column
            due_col = None
            for col in ['DueAmount', 'due_amount', 'Due']:
                if col in df_purchase.columns:
                    due_col = col
                    break
            
            # Find supplier name column
            supplier_col = None
            for col in ['VendorName', 'vendor_name', 'SupplierName', 'supplier_name']:
                if col in df_purchase.columns:
                    supplier_col = col
                    break
            
            # Find PO column
            po_col = None
            for col in ['PoNumber', 'po_number', 'PurchaseNo', 'purchase_no']:
                if col in df_purchase.columns:
                    po_col = col
                    break
            
            if due_col and supplier_col:
                # Filter due suppliers
                due_suppliers_df = df_purchase[df_purchase[due_col] > 0]
                
                if len(due_suppliers_df) > 0:
                    # Group by supplier
                    if po_col:
                        due_suppliers = due_suppliers_df.groupby(supplier_col).agg({
                            due_col: 'sum',
                            po_col: 'count'
                        }).reset_index()
                        due_suppliers.columns = ['Supplier Name', 'Due Amount', 'Purchase Count']
                    else:
                        due_suppliers = due_suppliers_df.groupby(supplier_col).agg({
                            due_col: 'sum'
                        }).reset_index()
                        due_suppliers.columns = ['Supplier Name', 'Due Amount']
                    
                    due_suppliers = due_suppliers.sort_values('Due Amount', ascending=False)
                    st.dataframe(due_suppliers.head(10), use_container_width=True)
                    st.metric("Total Payable", f"{due_suppliers['Due Amount'].sum():,.2f}")
                    st.caption("⚠️ Priority: Pay suppliers with oldest dues first")
                else:
                    st.success("✅ No supplier dues found! All payments cleared!")
            else:
                st.info("No due amount column found in purchase data")
        else:
            st.info("No purchase data available")
    
    # ================= TOP PERFORMERS =================
    st.markdown("<div class='section-header'>🏆 Top Performers</div>", unsafe_allow_html=True)
    
    col_top1, col_top2, col_top3 = st.columns(3)
    
    with col_top1:
        # Top Customers
        st.subheader("👥 Top Customers")
        if len(df_sales) > 0:
            amount_col = 'NetSales' if 'NetSales' in df_sales.columns else ('net_amount' if 'net_amount' in df_sales.columns else None)
            customer_col = 'CustomerName' if 'CustomerName' in df_sales.columns else ('customer_name' if 'customer_name' in df_sales.columns else None)
            
            if amount_col and customer_col:
                top_customers = df_sales.groupby(customer_col)[amount_col].sum().sort_values(ascending=False).head(10)
                
                if len(top_customers) > 0:
                    fig_customers = px.bar(
                        x=top_customers.values,
                        y=top_customers.index,
                        orientation='h',
                        title="Top 10 Customers by Sales",
                        labels={'x': 'Sales (BDT)', 'y': 'Customer'},
                        text=top_customers.values
                    )
                    fig_customers.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    fig_customers.update_layout(height=400)
                    st.plotly_chart(fig_customers, use_container_width=True)
                else:
                    st.info("No customer data available")
            else:
                st.info("Required columns not found")
        else:
            st.info("No sales data available")
    
    with col_top2:
        # Top Products
        st.subheader("🌟 Top Products")
        if len(df_sales) > 0:
            product_col = 'ProductName' if 'ProductName' in df_sales.columns else ('product_name' if 'product_name' in df_sales.columns else None)
            quantity_col = 'Quantity' if 'Quantity' in df_sales.columns else ('quantity' if 'quantity' in df_sales.columns else None)
            
            if product_col and quantity_col:
                top_products = df_sales.groupby(product_col)[quantity_col].sum().sort_values(ascending=False).head(10)
                
                if len(top_products) > 0:
                    fig_products = px.bar(
                        x=top_products.values,
                        y=top_products.index,
                        orientation='h',
                        title="Top 10 Products by Quantity",
                        labels={'x': 'Quantity Sold', 'y': 'Product'},
                        text=top_products.values
                    )
                    fig_products.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    fig_products.update_layout(height=400)
                    st.plotly_chart(fig_products, use_container_width=True)
                else:
                    st.info("No product data available")
            else:
                st.info("Required columns not found")
        else:
            st.info("No sales data available")
    
    with col_top3:
        # Top Vendors
        st.subheader("🏢 Top Vendors")
        if len(df_purchase) > 0:
            vendor_col = None
            for col in ['VendorName', 'vendor_name', 'SupplierName', 'supplier_name']:
                if col in df_purchase.columns:
                    vendor_col = col
                    break
            
            amount_col = 'NetSales' if 'NetSales' in df_purchase.columns else ('net_amount' if 'net_amount' in df_purchase.columns else None)
            
            if vendor_col and amount_col:
                top_vendors = df_purchase.groupby(vendor_col)[amount_col].sum().sort_values(ascending=False).head(10)
                
                if len(top_vendors) > 0:
                    fig_vendors = px.bar(
                        x=top_vendors.values,
                        y=top_vendors.index,
                        orientation='h',
                        title="Top 10 Vendors by Purchase",
                        labels={'x': 'Purchase (BDT)', 'y': 'Vendor'},
                        text=top_vendors.values
                    )
                    fig_vendors.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                    fig_vendors.update_layout(height=400)
                    st.plotly_chart(fig_vendors, use_container_width=True)
                else:
                    st.info("No vendor data available")
            else:
                st.info("Required columns not found")
        else:
            st.info("No purchase data available")
    
    # ================= EXPORT REPORTS =================
    st.markdown("<div class='section-header'>📥 Export Reports</div>", unsafe_allow_html=True)
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        if len(fin_filtered) > 0:
            csv_financial = fin_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Financial Report",
                csv_financial,
                f"financial_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="export_financial"
            )
    
    with col_exp2:
        if len(sales_filtered) > 0:
            csv_sales = sales_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Sales Report",
                csv_sales,
                f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="export_sales"
            )
    
    with col_exp3:
        if len(purchase_filtered) > 0:
            csv_purchase = purchase_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Purchase Report",
                csv_purchase,
                f"purchase_report_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="export_purchase"
            )
    
    # ================= SUMMARY INSIGHTS =================
    st.markdown("<div class='section-header'>💡 Key Insights & Recommendations</div>", unsafe_allow_html=True)
    
    col_ins1, col_ins2 = st.columns(2)
    
    with col_ins1:
        st.markdown("### 📈 Performance Insights")
        
        insights = []
        
        if total_sales > 0:
            if gross_profit > 0:
                insights.append(f"✅ Gross profit margin: {(gross_profit/total_sales*100):.1f}%")
            else:
                insights.append(f"⚠️ Negative gross profit margin: {(gross_profit/total_sales*100):.1f}%")
        
        if profit_margin > 20:
            insights.append("🎯 Excellent profit margin above 20%")
        elif profit_margin > 10:
            insights.append("📊 Healthy profit margin between 10-20%")
        elif profit_margin > 0:
            insights.append("⚠️ Low profit margin, consider cost optimization")
        else:
            insights.append("🔴 Operating at a loss, review expenses")
        
        if insights:
            for insight in insights:
                st.write(insight)
        else:
            st.info("Insufficient data for insights")
    
    with col_ins2:
        st.markdown("### 💰 Cash Flow Insights")
        
        cash_insights = []
        
        if total_income > 0:
            expense_ratio = (total_expense / total_income * 100) if total_income > 0 else 0
            if expense_ratio < 70:
                cash_insights.append(f"✅ Expense ratio is healthy: {expense_ratio:.1f}%")
            elif expense_ratio < 85:
                cash_insights.append(f"📊 Moderate expense ratio: {expense_ratio:.1f}%")
            else:
                cash_insights.append(f"⚠️ High expense ratio: {expense_ratio:.1f}%")
        
        if len(df_sales) > 0 and 'DueAmount' in df_sales.columns and 'NetSales' in df_sales.columns:
            receivable_days = (df_sales['DueAmount'].sum() / df_sales['NetSales'].sum() * 30) if df_sales['NetSales'].sum() > 0 else 0
            cash_insights.append(f"📅 Average receivable days: {receivable_days:.0f} days")
        
        if cash_insights:
            for insight in cash_insights:
                st.write(insight)
        else:
            st.info("Insufficient data for cash flow insights")
    
    # ================= FOOTER =================
    st.markdown("---")
    st.markdown(f"*Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.markdown(f"*Data period: {start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else start_date} to {end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else end_date}*")

# ================= RUN THE APP =================
if __name__ == "__main__":
    main()