import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Financial App", layout="wide")

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
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    """Load and prepare the financial data"""
    try:
        df = pd.read_csv("data/financial_transactions.csv")
        
        # Rename columns to match expected format if needed
        if 'OrderDate' in df.columns and 'date' not in df.columns:
            df['date'] = pd.to_datetime(df['OrderDate'])
        
        # Ensure numeric columns
        for col in ['debit', 'credit', 'amount']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Create bank-related columns if they don't exist
        if 'bank_deposit' not in df.columns:
            # Derive from payment_method or bank_name
            df['bank_deposit'] = df.apply(
                lambda row: row['credit'] if row.get('payment_method') == 'Bank Transfer' and row['credit'] > 0 else 0, 
                axis=1
            )
            df['bank_withdrawal'] = df.apply(
                lambda row: row['debit'] if row.get('payment_method') == 'Bank Transfer' and row['debit'] > 0 else 0, 
                axis=1
            )
        
        # Create description if not exists
        if 'description' not in df.columns:
            df['description'] = df['remarks'].fillna(df['account_head']).fillna('Transaction')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load the data
df = load_data()

# --- Ensure Numeric Columns ---
for col in ['debit', 'credit', 'bank_deposit', 'bank_withdrawal']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- Current Balance Calculation ---
if len(df) > 0:
    total_cash = df['debit'].sum() - df['credit'].sum()
    total_bank = df['bank_deposit'].sum() - df['bank_withdrawal'].sum()
    total_balance = total_cash + total_bank
else:
    total_cash = total_bank = total_balance = 0

# --- Header ---
st.markdown("<div class='main-header'>🏠 Welcome to Financial App</div>", unsafe_allow_html=True)

# --- Filters Sidebar ---
st.sidebar.header("🔍 Filters")

# Date range filter
if 'date' in df.columns and len(df) > 0:
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        mask = (df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))
        df_filtered = df[mask].copy()
    else:
        df_filtered = df.copy()
else:
    df_filtered = df.copy()

# Account type filter
if 'account_type' in df_filtered.columns:
    account_types = ['All'] + sorted(df_filtered['account_type'].dropna().unique().tolist())
    selected_type = st.sidebar.selectbox("Account Type", account_types)
    if selected_type != 'All':
        df_filtered = df_filtered[df_filtered['account_type'] == selected_type]

# Category filter
if 'category' in df_filtered.columns:
    categories = ['All'] + sorted(df_filtered['category'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    if selected_category != 'All':
        df_filtered = df_filtered[df_filtered['category'] == selected_category]

# Payment method filter
if 'payment_method' in df_filtered.columns:
    payment_methods = ['All'] + sorted(df_filtered['payment_method'].dropna().unique().tolist())
    selected_payment = st.sidebar.selectbox("Payment Method", payment_methods)
    if selected_payment != 'All':
        df_filtered = df_filtered[df_filtered['payment_method'] == selected_payment]

# --- Metrics Row ---
col_metric1, col_metric2, col_metric3 = st.columns(3)

with col_metric1:
    cash_balance = df_filtered['debit'].sum() - df_filtered['credit'].sum()
    st.metric("💵 Total Cash Balance", f"{cash_balance:,.2f}", 
              delta=f"{((cash_balance - total_cash)/total_cash*100 if total_cash != 0 else 0):.1f}% vs total" if total_cash != 0 else None)

with col_metric2:
    bank_balance = df_filtered['bank_deposit'].sum() - df_filtered['bank_withdrawal'].sum()
    st.metric("🏦 Total Bank Balance", f"{bank_balance:,.2f}")

with col_metric3:
    current_balance = cash_balance + bank_balance
    st.metric("💳 Current Balance", f"{current_balance:,.2f}")

# --- Features ---
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

# --- Monthly Income & Expense Chart ---
if 'date' in df_filtered.columns and len(df_filtered) > 0:
    df_filtered['month'] = df_filtered['date'].dt.to_period('M').astype(str)

    monthly_summary = df_filtered.groupby('month', as_index=False).agg(
        total_income=('debit', 'sum'),
        total_expense=('credit', 'sum')
    )

    fig = px.bar(
        monthly_summary,
        x='month',
        y=['total_income', 'total_expense'],
        barmode='group',
        title="📅 Monthly Income vs Expense",
        labels={"value": "Amount (₹)", "month": "Month", "variable": "Type"},
        color_discrete_map={'total_income': '#2ECC71', 'total_expense': '#E74C3C'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- Additional Insights ---
st.subheader("📊 Quick Insights")
col_insight1, col_insight2, col_insight3, col_insight4 = st.columns(4)

with col_insight1:
    total_income = df_filtered['debit'].sum()
    st.metric("💰 Total Income", f"{total_income:,.2f}")
    
with col_insight2:
    total_expense = df_filtered['credit'].sum()
    st.metric("💸 Total Expense", f"{total_expense:,.2f}")
    
with col_insight3:
    savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
    st.metric("📈 Savings Rate", f"{savings_rate:.1f}%")
    
with col_insight4:
    transaction_count = len(df_filtered)
    st.metric("📊 Transactions", f"{transaction_count:,}")

# --- Category-wise Breakdown ---
st.subheader("📊 Category-wise Analysis")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    if 'category' in df_filtered.columns:
        category_income = df_filtered[df_filtered['debit'] > 0].groupby('category')['debit'].sum().sort_values(ascending=True)
        if len(category_income) > 0:
            fig_pie = px.pie(
                values=category_income.values,
                names=category_income.index,
                title="Expense by Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    if 'category' in df_filtered.columns:
        category_expense = df_filtered[df_filtered['credit'] > 0].groupby('category')['credit'].sum().sort_values(ascending=True)
        if len(category_expense) > 0:
            fig_pie = px.pie(
                values=category_expense.values,
                names=category_expense.index,
                title="Income by Category",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_pie, use_container_width=True)

# --- Recent Transactions ---
st.subheader("📋 Recent Transactions")
if len(df_filtered) > 0:
    # Select columns to display
    display_cols = ['date', 'voucher_no', 'account_head', 'category', 'party_name', 
                    'payment_method', 'debit', 'credit', 'remarks']
    
    # Only use columns that exist
    available_cols = [col for col in display_cols if col in df_filtered.columns]
    
    recent_df = df_filtered[available_cols].tail(10)
    
    # Format the dataframe
    if 'date' in recent_df.columns:
        recent_df['date'] = recent_df['date'].dt.strftime('%Y-%m-%d')
    
    # Rename columns for display
    rename_map = {
        'date': 'Date',
        'voucher_no': 'Voucher No',
        'account_head': 'Account Head',
        'category': 'Category',
        'party_name': 'Party Name',
        'payment_method': 'Payment Method',
        'debit': 'Debit (Income)',
        'credit': 'Credit (Expense)',
        'remarks': 'Remarks'
    }
    recent_df = recent_df.rename(columns={k: v for k, v in rename_map.items() if k in recent_df.columns})
    
    st.dataframe(recent_df, use_container_width=True)

# --- Data Upload Option ---
st.sidebar.markdown("---")
st.sidebar.header("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_new = pd.read_csv(uploaded_file)
        else:
            df_new = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ Data loaded successfully!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")

# --- Export Option ---
if len(df_filtered) > 0:
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Export Filtered Data to CSV",
        data=csv,
        file_name="financial_data_export.csv",
        mime="text/csv"
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Summary Stats")
st.sidebar.markdown(f"""
- **Total Records**: {len(df_filtered):,}
- **Date Range**: {df_filtered['date'].min().strftime('%Y-%m-%d') if 'date' in df_filtered.columns and len(df_filtered) > 0 else 'N/A'} to {df_filtered['date'].max().strftime('%Y-%m-%d') if 'date' in df_filtered.columns and len(df_filtered) > 0 else 'N/A'}
- **Avg Transaction**: ₹{(df_filtered['debit'].sum() + df_filtered['credit'].sum()) / len(df_filtered):,.2f} if len(df_filtered) > 0 else 0
""")


st.markdown("______")

# ==================== NEW SECTION: GROUP BY BANK BALANCE ====================
st.subheader("🏦 Bank-wise Balance Breakdown")

# Create bank balance grouping
if 'bank_name' in df_filtered.columns and len(df_filtered) > 0:
    # Group by bank name
    bank_balance_df = df_filtered.groupby('bank_name').agg({
        'bank_deposit': 'sum',
        'bank_withdrawal': 'sum'
    }).reset_index()
    
    # Calculate net balance per bank
    bank_balance_df['net_balance'] = bank_balance_df['bank_deposit'] - bank_balance_df['bank_withdrawal']
    bank_balance_df = bank_balance_df[bank_balance_df['bank_name'].notna() & (bank_balance_df['bank_name'] != '')]
    
    if len(bank_balance_df) > 0:
        # Sort by net balance descending
        bank_balance_df = bank_balance_df.sort_values('net_balance', ascending=False)
        
        # Display bank balances in columns
        cols = st.columns(min(len(bank_balance_df), 4))
        for idx, (_, row) in enumerate(bank_balance_df.iterrows()):
            with cols[idx % 4]:
                st.markdown(f"""
                <div class='bank-card'>
                    <h3>🏛️ {row['bank_name']}</h3>
                    <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>{row['net_balance']:,.2f}</p>
                    <hr style='margin: 10px 0;'>
                    <p>💰 Deposits: {row['bank_deposit']:,.2f}</p>
                    <p>💸 Withdrawals: {row['bank_withdrawal']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Bank Balance Chart
        st.markdown("---")
        col_chart_left, col_chart_right = st.columns(2)
        
        with col_chart_left:
            # Bar chart for bank balances
            fig_bank_bar = px.bar(
                bank_balance_df,
                x='bank_name',
                y='net_balance',
                title="Bank-wise Net Balance",
                labels={'bank_name': 'Bank Name', 'net_balance': 'Net Balance (BDT)'},
                color='net_balance',
                color_continuous_scale='Viridis',
                text='net_balance'
            )
            fig_bank_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_bank_bar.update_layout(height=400)
            st.plotly_chart(fig_bank_bar, use_container_width=True)
        
        with col_chart_right:
            # Pie chart for bank distribution
            positive_banks = bank_balance_df[bank_balance_df['net_balance'] > 0]
            if len(positive_banks) > 0:
                fig_bank_pie = px.pie(
                    positive_banks,
                    values='net_balance',
                    names='bank_name',
                    title="Bank Balance Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.3
                )
                fig_bank_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_bank_pie.update_layout(height=400)
                st.plotly_chart(fig_bank_pie, use_container_width=True)
            else:
                st.info("No positive bank balances to display in pie chart")
        
        # Detailed bank transactions table
        with st.expander("📊 View Detailed Bank Transactions"):
            # Get bank transaction details
            bank_transactions = df_filtered[df_filtered['bank_name'].notna() & (df_filtered['bank_name'] != '')]
            if len(bank_transactions) > 0:
                # Select relevant columns
                bank_cols = ['date', 'bank_name', 'bank_deposit', 'bank_withdrawal', 'voucher_no', 'account_head']
                available_bank_cols = [col for col in bank_cols if col in bank_transactions.columns]
                
                bank_details = bank_transactions[available_bank_cols].copy()
                bank_details = bank_details.sort_values('date', ascending=False)
                
                # Format the dataframe
                if 'date' in bank_details.columns:
                    bank_details['date'] = bank_details['date'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(bank_details, use_container_width=True)
                
                # Summary statistics
                st.markdown("### 📈 Bank Summary Statistics")
                summary_stats = bank_balance_df[['bank_name', 'bank_deposit', 'bank_withdrawal', 'net_balance']].copy()
                summary_stats.columns = ['Bank Name', 'Total Deposits', 'Total Withdrawals', 'Net Balance']
                st.dataframe(summary_stats.style.format({
                    'Total Deposits': '{:,.2f}',
                    'Total Withdrawals': '{:,.2f}',
                    'Net Balance': '{:,.2f}'
                }), use_container_width=True)
    else:
        st.info("No bank transaction data available. Please ensure 'bank_name' column exists in your data.")
else:
    st.warning("⚠️ 'bank_name' column not found in the dataset. Please check your CSV file structure.")
    
    # Alternative: Show available columns for debugging
    with st.expander("🔍 Available Columns in Dataset"):
        st.write("Columns found:", list(df_filtered.columns))
        st.info("To enable bank-wise grouping, please ensure your CSV has a 'bank_name' column.")


# ==================== BANK DEBIT AND CREDIT STATISTICS SECTION ====================
st.subheader("🏦 Bank Debit and Credit Statistics")

if 'bank_name' in df_filtered.columns and len(df_filtered) > 0:
    # Group by bank name to get debit and credit statistics
    bank_stats = df_filtered.groupby('bank_name').agg({
        'bank_deposit': 'sum',      # Bank Debits (Deposits)
        'bank_withdrawal': 'sum'     # Bank Credits (Withdrawals)
    }).reset_index()
    
    # Calculate net balance
    bank_stats['net_balance'] = bank_stats['bank_deposit'] - bank_stats['bank_withdrawal']
    
    # Remove empty bank names
    bank_stats = bank_stats[bank_stats['bank_name'].notna() & (bank_stats['bank_name'] != '')]
    
    if len(bank_stats) > 0:
        # Sort by net balance
        bank_stats = bank_stats.sort_values('net_balance', ascending=False)
        
        # Display summary metrics for bank transactions
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Bank Deposits (Debit)", f"₹{bank_stats['bank_deposit'].sum():,.2f}")
        with col2:
            st.metric("💸 Total Bank Withdrawals (Credit)", f"₹{bank_stats['bank_withdrawal'].sum():,.2f}")
        with col3:
            st.metric("🏦 Net Bank Balance", f"₹{bank_stats['net_balance'].sum():,.2f}")
        with col4:
            # Calculate transaction ratio
            if bank_stats['bank_deposit'].sum() > 0:
                ratio = (bank_stats['bank_withdrawal'].sum() / bank_stats['bank_deposit'].sum()) * 100
                st.metric("💰 Withdrawal/Deposit Ratio", f"{ratio:.1f}%")
        
        st.markdown("---")
        
        # --- BAR CHART: Bank Debit vs Credit Comparison ---
        # Prepare data for grouped bar chart
        bank_chart_data = bank_stats.melt(
            id_vars=['bank_name'],
            value_vars=['bank_deposit', 'bank_withdrawal'],
            var_name='Transaction Type',
            value_name='Amount'
        )
        
        # Rename transaction types for better display
        bank_chart_data['Transaction Type'] = bank_chart_data['Transaction Type'].map({
            'bank_deposit': 'Bank Deposits (Debit)',
            'bank_withdrawal': 'Bank Withdrawals (Credit)'
        })
        
        # Create grouped bar chart
        fig_bank_debit_credit = px.bar(
            bank_chart_data,
            x='bank_name',
            y='Amount',
            color='Transaction Type',
            barmode='group',
            title="📊 Bank Debit vs Credit Statistics by Bank",
            labels={
                'bank_name': 'Bank Name',
                'Amount': 'Amount (₹)',
                'Transaction Type': 'Transaction Type'
            },
            color_discrete_map={
                'Bank Deposits (Debit)': '#2ECC71',
                'Bank Withdrawals (Credit)': '#E74C3C'
            },
            text='Amount'
        )
        
        # Customize bar chart appearance
        fig_bank_debit_credit.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside'
        )
        fig_bank_debit_credit.update_layout(
            height=500,
            xaxis_tickangle=-45,
            bargap=0.2,
            bargroupgap=0.1,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig_bank_debit_credit, use_container_width=True)
        
        # --- Additional Visualization: Stacked Bar Chart ---
        st.subheader("📊 Bank Transaction Distribution")
        
        col_stack1, col_stack2 = st.columns(2)
        
        with col_stack1:
            # Stacked bar chart showing composition
            fig_stacked = px.bar(
                bank_stats,
                x='bank_name',
                y=['bank_deposit', 'bank_withdrawal'],
                barmode='stack',
                title="Stacked View: Deposits vs Withdrawals",
                labels={'bank_name': 'Bank Name', 'value': 'Amount (BDT)', 'variable': 'Type'},
                color_discrete_map={
                    'bank_deposit': '#2ECC71',
                    'bank_withdrawal': '#E74C3C'
                },
                text_auto=True
            )
            fig_stacked.update_layout(height=400)
            fig_stacked.update_traces(texttemplate='%{text:,.0f}')
            st.plotly_chart(fig_stacked, use_container_width=True)
        
        with col_stack2:
            # Horizontal bar chart for better readability
            bank_stats_sorted = bank_stats.sort_values('net_balance', ascending=True)
            fig_horizontal = px.bar(
                bank_stats_sorted,
                y='bank_name',
                x='net_balance',
                orientation='h',
                title="Net Balance by Bank (Horizontal)",
                labels={'bank_name': 'Bank Name', 'net_balance': 'Net Balance (BDT)'},
                color='net_balance',
                color_continuous_scale='RdYlGn',
                text='net_balance'
            )
            fig_horizontal.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside'
            )
            fig_horizontal.update_layout(height=400)
            st.plotly_chart(fig_horizontal, use_container_width=True)
        
        # --- Bank Statistics Table ---
        with st.expander("📋 View Detailed Bank Statistics Table"):
            # Create formatted table
            display_table = bank_stats.copy()
            display_table.columns = ['Bank Name', 'Total Deposits (Debit)', 'Total Withdrawals (Credit)', 'Net Balance']
            
            # Add percentage columns
            total_deposits = display_table['Total Deposits (Debit)'].sum()
            total_withdrawals = display_table['Total Withdrawals (Credit)'].sum()
            
            display_table['Deposit %'] = (display_table['Total Deposits (Debit)'] / total_deposits * 100).round(2) if total_deposits > 0 else 0
            display_table['Withdrawal %'] = (display_table['Total Withdrawals (Credit)'] / total_withdrawals * 100).round(2) if total_withdrawals > 0 else 0
            
            # Format currency columns
            styled_table = display_table.style.format({
                'Total Deposits (Debit)': '{:,.2f}',
                'Total Withdrawals (Credit)': '{:,.2f}',
                'Net Balance': '{:,.2f}',
                'Deposit %': '{:.2f}%',
                'Withdrawal %': '{:.2f}%'
            })
            
            st.dataframe(styled_table, use_container_width=True)
            
            # Download button for bank statistics
            csv_bank_stats = bank_stats.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Bank Statistics as CSV",
                data=csv_bank_stats,
                file_name="bank_debit_credit_statistics.csv",
                mime="text/csv"
            )
        
        # --- Transaction Trends by Bank ---
        st.subheader("📈 Bank Transaction Trends")
        
        # Prepare time series data for banks
        if 'date' in df_filtered.columns and len(df_filtered) > 0:
            # Create monthly bank transaction summary
            df_filtered['month'] = df_filtered['date'].dt.to_period('M').astype(str)
            
            monthly_bank_stats = df_filtered.groupby(['month', 'bank_name']).agg({
                'bank_deposit': 'sum',
                'bank_withdrawal': 'sum'
            }).reset_index()
            
            monthly_bank_stats = monthly_bank_stats[monthly_bank_stats['bank_name'].notna() & (monthly_bank_stats['bank_name'] != '')]
            
            if len(monthly_bank_stats) > 0:
                # Line chart for deposit trends
                fig_trend = px.line(
                    monthly_bank_stats,
                    x='month',
                    y='bank_deposit',
                    color='bank_name',
                    title="Bank Deposit Trends Over Time",
                    labels={'month': 'Month', 'bank_deposit': 'Deposits (₹)', 'bank_name': 'Bank Name'},
                    markers=True
                )
                fig_trend.update_layout(height=400)
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Line chart for withdrawal trends
                fig_withdrawal_trend = px.line(
                    monthly_bank_stats,
                    x='month',
                    y='bank_withdrawal',
                    color='bank_name',
                    title="Bank Withdrawal Trends Over Time",
                    labels={'month': 'Month', 'bank_withdrawal': 'Withdrawals (₹)', 'bank_name': 'Bank Name'},
                    markers=True
                )
                fig_withdrawal_trend.update_layout(height=400)
                st.plotly_chart(fig_withdrawal_trend, use_container_width=True)
        
    else:
        st.info("No bank transaction data available. Please ensure 'bank_name' column exists in your data.")
else:
    st.warning("⚠️ 'bank_name' column not found in the dataset. Please check your CSV file structure.")
    
    # Alternative: Show available columns for debugging
    with st.expander("🔍 Available Columns in Dataset"):
        st.write("Columns found:", list(df_filtered.columns))
        st.info("To enable bank-wise grouping, please ensure your CSV has a 'bank_name' column.")
