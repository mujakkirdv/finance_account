import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
from datetime import timedelta
import numpy as np
# ================= CONFIGURATION =================
st.set_page_config(
    page_title="Finance and Account Dashboard",
    page_icon="💰",
    layout="wide"
)

# ================= SETTINGS =================
FILE = "data/financial_transactions.csv"
SALES_FILE = "data/cosmetics_sales.csv"
PURCHASE_FILE = "data/purchase_transactions.csv"

# ================= CUSTOM CSS =================
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
    .bank-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .vendor-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }
    .due-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .form-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border: 1px solid #dee2e6;
    }
    .status-paid { color: green; font-weight: bold; }
    .status-due { color: red; font-weight: bold; }
    .status-partial { color: orange; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA FUNCTIONS =================

@st.cache_data
def load_financial_data():
    """Load financial transactions data"""
    if os.path.exists(FILE):
        df = pd.read_csv(FILE)
        for col in ['transaction_date', 'date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Ensure required columns exist
        for col in ['debit', 'credit', 'amount']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    else:
        # Create empty dataframe with required columns
        columns = ['transaction_id', 'transaction_date', 'voucher_no', 'account_head',
                  'account_type', 'category', 'sub_category', 'party_name',
                  'payment_method', 'bank_name', 'reference', 'debit', 'credit', 'amount',
                  'remarks', 'created_by']
        return pd.DataFrame(columns=columns)

@st.cache_data
def load_sales_data():
    """Load sales transactions data"""
    if os.path.exists(SALES_FILE):
        df = pd.read_csv(SALES_FILE)
        for col in ['invoice_date', 'due_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    else:
        columns = ['invoice_id', 'invoice_no', 'invoice_date', 'customer_name', 
                  'customer_phone', 'product_name', 'quantity', 'unit_price', 
                  'total_amount', 'discount', 'tax', 'net_amount', 'payment_status',
                  'payment_method', 'due_date', 'remarks', 'created_by']
        return pd.DataFrame(columns=columns)

@st.cache_data
def load_purchase_data():
    """Load purchase transactions data"""
    if os.path.exists(PURCHASE_FILE):
        df = pd.read_csv(PURCHASE_FILE)
        for col in ['purchase_date', 'due_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    else:
        columns = ['purchase_id', 'purchase_no', 'purchase_date', 'supplier_name',
                  'supplier_phone', 'product_name', 'quantity', 'unit_price',
                  'total_amount', 'discount', 'tax', 'net_amount', 'payment_status',
                  'payment_method', 'due_date', 'remarks', 'created_by']
        return pd.DataFrame(columns=columns)

# ================= SAVE DATA FUNCTIONS =================

def save_financial_data(df):
    """Save financial data to CSV"""
    os.makedirs("data", exist_ok=True)
    df.to_csv(FILE, index=False)
    return True

def save_sales_data(df):
    """Save sales data to CSV"""
    os.makedirs("data", exist_ok=True)
    df.to_csv(SALES_FILE, index=False)
    return True

def save_purchase_data(df):
    """Save purchase data to CSV"""
    os.makedirs("data", exist_ok=True)
    df.to_csv(PURCHASE_FILE, index=False)
    return True

# ================= LOAD ALL DATA =================
df_financial = load_financial_data()
df_sales = load_sales_data()
df_purchase = load_purchase_data()

# ================= SESSION STATE INITIALIZATION =================
if 'data_updated' not in st.session_state:
    st.session_state.data_updated = False

# ================= SIDEBAR MENU =================
menu = [
    "🏠 Home", 
    "📝 Bank Data Entry", 
    "💰 Sales Entry", 
    "📦 Payable | Purchase Entry",
    "🏢 Vendor Payable Management",
    "📊 Reports Dashboard"
]

choice = st.sidebar.radio("📌 Navigation", menu)

# ================= HOME PAGE =================
if choice == "🏠 Home":
    st.markdown("<div class='main-header'>🏠 Welcome to Financial App</div>", unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_transactions = len(df_financial)
        st.metric("📊 Total Transactions", total_transactions)
    
    with col2:
        total_sales = df_sales['NetSales'].sum() if len(df_sales) > 0 else 0
        st.metric("💰 Total Sales", f"{total_sales:,.2f}")
    
    with col3:
        total_purchase = df_purchase['NetSales'].sum() if len(df_purchase) > 0 else 0
        st.metric("📦 Total Purchases", f"{total_purchase:,.2f}")
    
    with col4:
        profit = total_sales - total_purchase
        st.metric("📈 Estimated Profit", f"{profit:,.2f}", 
                 delta="Positive" if profit > 0 else "Negative")
    
    # Features
    st.subheader("📌 Features of this Application")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='feature-card'>💵 Cashbook Management</div>", unsafe_allow_html=True)
        st.markdown("<div class='feature-card'>🏦 Bankbook & Transactions</div>", unsafe_allow_html=True)
        st.markdown("<div class='feature-card'>📂 Accounts Payable</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='feature-card'>📥 Accounts Receivable</div>", unsafe_allow_html=True)
        st.markdown("<div class='feature-card'>📈 Forecast & Analytics</div>", unsafe_allow_html=True)
        st.markdown("<div class='feature-card'>📑 MD Reports</div>", unsafe_allow_html=True)
    
    # Recent Activity
    st.subheader("📋 Recent Activity")
    
    tab_home1, tab_home2, tab_home3 = st.tabs(["💰 Financial", "💵 Sales", "📦 Purchase"])
    
    with tab_home1:
        if len(df_financial) > 0:
            recent_fin = df_financial.sort_values('transaction_date', ascending=False).head(5)
            st.dataframe(recent_fin[['transaction_date', 'account_head', 'debit', 'credit', 'party_name']], 
                        use_container_width=True)
        else:
            st.info("No financial transactions yet")
    
    with tab_home2:
        if len(df_sales) > 0:
            recent_sales = df_sales.sort_values('OrderDate', ascending=False).head(5)
            st.dataframe(recent_sales[['OrderDate', 'CustomerName', 'ProductName', 'NetSales', 'Gender']],
                        use_container_width=True)
        else:
            st.info("No sales transactions yet")
    
    with tab_home3:
        if len(df_purchase) > 0:
            recent_purchase = df_purchase.sort_values('PostedDate', ascending=False).head(5)
            st.dataframe(recent_purchase[['PostedDate', 'VendorName', 'ProductName', 'NetSales', 'DiscountValue']],
                        use_container_width=True)
        else:
            st.info("No purchase transactions yet")

# ================= BANK DATA ENTRY PAGE =================
elif choice == "📝 Bank Data Entry":
    st.markdown("<div class='main-header'>📝 Bank Data Entry</div>", unsafe_allow_html=True)
    
    # Real-time Data Entry Section
    with st.sidebar:
        st.markdown("---")
        st.markdown("## ✍️ Quick Data Entry")
        if st.button("➕ Add New Transaction", use_container_width=True, type="primary"):
            st.session_state.show_bank_form = True
    
    if st.session_state.get('show_bank_form', False):
        with st.form("bank_transaction_form", clear_on_submit=True):
            st.markdown("### New Bank Transaction")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Generate transaction ID
                if len(df_financial) > 0 and 'transaction_id' in df_financial.columns:
                    last_id = df_financial['transaction_id'].max()
                    new_id = int(last_id) + 1 if pd.notna(last_id) else 1
                else:
                    new_id = 1
                
                transaction_id = st.number_input("Transaction ID", value=new_id, step=1)
                transaction_date = st.date_input("Transaction Date", value=datetime.now())
                voucher_no = st.text_input("Voucher No", placeholder="e.g., V-2024-001")
                account_head = st.text_input("Account Head *", placeholder="e.g., Sales, Purchase")
                
            with col2:
                account_type = st.selectbox("Account Type", ["Asset", "Liability", "Income", "Expense", "Equity"])
                category = st.text_input("Category", placeholder="e.g., Revenue, Operating")
                sub_category = st.text_input("Sub Category")
                party_name = st.text_input("Party Name", placeholder="Customer/Vendor name")
                
            with col3:
                payment_method = st.selectbox("Payment Method", ["Cash", "Bank", "Cheque", "Online Transfer"])
                bank_name = st.text_input("Bank Name", placeholder="e.g., HDFC, ICICI")
                reference = st.text_input("Reference", placeholder="Cheque no, UTR")
                
                debit = st.number_input("Debit (Income)", min_value=0.0, value=0.0, step=100.0)
                credit = st.number_input("Credit (Expense)", min_value=0.0, value=0.0, step=100.0)
            
            remarks = st.text_area("Remarks")
            created_by = st.text_input("Created By", value="Admin")
            
            submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True)
            
            if submitted:
                if debit == 0 and credit == 0:
                    st.error("Please enter either Debit or Credit amount")
                elif not account_head:
                    st.error("Account Head is required")
                else:
                    new_transaction = {
                        'transaction_id': transaction_id,
                        'transaction_date': pd.to_datetime(transaction_date),
                        'voucher_no': voucher_no if voucher_no else f"AUTO-{transaction_id}",
                        'account_head': account_head,
                        'account_type': account_type,
                        'category': category if category else "General",
                        'sub_category': sub_category,
                        'party_name': party_name,
                        'payment_method': payment_method,
                        'bank_name': bank_name if payment_method == "Bank" else "",
                        'reference': reference,
                        'debit': debit,
                        'credit': credit,
                        'amount': max(debit, credit),
                        'remarks': remarks,
                        'created_by': created_by
                    }
                    
                    df_financial = pd.concat([df_financial, pd.DataFrame([new_transaction])], ignore_index=True)
                    
                    if save_financial_data(df_financial):
                        st.success(f"✅ Transaction saved! ID: {transaction_id}")
                        st.balloons()
                        st.cache_data.clear()
                        st.rerun()
        
        if st.button("Close Form"):
            st.session_state.show_bank_form = False
            st.rerun()
    
    # Display existing data
    st.subheader("📋 Existing Bank Transactions")
    if len(df_financial) > 0:
        st.dataframe(df_financial.sort_values('transaction_date', ascending=False), 
                    use_container_width=True, height=400)
        
        # Export option
        csv = df_financial.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export to CSV", csv, "bank_transactions.csv", "text/csv", key="export_bank")
    else:
        st.info("No bank transactions found. Click 'Add New Transaction' to get started.")

# ================= SALES ENTRY PAGE =================
elif choice == "💰 Sales Entry":
    st.markdown("<div class='main-header'>💰 Sales Entry</div>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("---")
        if st.button("➕ New Sales Invoice", use_container_width=True, type="primary"):
            st.session_state.show_sales_form = True
    
    if st.session_state.get('show_sales_form', False):
        with st.form("sales_form", clear_on_submit=True):
            st.markdown("### New Sales Invoice")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Generate Sales ID
                if len(df_sales) > 0 and 'SalesID' in df_sales.columns:
                    # Convert to numeric, handling any non-numeric values
                    sales_ids = pd.to_numeric(df_sales['SalesID'], errors='coerce').dropna()
                    if len(sales_ids) > 0:
                        last_id = int(sales_ids.max())
                        new_id = last_id + 1
                    else:
                        new_id = 1
                else:
                    new_id = 1
                
                sales_id = st.number_input("Sales ID", value=new_id, step=1)
                invoice_no = st.text_input("Invoice No", placeholder=f"INV-{datetime.now().strftime('%Y%m%d')}-{new_id}")
                order_date = st.date_input("Order Date", value=datetime.now())
                sales_name = st.text_input("Sales Executive Name *", placeholder="e.g., John Doe")
                
            with col2:
                customer_name = st.text_input("Customer Name *")
                customer_id = st.text_input("Customer ID", placeholder=f"CUST-{new_id}")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                customer_type = st.selectbox("Customer Type", ["Regular", "Premium", "New", "Wholesale"])
                customer_phone = st.text_input("Customer Phone")
            
            with col3:
                product_name = st.text_input("Product Name *")
                product_code = st.text_input("Product Code", placeholder=f"PRD-{new_id}")
                product_category = st.selectbox("Product Category", 
                                               ["Cosmetics", "Accessories", "Fashion Apparel", "Hygiene Products"])
                category_code = st.selectbox("Category Code", ["CAT001", "CAT002", "CAT003", "CAT004"])
            
            # Product Details Section
            st.markdown("---")
            st.markdown("### 📊 Product & Pricing Details")
            
            col_price1, col_price2, col_price3 = st.columns(3)
            
            with col_price1:
                quantity = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
                unit_price = st.number_input("Unit Price (BDT)", min_value=0.0, value=0.0, step=100.0)
                order_value = quantity * unit_price
                st.info(f"**Order Value:** {order_value:,.2f}")
            
            with col_price2:
                discount_percent = st.slider("Discount (%)", min_value=0.0, max_value=50.0, value=0.0, step=1.0)
                discount_value = order_value * (discount_percent / 100)
                sales_value = order_value - discount_value
                st.info(f"**Sales Value:** {sales_value:,.2f}")
            
            with col_price3:
                sales_return = st.number_input("Sales Return (BDT)", min_value=0.0, value=0.0, step=50.0)
                credited_amount = sales_value - sales_return
                commission_percent = st.slider("Commission (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
                commission = credited_amount * (commission_percent / 100)
                net_sales = credited_amount - commission
            
            st.markdown(f"**💰 Net Sales Amount:** {net_sales:,.2f}")
            
            # Payment Details
            st.markdown("---")
            st.markdown("### 💳 Payment Details")
            
            col_pay1, col_pay2 = st.columns(2)
            
            with col_pay1:
                payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Cheque", "Bkash", "Nagad"])
                bank_name = st.text_input("Bank Name", placeholder="Required if payment method is Bank Transfer")
                reference = st.text_input("Reference No", placeholder="Cheque no, UTR, Transaction ID")
            
            with col_pay2:
                payment_status = st.selectbox("Payment Status", ["Paid", "Partial", "Due"])
                if payment_status == "Paid":
                    due_amount = 0
                elif payment_status == "Partial":
                    due_amount = net_sales * 0.5
                else:
                    due_amount = net_sales
                st.warning(f"**Due Amount:** {due_amount:,.2f}")
            
            # Additional Info
            st.markdown("---")
            st.markdown("### 📝 Additional Information")
            
            col_rem1, col_rem2 = st.columns(2)
            
            with col_rem1:
                year = st.number_input("Year", value=datetime.now().year, step=1)
                month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1)
                day = st.number_input("Day", value=datetime.now().day, min_value=1, max_value=31)
            
            with col_rem2:
                remarks = st.text_area("Remarks", placeholder="Additional notes about the sale")
                created_by = st.text_input("Created By", value="Admin")
            
            submitted = st.form_submit_button("💾 Save Invoice", use_container_width=True, type="primary")
            
            if submitted:
                # Validation
                errors = []
                if not sales_name:
                    errors.append("Sales Executive Name is required")
                if not customer_name:
                    errors.append("Customer Name is required")
                if not product_name:
                    errors.append("Product Name is required")
                if payment_method in ["Bank Transfer", "Cheque"] and not bank_name:
                    errors.append("Bank Name is required for Bank Transfer or Cheque payments")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    new_invoice = {
                        'OrderDate': pd.to_datetime(order_date),
                        'SalesID': sales_id,
                        'SalesName': sales_name,
                        'InvoiceNo': invoice_no if invoice_no else f"INV-{datetime.now().strftime('%Y%m%d')}-{sales_id}",
                        'CustomerName': customer_name,
                        'Gender': gender,
                        'CustomerID': customer_id if customer_id else f"CUST-{sales_id}",
                        'CustomerType': customer_type,
                        'ProductName': product_name,
                        'ProductCode': product_code if product_code else f"PRD-{sales_id}",
                        'ProductCategory': product_category,
                        'CategoryCode': category_code,
                        'UnitPrice': unit_price,
                        'Quantity': quantity,
                        'OrderValue': order_value,
                        'DiscountValue': discount_value,
                        'SalesValue': sales_value,
                        'SalesReturn': sales_return,
                        'CreditedAmount': credited_amount,
                        'Commission': commission,
                        'Year': year,
                        'Month': month,
                        'Day': day,
                        'NetSales': net_sales,
                        'DueAmount': due_amount
                    }
                    
                    df_sales = pd.concat([df_sales, pd.DataFrame([new_invoice])], ignore_index=True)
                    
                    if save_sales_data(df_sales):
                        st.success(f"✅ Invoice saved successfully! Invoice No: {new_invoice['InvoiceNo']}")
                        st.balloons()
                        st.cache_data.clear()
                        st.rerun()
        
        if st.button("Close Form"):
            st.session_state.show_sales_form = False
            st.rerun()
    
    # Display sales data with enhanced filters
    st.subheader("📋 Sales Invoices")
    
    # Convert OrderDate to datetime for the entire dataframe
    if 'OrderDate' in df_sales.columns and len(df_sales) > 0:
        df_sales['OrderDate'] = pd.to_datetime(df_sales['OrderDate'], errors='coerce')
    
    # Enhanced Filters
    st.markdown("### 🔍 Filters")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        status_filter = st.selectbox("Payment Status", ["All", "Paid", "Partial", "Due"])
    
    with col_f2:
        if len(df_sales) > 0 and 'SalesName' in df_sales.columns:
            sales_executives = ["All"] + sorted(df_sales['SalesName'].dropna().unique().tolist())
            executive_filter = st.selectbox("Sales Executive", sales_executives)
        else:
            executive_filter = "All"
    
    with col_f3:
        if len(df_sales) > 0 and 'CustomerName' in df_sales.columns:
            customers = ["All"] + sorted(df_sales['CustomerName'].dropna().unique().tolist())
            customer_filter = st.selectbox("Customer", customers)
        else:
            customer_filter = "All"
    
    with col_f4:
        if len(df_sales) > 0 and 'ProductCategory' in df_sales.columns:
            categories = ["All"] + sorted(df_sales['ProductCategory'].dropna().unique().tolist())
            category_filter = st.selectbox("Product Category", categories)
        else:
            category_filter = "All"
    
    # Date Range Filter
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col_date2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Apply filters
    filtered_df = df_sales.copy()
    
    # Ensure OrderDate is datetime
    if 'OrderDate' in filtered_df.columns and len(filtered_df) > 0:
        filtered_df['OrderDate'] = pd.to_datetime(filtered_df['OrderDate'], errors='coerce')
    
    # Status filter
    if status_filter != "All" and 'DueAmount' in filtered_df.columns:
        if status_filter == "Paid":
            filtered_df = filtered_df[filtered_df['DueAmount'] == 0]
        elif status_filter == "Due":
            filtered_df = filtered_df[filtered_df['DueAmount'] > 0]
        elif status_filter == "Partial":
            filtered_df = filtered_df[(filtered_df['DueAmount'] > 0) & (filtered_df['DueAmount'] < filtered_df['NetSales'])]
    
    # Executive filter
    if executive_filter != "All" and 'SalesName' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['SalesName'] == executive_filter]
    
    # Customer filter
    if customer_filter != "All" and 'CustomerName' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['CustomerName'] == customer_filter]
    
    # Category filter
    if category_filter != "All" and 'ProductCategory' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ProductCategory'] == category_filter]
    
    # Date range filter - FIXED: Handle datetime conversion properly
    if 'OrderDate' in filtered_df.columns and len(filtered_df) > 0:
        # Convert to datetime and drop any NaT values
        filtered_df['OrderDate'] = pd.to_datetime(filtered_df['OrderDate'], errors='coerce')
        filtered_df = filtered_df.dropna(subset=['OrderDate'])
        
        if len(filtered_df) > 0:
            start_datetime = pd.to_datetime(start_date)
            end_datetime = pd.to_datetime(end_date) + timedelta(days=1)  # Include the end date
            
            # Use .loc to avoid chained assignment issues
            mask = (filtered_df['OrderDate'] >= start_datetime) & (filtered_df['OrderDate'] <= end_datetime)
            filtered_df = filtered_df.loc[mask].copy()
    
    if len(filtered_df) > 0:
        # Summary metrics
        st.markdown("### 📊 Summary Metrics")
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        
        with col_m1:
            total_sales = filtered_df['NetSales'].sum() if 'NetSales' in filtered_df.columns else 0
            st.metric("💰 Total Sales", f"{total_sales:,.2f}")
        
        with col_m2:
            total_orders = filtered_df['InvoiceNo'].nunique() if 'InvoiceNo' in filtered_df.columns else 0
            st.metric("📦 Total Orders", total_orders)
        
        with col_m3:
            paid_amount = filtered_df[filtered_df['DueAmount'] == 0]['NetSales'].sum() if 'DueAmount' in filtered_df.columns and 'NetSales' in filtered_df.columns else 0
            st.metric("✅ Amount Received", f"{paid_amount:,.2f}")
        
        with col_m4:
            due_amount = filtered_df['DueAmount'].sum() if 'DueAmount' in filtered_df.columns else 0
            st.metric("⚠️ Due Amount", f"{due_amount:,.2f}")
        
        with col_m5:
            collection_rate = (paid_amount / total_sales * 100) if total_sales > 0 else 0
            st.metric("📈 Collection Rate", f"{collection_rate:.1f}%")
        
        # Sales by Executive Chart
        if 'SalesName' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            st.markdown("### 📊 Sales by Executive")
            executive_sales = filtered_df.groupby('SalesName')['NetSales'].sum().reset_index()
            executive_sales = executive_sales.sort_values('NetSales', ascending=True)
            
            if len(executive_sales) > 0:
                fig_exec = px.bar(
                    executive_sales,
                    x='NetSales',
                    y='SalesName',
                    orientation='h',
                    title="Sales Performance by Executive",
                    text='NetSales',
                    color='NetSales',
                    color_continuous_scale='Viridis'
                )
                fig_exec.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig_exec.update_layout(height=400)
                st.plotly_chart(fig_exec, use_container_width=True)
        
        # Sales by Category Chart
        if 'ProductCategory' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            st.markdown("### 📊 Sales by Product Category")
            category_sales = filtered_df.groupby('ProductCategory')['NetSales'].sum().reset_index()
            
            if len(category_sales) > 0:
                fig_category = px.pie(
                    category_sales,
                    values='NetSales',
                    names='ProductCategory',
                    title="Sales Distribution by Category",
                    hole=0.3,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_category, use_container_width=True)
        
        # Customer Type Analysis
        if 'CustomerType' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            st.markdown("### 👥 Customer Type Analysis")
            customer_type_sales = filtered_df.groupby('CustomerType')['NetSales'].sum().reset_index()
            
            if len(customer_type_sales) > 0:
                fig_customer_type = px.bar(
                    customer_type_sales,
                    x='CustomerType',
                    y='NetSales',
                    title="Sales by Customer Type",
                    text='NetSales',
                    color='CustomerType'
                )
                fig_customer_type.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig_customer_type, use_container_width=True)
        
        # Display data table
        st.markdown("### 📋 Sales Data Table")
        
        # Select columns for display
        display_columns = ['OrderDate', 'InvoiceNo', 'CustomerName', 'SalesName', 'ProductName', 
                          'Quantity', 'UnitPrice', 'NetSales', 'DueAmount']
        
        # Add payment status column for display
        if 'DueAmount' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            filtered_df['PaymentStatus'] = filtered_df.apply(
                lambda row: 'Paid' if row['DueAmount'] == 0 else ('Partial' if 0 < row['DueAmount'] < row['NetSales'] else 'Due'), 
                axis=1
            )
            display_columns.append('PaymentStatus')
        
        # Get available columns
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        if len(available_columns) > 0:
            # Sort by date
            display_df = filtered_df[available_columns].copy()
            if 'OrderDate' in display_df.columns:
                display_df = display_df.sort_values('OrderDate', ascending=False)
            
            # Format numeric columns
            format_dict = {}
            if 'UnitPrice' in display_df.columns:
                format_dict['UnitPrice'] = '{:,.2f}'
            if 'NetSales' in display_df.columns:
                format_dict['NetSales'] = '{:,.2f}'
            if 'DueAmount' in display_df.columns:
                format_dict['DueAmount'] = '{:,.2f}'
            
            if format_dict:
                st.dataframe(
                    display_df.style.format(format_dict),
                    use_container_width=True,
                    height=400
                )
            else:
                st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download buttons
        st.markdown("### 📥 Export Data")
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Filtered Data to CSV",
                csv,
                f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="export_sales_filtered"
            )
        
        with col_d2:
            if 'SalesName' in filtered_df.columns and 'NetSales' in filtered_df.columns:
                # Summary report
                summary_report = filtered_df.groupby('SalesName').agg({
                    'NetSales': 'sum',
                    'InvoiceNo': 'count' if 'InvoiceNo' in filtered_df.columns else 'SalesID',
                    'CustomerID': 'nunique' if 'CustomerID' in filtered_df.columns else 'CustomerName'
                }).reset_index() if 'InvoiceNo' in filtered_df.columns else pd.DataFrame()
                
                if len(summary_report) > 0:
                    summary_report.columns = ['Sales Executive', 'Total Sales', 'Orders', 'Unique Customers']
                    csv_summary = summary_report.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Executive Summary",
                        csv_summary,
                        f"executive_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key="export_executive_summary"
                    )
        
        # Due Report
        if 'DueAmount' in filtered_df.columns and due_amount > 0:
            st.markdown("### ⚠️ Due Report")
            due_invoices = filtered_df[filtered_df['DueAmount'] > 0].copy()
            
            # Select columns for due report
            due_columns = ['OrderDate', 'InvoiceNo', 'CustomerName', 'NetSales', 'DueAmount']
            available_due_cols = [col for col in due_columns if col in due_invoices.columns]
            
            if len(available_due_cols) > 0:
                due_invoices = due_invoices[available_due_cols]
                due_invoices = due_invoices.sort_values('DueAmount', ascending=False)
                
                st.warning(f"Total Due Amount: {due_amount:,.2f} from {len(due_invoices)} invoices")
                
                format_dict = {}
                if 'NetSales' in due_invoices.columns:
                    format_dict['NetSales'] = '{:,.2f}'
                if 'DueAmount' in due_invoices.columns:
                    format_dict['DueAmount'] = '{:,.2f}'
                
                if format_dict:
                    st.dataframe(
                        due_invoices.style.format(format_dict),
                        use_container_width=True
                    )
                else:
                    st.dataframe(due_invoices, use_container_width=True)
                
                # Due aging analysis
                if 'OrderDate' in due_invoices.columns:
                    due_invoices['OrderDate'] = pd.to_datetime(due_invoices['OrderDate'], errors='coerce')
                    due_invoices = due_invoices.dropna(subset=['OrderDate'])
                    
                    if len(due_invoices) > 0:
                        today = datetime.now()
                        due_invoices['Days Outstanding'] = (today - due_invoices['OrderDate']).dt.days
                        
                        due_invoices['Aging'] = pd.cut(
                            due_invoices['Days Outstanding'],
                            bins=[-1, 30, 60, 90, float('inf')],
                            labels=['0-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
                        )
                        
                        aging_summary = due_invoices.groupby('Aging', observed=True)['DueAmount'].sum().reset_index()
                        
                        if len(aging_summary) > 0:
                            fig_aging = px.bar(
                                aging_summary,
                                x='Aging',
                                y='DueAmount',
                                title="Due Aging Analysis",
                                text='DueAmount',
                                color='DueAmount',
                                color_continuous_scale='Reds'
                            )
                            fig_aging.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                            st.plotly_chart(fig_aging, use_container_width=True)
            
    else:
        st.info("No sales data found for the selected filters")


# ================= PURCHASE ENTRY PAGE =================
elif choice == "📦 Payable | Purchase Entry":
    st.markdown("<div class='main-header'>📦 Purchase Entry (Accounts Payable)</div>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("---")
        if st.button("➕ New Purchase Entry", use_container_width=True, type="primary"):
            st.session_state.show_purchase_form = True
    
    if st.session_state.get('show_purchase_form', False):
        with st.form("purchase_form", clear_on_submit=True):
            st.markdown("### New Purchase Entry")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Generate Purchase/PO Number
                if len(df_purchase) > 0 and 'PoNumber' in df_purchase.columns:
                    # Extract numeric part from PO numbers
                    po_numbers = df_purchase['PoNumber'].dropna().tolist()
                    if po_numbers:
                        last_po = po_numbers[-1]
                        try:
                            # Try to extract number from PO-202401-0001 format
                            new_id = int(last_po.split('-')[-1]) + 1
                        except:
                            new_id = len(df_purchase) + 1
                    else:
                        new_id = 1
                else:
                    new_id = 1
                
                po_number = st.text_input("PO Number", placeholder=f"PO-{datetime.now().strftime('%Y%m')}-{str(new_id).zfill(4)}")
                posted_date = st.date_input("Posted Date", value=datetime.now())
                vendor_name = st.text_input("Vendor Name *", placeholder="e.g., Creative Corporation")
                vendor_id = st.text_input("Vendor ID", placeholder=f"VND{str(new_id).zfill(3)}")
                
            with col2:
                invoice_no = st.text_input("Invoice No", placeholder=f"INV-{datetime.now().strftime('%Y%m%d')}-{new_id}")
                product_name = st.text_input("Product Name *")
                product_code = st.text_input("Product Code", placeholder=f"PRD-{new_id}")
                product_category = st.selectbox("Product Category", 
                                               ["Cosmetics", "Accessories", "Fashion Apparel", "Hygiene Products"])
                category_code = st.selectbox("Category Code", ["CAT001", "CAT002", "CAT003", "CAT004"])
            
            with col3:
                posted_no = st.text_input("Posted No", placeholder=f"ENT-{datetime.now().strftime('%Y%m%d')}-{str(new_id).zfill(5)}")
                payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Cheque", "Bkash", "Nagad"])
                bank_name = st.text_input("Bank Name", placeholder="Required if payment method is Bank Transfer")
            
            # Product & Pricing Details
            st.markdown("---")
            st.markdown("### 📊 Product & Pricing Details")
            
            col_price1, col_price2, col_price3 = st.columns(3)
            
            with col_price1:
                quantity = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
                unit_price = st.number_input("Unit Price (BDT)", min_value=0.0, value=0.0, step=100.0)
                order_value = quantity * unit_price
                st.info(f"**Order Value:** {order_value:,.2f}")
            
            with col_price2:
                discount_percent = st.slider("Discount (%)", min_value=0.0, max_value=50.0, value=0.0, step=1.0)
                discount_value = order_value * (discount_percent / 100)
                sales_value = order_value - discount_value
                st.info(f"**Sales Value:** {sales_value:,.2f}")
            
            with col_price3:
                sales_return = st.number_input("Sales Return (BDT)", min_value=0.0, value=0.0, step=50.0)
                debited_amount = sales_value - sales_return
                commission_percent = st.slider("Commission (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
                commission = debited_amount * (commission_percent / 100)
                net_sales = debited_amount - commission
            
            st.markdown(f"**💰 Net Sales Amount:** {net_sales:,.2f}")
            
            # Payment Details
            st.markdown("---")
            st.markdown("### 💳 Payment Details")
            
            col_pay1, col_pay2 = st.columns(2)
            
            with col_pay1:
                payment_status = st.selectbox("Payment Status", ["Paid", "Partial", "Due"])
                if payment_status == "Paid":
                    due_amount = 0
                elif payment_status == "Partial":
                    due_amount = net_sales * 0.5
                else:
                    due_amount = net_sales
                st.warning(f"**Due Amount:** {due_amount:,.2f}")
            
            with col_pay2:
                reference = st.text_input("Reference No", placeholder="Cheque no, UTR, Transaction ID")
            
            # Additional Info
            st.markdown("---")
            st.markdown("### 📝 Additional Information")
            
            col_rem1, col_rem2 = st.columns(2)
            
            with col_rem1:
                year = st.number_input("Year", value=datetime.now().year, step=1)
                month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1)
                day = st.number_input("Day", value=datetime.now().day, min_value=1, max_value=31)
            
            with col_rem2:
                remarks = st.text_area("Remarks", placeholder="Additional notes about the purchase")
                created_by = st.text_input("Created By", value="Admin")
            
            submitted = st.form_submit_button("💾 Save Purchase", use_container_width=True, type="primary")
            
            if submitted:
                # Validation
                errors = []
                if not vendor_name:
                    errors.append("Vendor Name is required")
                if not product_name:
                    errors.append("Product Name is required")
                if payment_method in ["Bank Transfer", "Cheque"] and not bank_name:
                    errors.append("Bank Name is required for Bank Transfer or Cheque payments")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    new_purchase = {
                        'PoNumber': po_number if po_number else f"PO-{datetime.now().strftime('%Y%m')}-{str(new_id).zfill(4)}",
                        'PostedDate': pd.to_datetime(posted_date),
                        'VendorID': vendor_id if vendor_id else f"VND{str(new_id).zfill(3)}",
                        'VendorName': vendor_name,
                        'InvoiceNo': invoice_no if invoice_no else f"INV-{datetime.now().strftime('%Y%m%d')}-{new_id}",
                        'ProductName': product_name,
                        'ProductCode': product_code if product_code else f"PRD-{new_id}",
                        'ProductCategory': product_category,
                        'CategoryCode': category_code,
                        'UnitPrice': unit_price,
                        'Quantity': quantity,
                        'OrderValue': order_value,
                        'DiscountValue': discount_value,
                        'SalesValue': sales_value,
                        'SalesReturn': sales_return,
                        'DebitedAmount': debited_amount,
                        'Commission': commission,
                        'Year': year,
                        'Month': month,
                        'Day': day,
                        'NetSales': net_sales,
                        'DueAmount': due_amount,
                        'PaymentMethods': payment_method,
                        'BankName': bank_name if payment_method in ["Bank Transfer", "Cheque"] else "",
                        'PostedNo': posted_no if posted_no else f"ENT-{datetime.now().strftime('%Y%m%d')}-{str(new_id).zfill(5)}"
                    }
                    
                    df_purchase = pd.concat([df_purchase, pd.DataFrame([new_purchase])], ignore_index=True)
                    
                    if save_purchase_data(df_purchase):
                        st.success(f"✅ Purchase saved! PO No: {new_purchase['PoNumber']}")
                        st.balloons()
                        st.cache_data.clear()
                        st.rerun()
        
        if st.button("Close Form"):
            st.session_state.show_purchase_form = False
            st.rerun()
    
    # Convert PostedDate to datetime for the entire dataframe
    if 'PostedDate' in df_purchase.columns and len(df_purchase) > 0:
        df_purchase['PostedDate'] = pd.to_datetime(df_purchase['PostedDate'], errors='coerce')
    
    # Display purchase data with enhanced filters
    st.subheader("📋 Purchase Orders (Accounts Payable)")
    
    # Enhanced Filters
    st.markdown("### 🔍 Filters")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        status_filter = st.selectbox("Payment Status", ["All", "Paid", "Partial", "Due"])
    
    with col_f2:
        if len(df_purchase) > 0 and 'VendorName' in df_purchase.columns:
            vendors = ["All"] + sorted(df_purchase['VendorName'].dropna().unique().tolist())
            vendor_filter = st.selectbox("Vendor", vendors)
        else:
            vendor_filter = "All"
    
    with col_f3:
        if len(df_purchase) > 0 and 'ProductCategory' in df_purchase.columns:
            categories = ["All"] + sorted(df_purchase['ProductCategory'].dropna().unique().tolist())
            category_filter = st.selectbox("Product Category", categories)
        else:
            category_filter = "All"
    
    with col_f4:
        if len(df_purchase) > 0 and 'PaymentMethods' in df_purchase.columns:
            payment_methods = ["All"] + sorted(df_purchase['PaymentMethods'].dropna().unique().tolist())
            payment_filter = st.selectbox("Payment Method", payment_methods)
        else:
            payment_filter = "All"
    
    # Date Range Filter
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col_date2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Apply filters
    filtered_df = df_purchase.copy()
    
    # Ensure PostedDate is datetime
    if 'PostedDate' in filtered_df.columns and len(filtered_df) > 0:
        filtered_df['PostedDate'] = pd.to_datetime(filtered_df['PostedDate'], errors='coerce')
        filtered_df = filtered_df.dropna(subset=['PostedDate'])
    
    # Status filter
    if status_filter != "All" and 'DueAmount' in filtered_df.columns:
        if status_filter == "Paid":
            filtered_df = filtered_df[filtered_df['DueAmount'] == 0]
        elif status_filter == "Due":
            filtered_df = filtered_df[filtered_df['DueAmount'] > 0]
        elif status_filter == "Partial":
            filtered_df = filtered_df[(filtered_df['DueAmount'] > 0) & (filtered_df['DueAmount'] < filtered_df['NetSales'])]
    
    # Vendor filter
    if vendor_filter != "All" and 'VendorName' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['VendorName'] == vendor_filter]
    
    # Category filter
    if category_filter != "All" and 'ProductCategory' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ProductCategory'] == category_filter]
    
    # Payment method filter
    if payment_filter != "All" and 'PaymentMethods' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['PaymentMethods'] == payment_filter]
    
    # Date range filter
    if 'PostedDate' in filtered_df.columns and len(filtered_df) > 0:
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + timedelta(days=1)
        mask = (filtered_df['PostedDate'] >= start_datetime) & (filtered_df['PostedDate'] <= end_datetime)
        filtered_df = filtered_df.loc[mask].copy()
    
    if len(filtered_df) > 0:
        # Summary metrics
        st.markdown("### 📊 Summary Metrics")
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        
        with col_m1:
            total_purchase = filtered_df['NetSales'].sum() if 'NetSales' in filtered_df.columns else 0
            st.metric("💰 Total Purchases", f"{total_purchase:,.2f}")
        
        with col_m2:
            total_orders = filtered_df['PoNumber'].nunique() if 'PoNumber' in filtered_df.columns else 0
            st.metric("📦 Total Orders", total_orders)
        
        with col_m3:
            paid_amount = filtered_df[filtered_df['DueAmount'] == 0]['NetSales'].sum() if 'DueAmount' in filtered_df.columns and 'NetSales' in filtered_df.columns else 0
            st.metric("✅ Amount Paid", f"{paid_amount:,.2f}")
        
        with col_m4:
            due_amount = filtered_df['DueAmount'].sum() if 'DueAmount' in filtered_df.columns else 0
            st.metric("⚠️ Amount Due", f"{due_amount:,.2f}")
        
        with col_m5:
            payment_rate = (paid_amount / total_purchase * 100) if total_purchase > 0 else 0
            st.metric("📈 Payment Rate", f"{payment_rate:.1f}%")
        
        # Purchase by Vendor Chart
        if 'VendorName' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            st.markdown("### 📊 Purchases by Vendor")
            vendor_purchases = filtered_df.groupby('VendorName')['NetSales'].sum().reset_index()
            vendor_purchases = vendor_purchases.sort_values('NetSales', ascending=True)
            
            if len(vendor_purchases) > 0:
                fig_vendor = px.bar(
                    vendor_purchases,
                    x='NetSales',
                    y='VendorName',
                    orientation='h',
                    title="Purchase Amount by Vendor",
                    text='NetSales',
                    color='NetSales',
                    color_continuous_scale='Viridis'
                )
                fig_vendor.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig_vendor.update_layout(height=400)
                st.plotly_chart(fig_vendor, use_container_width=True)
        
        # Purchase by Category Chart
        if 'ProductCategory' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            st.markdown("### 📊 Purchases by Product Category")
            category_purchases = filtered_df.groupby('ProductCategory')['NetSales'].sum().reset_index()
            
            if len(category_purchases) > 0:
                fig_category = px.pie(
                    category_purchases,
                    values='NetSales',
                    names='ProductCategory',
                    title="Purchase Distribution by Category",
                    hole=0.3,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_category, use_container_width=True)
        
        # Payment Method Distribution
        if 'PaymentMethods' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            st.markdown("### 💳 Payment Method Distribution")
            payment_dist = filtered_df.groupby('PaymentMethods')['NetSales'].sum().reset_index()
            
            if len(payment_dist) > 0:
                fig_payment = px.pie(
                    payment_dist,
                    values='NetSales',
                    names='PaymentMethods',
                    title="Purchase by Payment Method",
                    hole=0.3,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_payment, use_container_width=True)
        
        # Display data table
        st.markdown("### 📋 Purchase Data Table")
        
        # Select columns for display
        display_columns = ['PostedDate', 'PoNumber', 'InvoiceNo', 'VendorName', 'ProductName', 
                          'Quantity', 'UnitPrice', 'NetSales', 'DueAmount', 'PaymentMethods']
        
        # Add payment status column for display
        if 'DueAmount' in filtered_df.columns and 'NetSales' in filtered_df.columns:
            filtered_df['PaymentStatus'] = filtered_df.apply(
                lambda row: 'Paid' if row['DueAmount'] == 0 else ('Partial' if 0 < row['DueAmount'] < row['NetSales'] else 'Due'), 
                axis=1
            )
            display_columns.append('PaymentStatus')
        
        # Get available columns
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        
        if len(available_columns) > 0:
            # Sort by date
            display_df = filtered_df[available_columns].copy()
            if 'PostedDate' in display_df.columns:
                display_df = display_df.sort_values('PostedDate', ascending=False)
            
            # Format numeric columns
            format_dict = {}
            if 'UnitPrice' in display_df.columns:
                format_dict['UnitPrice'] = '{:,.2f}'
            if 'NetSales' in display_df.columns:
                format_dict['NetSales'] = '{:,.2f}'
            if 'DueAmount' in display_df.columns:
                format_dict['DueAmount'] = '{:,.2f}'
            
            if format_dict:
                st.dataframe(
                    display_df.style.format(format_dict),
                    use_container_width=True,
                    height=400
                )
            else:
                st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download buttons
        st.markdown("### 📥 Export Data")
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Filtered Data to CSV",
                csv,
                f"purchase_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="export_purchase_filtered"
            )
        
        with col_d2:
            if 'VendorName' in filtered_df.columns and 'NetSales' in filtered_df.columns:
                # Vendor summary report
                vendor_summary = filtered_df.groupby('VendorName').agg({
                    'NetSales': 'sum',
                    'PoNumber': 'count',
                    'DueAmount': 'sum'
                }).reset_index() if 'PoNumber' in filtered_df.columns else pd.DataFrame()
                
                if len(vendor_summary) > 0:
                    vendor_summary.columns = ['Vendor', 'Total Purchase', 'Orders', 'Due Amount']
                    csv_summary = vendor_summary.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Vendor Summary",
                        csv_summary,
                        f"vendor_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key="export_vendor_summary"
                    )
        
        # Due Report
        if 'DueAmount' in filtered_df.columns and due_amount > 0:
            st.markdown("### ⚠️ Due Report")
            due_invoices = filtered_df[filtered_df['DueAmount'] > 0].copy()
            
            # Select columns for due report
            due_columns = ['PostedDate', 'PoNumber', 'InvoiceNo', 'VendorName', 'NetSales', 'DueAmount']
            available_due_cols = [col for col in due_columns if col in due_invoices.columns]
            
            if len(available_due_cols) > 0:
                due_invoices = due_invoices[available_due_cols]
                due_invoices = due_invoices.sort_values('DueAmount', ascending=False)
                
                st.warning(f"Total Due Amount: {due_amount:,.2f} from {len(due_invoices)} invoices")
                
                format_dict = {}
                if 'NetSales' in due_invoices.columns:
                    format_dict['NetSales'] = '{:,.2f}'
                if 'DueAmount' in due_invoices.columns:
                    format_dict['DueAmount'] = '{:,.2f}'
                
                if format_dict:
                    st.dataframe(
                        due_invoices.style.format(format_dict),
                        use_container_width=True
                    )
                else:
                    st.dataframe(due_invoices, use_container_width=True)
                
                # Due aging analysis
                if 'PostedDate' in due_invoices.columns:
                    due_invoices['PostedDate'] = pd.to_datetime(due_invoices['PostedDate'], errors='coerce')
                    due_invoices = due_invoices.dropna(subset=['PostedDate'])
                    
                    if len(due_invoices) > 0:
                        today = datetime.now()
                        due_invoices['Days Outstanding'] = (today - due_invoices['PostedDate']).dt.days
                        
                        due_invoices['Aging'] = pd.cut(
                            due_invoices['Days Outstanding'],
                            bins=[-1, 30, 60, 90, float('inf')],
                            labels=['0-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
                        )
                        
                        aging_summary = due_invoices.groupby('Aging', observed=True)['DueAmount'].sum().reset_index()
                        
                        if len(aging_summary) > 0:
                            fig_aging = px.bar(
                                aging_summary,
                                x='Aging',
                                y='DueAmount',
                                title="Due Aging Analysis",
                                text='DueAmount',
                                color='DueAmount',
                                color_continuous_scale='Reds'
                            )
                            fig_aging.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                            st.plotly_chart(fig_aging, use_container_width=True)
            
    else:
        st.info("No purchase data found for the selected filters")

# ================= END OF PURCHASE ENTRY PAGE =================
# ================= VENDOR PAYABLE MANAGEMENT PAGE =================
# ================= VENDOR PAYABLE MANAGEMENT PAGE =================
elif choice == "🏢 Vendor Payable Management":
    st.markdown("<div class='main-header'>🏢 Vendor Payable Account Management System</div>", unsafe_allow_html=True)
    
    # Convert PostedDate to datetime if needed
    if 'PostedDate' in df_purchase.columns and len(df_purchase) > 0:
        df_purchase['PostedDate'] = pd.to_datetime(df_purchase['PostedDate'], errors='coerce')
    
    if len(df_purchase) > 0:
        # Vendor Selection
        st.sidebar.markdown("---")
        st.sidebar.subheader("🏢 Select Vendor")
        
        if 'VendorName' in df_purchase.columns:
            vendors = sorted(df_purchase['VendorName'].dropna().unique().tolist())
            selected_vendor = st.sidebar.selectbox("Choose Vendor", vendors)
            
            if selected_vendor:
                vendor_data = df_purchase[df_purchase['VendorName'] == selected_vendor].copy()
                
                # Vendor Summary Cards
                st.subheader(f"📋 Vendor Details: {selected_vendor}")
                
                col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns(5)
                
                with col_v1:
                    total_purchase = vendor_data['NetSales'].sum() if 'NetSales' in vendor_data.columns else 0
                    st.metric("💰 Total Purchase", f"{total_purchase:,.2f}")
                
                with col_v2:
                    total_due = vendor_data['DueAmount'].sum() if 'DueAmount' in vendor_data.columns else 0
                    st.metric("⚠️ Due Amount", f"{total_due:,.2f}", 
                             delta="Payable" if total_due > 0 else "Settled")
                
                with col_v3:
                    total_orders = vendor_data['PoNumber'].nunique() if 'PoNumber' in vendor_data.columns else 0
                    st.metric("📦 Total Orders", total_orders)
                
                with col_v4:
                    if 'PostedDate' in vendor_data.columns:
                        last_purchase = vendor_data['PostedDate'].max()
                        last_purchase_date = last_purchase.strftime('%Y-%m-%d') if pd.notna(last_purchase) else 'N/A'
                        st.metric("📅 Last Purchase", last_purchase_date)
                    else:
                        st.metric("📅 Last Purchase", "N/A")
                
                with col_v5:
                    # Calculate average days between purchases
                    if len(vendor_data) > 1 and 'PostedDate' in vendor_data.columns:
                        dates = vendor_data['PostedDate'].sort_values()
                        avg_days = (dates.diff().dt.days).mean()
                        st.metric("⏱️ Avg Purchase Frequency", f"{avg_days:.0f} days" if pd.notna(avg_days) else "N/A")
                    else:
                        st.metric("⏱️ Avg Purchase Frequency", "N/A")
                
                # Payment Performance
                st.markdown("---")
                st.subheader("📊 Payment Performance")
                
                col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                
                with col_p1:
                    paid_amount = total_purchase - total_due
                    payment_rate = (paid_amount / total_purchase * 100) if total_purchase > 0 else 0
                    st.metric("✅ Payment Rate", f"{payment_rate:.1f}%")
                
                with col_p2:
                    avg_order_value = total_purchase / total_orders if total_orders > 0 else 0
                    st.metric("💰 Avg Order Value", f"{avg_order_value:,.2f}")
                
                with col_p3:
                    # Calculate total discount received
                    total_discount = vendor_data['DiscountValue'].sum() if 'DiscountValue' in vendor_data.columns else 0
                    st.metric("🎯 Total Discount", f"{total_discount:,.2f}")
                
                with col_p4:
                    # Calculate total commission
                    total_commission = vendor_data['Commission'].sum() if 'Commission' in vendor_data.columns else 0
                    st.metric("💵 Total Commission", f"{total_commission:,.2f}")
                
                # Transaction History
                st.markdown("---")
                st.subheader("📜 Transaction History")
                
                # Select columns for history
                history_columns = ['PostedDate', 'PoNumber', 'InvoiceNo', 'ProductName', 
                                  'Quantity', 'UnitPrice', 'NetSales', 'DueAmount', 'PaymentMethods']
                available_history_cols = [col for col in history_columns if col in vendor_data.columns]
                
                if len(available_history_cols) > 0:
                    history_df = vendor_data[available_history_cols].copy()
                    history_df = history_df.sort_values('PostedDate', ascending=False) if 'PostedDate' in history_df.columns else history_df
                    
                    # Rename columns for display
                    rename_map = {
                        'PostedDate': 'Date',
                        'PoNumber': 'PO No',
                        'InvoiceNo': 'Invoice No',
                        'ProductName': 'Product',
                        'Quantity': 'Qty',
                        'UnitPrice': 'Unit Price',
                        'NetSales': 'Amount',
                        'DueAmount': 'Due',
                        'PaymentMethods': 'Payment Method'
                    }
                    history_df = history_df.rename(columns={k: v for k, v in rename_map.items() if k in history_df.columns})
                    
                    # Add payment status column
                    if 'Due' in history_df.columns and 'Amount' in history_df.columns:
                        history_df['Status'] = history_df.apply(
                            lambda row: 'Paid' if row['Due'] == 0 else ('Partial' if 0 < row['Due'] < row['Amount'] else 'Due'), 
                            axis=1
                        )
                    
                    # Color code status
                    def color_status(val):
                        if val == 'Paid':
                            return 'color: green; font-weight: bold'
                        elif val == 'Due':
                            return 'color: red; font-weight: bold'
                        elif val == 'Partial':
                            return 'color: orange; font-weight: bold'
                        return ''
                    
                    # Format currency columns
                    format_dict = {}
                    if 'Unit Price' in history_df.columns:
                        format_dict['Unit Price'] = '{:,.2f}'
                    if 'Amount' in history_df.columns:
                        format_dict['Amount'] = '{:,.2f}'
                    if 'Due' in history_df.columns:
                        format_dict['Due'] = '{:,.2f}'
                    
                    if 'Status' in history_df.columns:
                        st.dataframe(
                            history_df.style.applymap(color_status, subset=['Status']).format(format_dict),
                            use_container_width=True,
                            height=400
                        )
                    else:
                        st.dataframe(history_df.style.format(format_dict), use_container_width=True, height=400)
                else:
                    st.info("No transaction history available")
                
                # Due Analysis
                due_orders = vendor_data[vendor_data['DueAmount'] > 0].copy() if 'DueAmount' in vendor_data.columns else pd.DataFrame()
                
                if len(due_orders) > 0:
                    st.markdown("---")
                    st.subheader("⚠️ Due Analysis & Payment Schedule")
                    
                    # Aging Analysis
                    today = datetime.now()
                    
                    # Use PostedDate for aging if available
                    if 'PostedDate' in due_orders.columns:
                        due_orders['Days Outstanding'] = (today - due_orders['PostedDate']).dt.days
                    else:
                        due_orders['Days Outstanding'] = 0
                    
                    due_orders['Days Outstanding'] = due_orders['Days Outstanding'].apply(lambda x: max(0, x))
                    
                    due_orders['Aging'] = pd.cut(
                        due_orders['Days Outstanding'],
                        bins=[-1, 30, 60, 90, float('inf')],
                        labels=['0-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
                    )
                    
                    aging_summary = due_orders.groupby('Aging', observed=True)['DueAmount'].sum().reset_index()
                    
                    col_a1, col_a2 = st.columns(2)
                    
                    with col_a1:
                        fig_aging = px.bar(
                            aging_summary,
                            x='Aging',
                            y='DueAmount',
                            title="Due Aging Analysis",
                            text='DueAmount',
                            color='Aging',
                            color_discrete_sequence=['#4ECDC4', '#FFB86B', '#FF6B6B', '#C45C5C']
                        )
                        fig_aging.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                        fig_aging.update_layout(height=400)
                        st.plotly_chart(fig_aging, use_container_width=True)
                    
                    with col_a2:
                        # Calculate amounts for each aging category
                        amount_0_30 = aging_summary[aging_summary['Aging'] == '0-30 Days']['DueAmount'].sum() if len(aging_summary[aging_summary['Aging'] == '0-30 Days']) > 0 else 0
                        amount_31_60 = aging_summary[aging_summary['Aging'] == '31-60 Days']['DueAmount'].sum() if len(aging_summary[aging_summary['Aging'] == '31-60 Days']) > 0 else 0
                        amount_61_90 = aging_summary[aging_summary['Aging'] == '61-90 Days']['DueAmount'].sum() if len(aging_summary[aging_summary['Aging'] == '61-90 Days']) > 0 else 0
                        amount_90_plus = aging_summary[aging_summary['Aging'] == '90+ Days']['DueAmount'].sum() if len(aging_summary[aging_summary['Aging'] == '90+ Days']) > 0 else 0
                        
                        st.markdown("### 📅 Recommended Payment Plan")
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    color: white; border-radius: 10px; padding: 20px; margin: 10px 0;'>
                            <ul style='list-style-type: none; padding-left: 0;'>
                                <li><strong>🔴 Urgent (90+ days):</strong> {amount_90_plus:,.2f}</li>
                                <li><strong>🟠 Critical (61-90 days):</strong> {amount_61_90:,.2f}</li>
                                <li><strong>🟡 Normal (31-60 days):</strong> {amount_31_60:,.2f}</li>
                                <li><strong>🟢 Current (0-30 days):</strong> {amount_0_30:,.2f}</li>
                            </ul>
                            <hr style='margin: 15px 0; border-color: rgba(255,255,255,0.3);'>
                            <p><strong>💡 Suggested Action:</strong><br>
                            {'Pay urgent dues immediately' if amount_90_plus > 0 else 'No urgent payments required'}<br>
                            {'Schedule payments for critical dues within this week' if amount_61_90 > 0 else ''}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Due orders table
                    with st.expander("📋 View Due Orders Details"):
                        due_columns = ['PostedDate', 'PoNumber', 'InvoiceNo', 'ProductName', 'NetSales', 'DueAmount', 'Days Outstanding', 'Aging']
                        available_due_cols = [col for col in due_columns if col in due_orders.columns]
                        
                        if len(available_due_cols) > 0:
                            due_display = due_orders[available_due_cols].copy()
                            due_display = due_display.sort_values('Days Outstanding', ascending=False)
                            
                            format_dict = {}
                            if 'NetSales' in due_display.columns:
                                format_dict['NetSales'] = '{:,.2f}'
                            if 'DueAmount' in due_display.columns:
                                format_dict['DueAmount'] = '{:,.2f}'
                            
                            st.dataframe(
                                due_display.style.format(format_dict),
                                use_container_width=True
                            )
                else:
                    st.success("✅ No outstanding dues for this vendor")
                
                # Product Analysis for this vendor
                st.markdown("---")
                st.subheader("📦 Product Analysis")
                
                if 'ProductName' in vendor_data.columns and 'NetSales' in vendor_data.columns:
                    product_summary = vendor_data.groupby('ProductName').agg({
                        'NetSales': 'sum',
                        'Quantity': 'sum' if 'Quantity' in vendor_data.columns else 'NetSales',
                        'PoNumber': 'count'
                    }).reset_index()
                    
                    product_summary.columns = ['Product', 'Total Purchase', 'Quantity', 'Orders']
                    product_summary = product_summary.sort_values('Total Purchase', ascending=False).head(10)
                    
                    col_pr1, col_pr2 = st.columns(2)
                    
                    with col_pr1:
                        fig_top_products = px.bar(
                            product_summary.head(10),
                            x='Total Purchase',
                            y='Product',
                            orientation='h',
                            title="Top Products by Purchase Value",
                            text='Total Purchase',
                            color='Total Purchase',
                            color_continuous_scale='Viridis'
                        )
                        fig_top_products.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                        fig_top_products.update_layout(height=400)
                        st.plotly_chart(fig_top_products, use_container_width=True)
                    
                    with col_pr2:
                        # Payment method distribution for this vendor
                        if 'PaymentMethods' in vendor_data.columns:
                            payment_dist = vendor_data.groupby('PaymentMethods')['NetSales'].sum().reset_index()
                            fig_payment = px.pie(
                                payment_dist,
                                values='NetSales',
                                names='PaymentMethods',
                                title="Payment Method Distribution",
                                hole=0.3,
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            st.plotly_chart(fig_payment, use_container_width=True)
                
                # Download Vendor Statement
                st.markdown("---")
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    csv_statement = vendor_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {selected_vendor} Statement",
                        data=csv_statement,
                        file_name=f"{selected_vendor}_statement_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_vendor_statement"
                    )
                
                with col_dl2:
                    # Summary report for this vendor
                    summary_data = {
                        'Metric': ['Total Purchase', 'Total Due', 'Payment Rate', 'Total Orders', 'Avg Order Value'],
                        'Value': [
                            f"{total_purchase:,.2f}",
                            f"{total_due:,.2f}",
                            f"{payment_rate:.1f}%",
                            total_orders,
                            f"{avg_order_value:,.2f}"
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    csv_summary = summary_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {selected_vendor} Summary",
                        data=csv_summary,
                        file_name=f"{selected_vendor}_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="download_vendor_summary"
                    )
        
        # All Vendors Summary
        st.markdown("---")
        st.subheader("🏢 All Vendors Payable Summary")
        
        # Create vendor summary with correct column names
        vendor_summary = df_purchase.groupby('VendorName').agg({
            'NetSales': 'sum' if 'NetSales' in df_purchase.columns else 'OrderValue',
            'PoNumber': 'count' if 'PoNumber' in df_purchase.columns else 'VendorName',
            'DueAmount': 'sum' if 'DueAmount' in df_purchase.columns else 'NetSales'
        }).reset_index()
        
        vendor_summary.columns = ['Vendor', 'Total Purchase', 'Orders', 'Due Amount']
        vendor_summary['Paid Amount'] = vendor_summary['Total Purchase'] - vendor_summary['Due Amount']
        vendor_summary['Payment Rate'] = (vendor_summary['Paid Amount'] / vendor_summary['Total Purchase'] * 100).round(1)
        vendor_summary = vendor_summary.sort_values('Due Amount', ascending=False)
        
        # Add last purchase date for each vendor
        if 'PostedDate' in df_purchase.columns and 'VendorName' in df_purchase.columns:
            last_purchase_dates = df_purchase.groupby('VendorName')['PostedDate'].max()
            vendor_summary['Last Purchase'] = vendor_summary['Vendor'].map(
                lambda x: last_purchase_dates[x].strftime('%Y-%m-%d') if pd.notna(last_purchase_dates.get(x)) else 'N/A'
            )
        
        st.dataframe(
            vendor_summary.style.format({
                'Total Purchase': '{:,.2f}',
                'Due Amount': '{:,.2f}',
                'Paid Amount': '{:,.2f}',
                'Payment Rate': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        # Visualizations for all vendors
        st.markdown("### 📊 Vendor Analysis")
        
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            # Top 10 vendors by due amount
            top_due_vendors = vendor_summary.nlargest(10, 'Due Amount')
            if len(top_due_vendors) > 0:
                fig_due = px.bar(
                    top_due_vendors,
                    x='Due Amount',
                    y='Vendor',
                    orientation='h',
                    title="Top 10 Vendors by Due Amount",
                    text='Due Amount',
                    color='Due Amount',
                    color_continuous_scale='Reds'
                )
                fig_due.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig_due.update_layout(height=400)
                st.plotly_chart(fig_due, use_container_width=True)
        
        with col_viz2:
            # Payment rate distribution
            fig_payment_rate = px.bar(
                vendor_summary.nlargest(10, 'Total Purchase'),
                x='Vendor',
                y='Payment Rate',
                title="Payment Rate by Vendor",
                text='Payment Rate',
                color='Payment Rate',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig_payment_rate.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_payment_rate.update_layout(height=400)
            st.plotly_chart(fig_payment_rate, use_container_width=True)
        
        # Export all vendors
        st.markdown("---")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            csv_all_vendors = vendor_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download All Vendors Summary",
                csv_all_vendors,
                f"all_vendors_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="export_all_vendors"
            )
        
        with col_exp2:
            csv_full_data = df_purchase.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Complete Purchase Data",
                csv_full_data,
                f"complete_purchase_data_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key="export_complete_purchase"
            )
        
    else:
        st.info("No purchase data available. Please add purchase transactions first.")

# ================= END OF VENDOR PAYABLE MANAGEMENT PAGE =================


# ================= REPORTS DASHBOARD =================
elif choice == "📊 Reports Dashboard":
    st.markdown("<div class='main-header'>📊 Reports Dashboard</div>", unsafe_allow_html=True)
    
    # Date range selector for all reports
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col_date2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Financial Summary
    st.subheader("💰 Financial Summary")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    
    # Filter data by date
    fin_filtered = df_financial[(df_financial['transaction_date'] >= pd.to_datetime(start_date)) & 
                                 (df_financial['transaction_date'] <= pd.to_datetime(end_date))] if len(df_financial) > 0 else pd.DataFrame()
    
    sales_filtered = df_sales[(df_sales['invoice_date'] >= pd.to_datetime(start_date)) & 
                               (df_sales['invoice_date'] <= pd.to_datetime(end_date))] if len(df_sales) > 0 else pd.DataFrame()
    
    purchase_filtered = df_purchase[(df_purchase['purchase_date'] >= pd.to_datetime(start_date)) & 
                                     (df_purchase['purchase_date'] <= pd.to_datetime(end_date))] if len(df_purchase) > 0 else pd.DataFrame()
    
    with col_r1:
        total_income = fin_filtered['debit'].sum() if len(fin_filtered) > 0 else 0
        st.metric("Total Income", f"{total_income:,.2f}")
    
    with col_r2:
        total_expense = fin_filtered['credit'].sum() if len(fin_filtered) > 0 else 0
        st.metric("Total Expense", f"{total_expense:,.2f}")
    
    with col_r3:
        total_sales = sales_filtered['net_amount'].sum() if len(sales_filtered) > 0 else 0
        st.metric("Total Sales", f"{total_sales:,.2f}")
    
    with col_r4:
        total_purchase = purchase_filtered['net_amount'].sum() if len(purchase_filtered) > 0 else 0
        st.metric("Total Purchases", f"{total_purchase:,.2f}")
    
    # Charts
    col_ch1, col_ch2 = st.columns(2)
    
    with col_ch1:
        # Income vs Expense Bar Chart
        if len(fin_filtered) > 0:
            fin_filtered['month'] = fin_filtered['transaction_date'].dt.to_period('M').astype(str)
            monthly_summary = fin_filtered.groupby('month', as_index=False).agg(
                income=('debit', 'sum'),
                expense=('credit', 'sum')
            )
            
            fig = px.bar(monthly_summary, x='month', y=['income', 'expense'],
                        barmode='group', title="Monthly Income vs Expense",
                        labels={'value': 'Amount (BDT)', 'month': 'Month', 'variable': 'Type'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col_ch2:
        # Payment Status Pie Chart
        if len(sales_filtered) > 0:
            payment_summary = sales_filtered.groupby('payment_status')['net_amount'].sum().reset_index()
            fig = px.pie(payment_summary, values='net_amount', names='payment_status',
                        title="Sales by Payment Status", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
    
    # Accounts Receivable (Due from Customers)
    st.subheader("📥 Accounts Receivable (Customer Dues)")
    if len(df_sales) > 0:
        due_customers = df_sales[df_sales['payment_status'] == 'Due'].groupby('customer_name').agg({
            'net_amount': 'sum',
            'invoice_no': 'count'
        }).reset_index()
        due_customers.columns = ['Customer Name', 'Due Amount', 'Invoice Count']
        
        if len(due_customers) > 0:
            st.dataframe(due_customers, use_container_width=True)
            st.metric("Total Accounts Receivable", f"{due_customers['Due Amount'].sum():,.2f}")
        else:
            st.info("No customer dues found")
    
    # Accounts Payable (Due to Suppliers)
    st.subheader("📂 Accounts Payable (Supplier Dues)")
    if len(df_purchase) > 0:
        due_suppliers = df_purchase[df_purchase['payment_status'] == 'Due'].groupby('supplier_name').agg({
            'net_amount': 'sum',
            'purchase_no': 'count'
        }).reset_index()
        due_suppliers.columns = ['Supplier Name', 'Due Amount', 'Purchase Count']
        
        if len(due_suppliers) > 0:
            st.dataframe(due_suppliers, use_container_width=True)
            st.metric("Total Accounts Payable", f"{due_suppliers['Due Amount'].sum():,.2f}")
        else:
            st.info("No supplier dues found")
    
    # Top Customers and Products
    st.subheader("🏆 Top Performers")
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        if len(df_sales) > 0:
            top_customers = df_sales.groupby('customer_name')['net_amount'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(x=top_customers.values, y=top_customers.index, orientation='h',
                        title="Top 10 Customers by Sales", labels={'x': 'Sales (BDT)', 'y': 'Customer'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col_top2:
        if len(df_sales) > 0:
            top_products = df_sales.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(x=top_products.values, y=top_products.index, orientation='h',
                        title="Top 10 Products by Quantity", labels={'x': 'Quantity Sold', 'y': 'Product'})
            st.plotly_chart(fig, use_container_width=True)

# ================= FOOTER =================
st.sidebar.markdown("---")
st.sidebar.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")