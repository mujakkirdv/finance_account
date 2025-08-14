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
EXCEL_FILE = "data/accounts.xlsx"

# ================= LOAD DATA =================

@st.cache_data
def load_data():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        # Ensure date columns are parsed properly
        for col in ['date', 'invoice_date', 'due_date', 'payment_date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    else:
        st.error(f"Excel file not found: {EXCEL_FILE}")
        return pd.DataFrame()

df = load_data()

# ================= SIDEBAR MENU =================
menu = [
    "🏠 Home", 
    "📊 Dashboard", 
    "💵 Cashbook", 
    "🏦 Bankbook", 
    "📉 Liability",
    "💰 Income", 
    "💸 Expense", 
    "📂 Payables", 
    "📥 Receivables",
    "📈 Forecast",
    "📑 MD Report",
    "🏧 Bank Txns",
    "⚙ Settings",
    "👨‍⚖️ About",
    "⚖ Blance Sheet",
]

choice = st.sidebar.radio("📌 Navigation", menu)

# ================= HOME =================
if choice == "🏠 Home":
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
    </style>
    """, unsafe_allow_html=True)

    # --- Ensure Numeric Columns ---
    for col in ['debit', 'credit', 'bank_deposit', 'bank_withdrawal']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- Current Balance Calculation ---
    total_cash = df['debit'].sum() - df['credit'].sum()
    total_bank = df['bank_deposit'].sum() - df['bank_withdrawal'].sum()
    total_balance = total_cash + total_bank

    # --- Header ---
    st.markdown("<div class='main-header'>🏠 Welcome to Financial App</div>", unsafe_allow_html=True)
    st.metric("💳 Current Balance", f"{total_balance:,.2f}")

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
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.to_period('M').astype(str)

        monthly_summary = df.groupby('month', as_index=False).agg(
            total_income=('debit', 'sum'),
            total_expense=('credit', 'sum')
        )

        fig = px.bar(
            monthly_summary,
            x='month',
            y=['total_income', 'total_expense'],
            barmode='group',
            title="📅 Monthly Income vs Expense",
            labels={"value": "Amount", "month": "Month"}
        )
        st.plotly_chart(fig, use_container_width=True)

# ================= DASHBOARD =================
elif choice == "📊 Dashboard" and not df.empty:
    # --- Custom CSS for Dashboard ---
    st.markdown("""
    <style>
        .dashboard-header {
            font-size: 28px;
            font-weight: bold;
            color: #2E86C1;
            margin-bottom: 15px;
        }
        .metric-container {
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='dashboard-header'>📈 Overall Summary Dashboard</div>", unsafe_allow_html=True)

    # --- Ensure numeric values ---
    for col in ['debit', 'credit']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- Summary Calculations ---
    total_income = df['credit'].sum()
    total_expense = df['debit'].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Income", f"{total_income:,.2f}")
    col2.metric("💸 Total Expense", f"{total_expense:,.2f}")
    col3.metric("📊 Net Balance", f"{balance:,.2f}")

    st.markdown("---")

    # --- Category-wise Income/Expense ---
    if 'category' in df.columns:
        category_summary = df.groupby('category', dropna=False).agg(
            total_expense=('debit', 'sum'),
            total_income=('credit', 'sum')
        ).reset_index()

        fig = px.bar(
            category_summary,
            x='category',
            y=['total_expense', 'total_income'],
            barmode='group',
            title="📂 Category-wise Income & Expense",
            labels={"value": "Amount", "category": "Category"},
            hover_data={'category': True, 'total_expense': ':.2f', 'total_income': ':.2f'}
        )
        fig.update_layout(xaxis_title="Category", yaxis_title="Amount")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Monthly Trend Chart ---
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.to_period('M')

        monthly_summary = df.groupby('month').agg(
            total_expense=('debit', 'sum'),
            total_income=('credit', 'sum')
        ).reset_index()
        monthly_summary['month'] = monthly_summary['month'].dt.to_timestamp()

        fig2 = px.line(
            monthly_summary,
            x='month',
            y=['total_expense', 'total_income'],
            title="📅 Monthly Income & Expense Trend",
            markers=True,
            labels={"value": "Amount", "month": "Month"}
        )
        fig2.update_traces(mode="lines+markers")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ Date column not found in data. Monthly trend chart cannot be displayed.")




# --------------------
# 💵 Cashbook
# --------------------
elif choice == "💵 Cashbook" and not df.empty:
    st.header("💵 Advanced Cashbook Analytics Dashboard")
    
    # Data Preparation Section
    with st.expander("⚙️ Data Preparation Settings", expanded=False):
        # Convert to numeric and date
        numeric_cols = ['debit', 'credit', 'amount', 'bank_deposit', 'bank_withdrawal']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
        
        # Create derived columns
        df['month_year'] = df['payment_date'].dt.to_period('M')
        df['day_of_week'] = df['payment_date'].dt.day_name()
        df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
        df['year'] = df['payment_date'].dt.year
        
        # Filter cash transactions
        if "payment_method" in df.columns:
            cash_df = df[df['payment_method'].str.lower().str.contains('cash|ca', na=False)].copy()
        else:
            st.warning("No payment_method column found - showing all transactions")
            cash_df = df.copy()

    if not cash_df.empty:
        # Date Range Selection with Enhanced Options
        st.subheader("📅 Date Range Selection")
        
        min_date = cash_df['payment_date'].min().date()
        max_date = cash_df['payment_date'].max().date()
        
        # Create columns for date selection
        col1, col2, col3, col4 = st.columns([3,1,1,1])
        
        with col1:
            date_range = st.date_input(
                "Select Date Range", 
                [min_date, max_date],
                key="cashbook_date_range"
            )
        
        with col2:
            if st.button("Last 7 Days"):
                date_range = [max_date - timedelta(days=7), max_date]
        
        with col3:
            if st.button("Current Month"):
                first_day = datetime(max_date.year, max_date.month, 1).date()
                date_range = [first_day, max_date]
        
        with col4:
            if st.button("Current Year"):
                first_day = datetime(max_date.year, 1, 1).date()
                date_range = [first_day, max_date]
        
        # Apply date filter
        if len(date_range) == 2:
            cash_df = cash_df[
                (cash_df['payment_date'].dt.date >= date_range[0]) & 
                (cash_df['payment_date'].dt.date <= date_range[1])
            ]
            st.success(f"Showing data from {date_range[0]} to {date_range[1]}")
        
        # Key Metrics Section with Enhanced Calculations
        st.subheader("📊 Cash Flow Summary")
        
        # Calculate metrics
        total_debit = cash_df['debit'].sum()
        total_credit = cash_df['credit'].sum()
        net_flow = total_debit - total_credit
        transaction_count = cash_df['voucher_no'].nunique()
        
        # Calculate period comparison metrics
        prev_period_label = ""
        debit_change = credit_change = 0
        
        if len(date_range) == 2:
            days_diff = (date_range[1] - date_range[0]).days
            prev_start = date_range[0] - timedelta(days=days_diff+1)
            prev_end = date_range[0] - timedelta(days=1)
            
            prev_period_df = df[
                (df['payment_date'].dt.date >= prev_start) & 
                (df['payment_date'].dt.date <= prev_end)
            ]
            
            prev_debit = prev_period_df['debit'].sum()
            prev_credit = prev_period_df['credit'].sum()
            
            debit_change = ((total_debit - prev_debit)/prev_debit*100) if prev_debit > 0 else 0
            credit_change = ((total_credit - prev_credit)/prev_credit*100) if prev_credit > 0 else 0
            
            prev_period_label = f"vs {prev_start} to {prev_end}"
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "💰 Total Cash In", 
            f"${total_debit:,.2f}", 
            f"{debit_change:.1f}% {prev_period_label}" if prev_period_label else ""
        )
        col2.metric(
            "💸 Total Cash Out", 
            f"${total_credit:,.2f}", 
            f"{credit_change:.1f}% {prev_period_label}" if prev_period_label else ""
        )
        col3.metric(
            "🏦 Net Cash Flow", 
            f"${net_flow:,.2f}", 
            "Surplus" if net_flow >= 0 else "Deficit",
            delta_color="inverse"
        )
        col4.metric(
            "🧾 Transactions", 
            f"{transaction_count:,}", 
            f"{len(cash_df['account_head'].unique()):,} Accounts"
        )
        
        # Enhanced Analysis Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Trend Analysis", "Category Analysis", "Party Analysis", "Detailed Transactions"])
        
        with tab1:
            # Enhanced Trend Analysis
            st.subheader("📈 Cash Flow Trends")
            
            col1, col2 = st.columns(2)
            with col1:
                time_period = st.selectbox(
                    "Aggregation Period",
                    ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
                    key="cashbook_time_period"
                )
            
            with col2:
                show_cumulative = st.checkbox("Show Cumulative", True)
            
            # Resample data based on selected period
            if time_period == "Daily":
                time_df = cash_df.set_index('payment_date').resample('D').sum(numeric_only=True)
            elif time_period == "Weekly":
                time_df = cash_df.set_index('payment_date').resample('W').sum(numeric_only=True)
            elif time_period == "Monthly":
                time_df = cash_df.set_index('payment_date').resample('M').sum(numeric_only=True)
            elif time_period == "Quarterly":
                time_df = cash_df.set_index('payment_date').resample('Q').sum(numeric_only=True)
            else:
                time_df = cash_df.set_index('payment_date').resample('Y').sum(numeric_only=True)
            
            # Create trend chart
            fig = px.line(
                time_df, 
                y=['debit', 'credit'],
                title=f"{time_period} Cash Flow Trend",
                labels={'value': 'Amount', 'variable': 'Flow Type'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add cumulative view if selected
            if show_cumulative:
                time_df['cumulative_debit'] = time_df['debit'].cumsum()
                time_df['cumulative_credit'] = time_df['credit'].cumsum()
                time_df['cumulative_net'] = time_df['cumulative_debit'] - time_df['cumulative_credit']
                
                fig = px.area(
                    time_df,
                    y=['cumulative_debit', 'cumulative_credit', 'cumulative_net'],
                    title="Cumulative Cash Flow"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Weekday/Weekend Analysis
            if 'day_of_week' in cash_df.columns:
                st.subheader("📅 Day of Week Analysis")
                
                weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                weekday_agg = cash_df.groupby('day_of_week').agg(
                    total_debit=('debit', 'sum'),
                    total_credit=('credit', 'sum'),
                    count=('voucher_no', 'nunique')
                ).reindex(weekday_order).reset_index()
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(
                        weekday_agg, 
                        x='day_of_week', 
                        y='total_debit',
                        title="Cash In by Day of Week"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(
                        weekday_agg, 
                        x='day_of_week', 
                        y='total_credit',
                        title="Cash Out by Day of Week"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Enhanced Category Analysis
            st.subheader("📊 Category Breakdown")
            
            if 'category' in cash_df.columns:
                # Prepare category data
                cat_data = cash_df.groupby(['category', 'sub_category']).agg(
                    total_debit=('debit', 'sum'),
                    total_credit=('credit', 'sum'),
                    transaction_count=('voucher_no', 'nunique'),
                    avg_amount=('amount', 'mean')
                ).reset_index()
                cat_data['net_flow'] = cat_data['total_debit'] - cat_data['total_credit']
                
                # Visualizations
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.treemap(
                        cat_data, 
                        path=['category', 'sub_category'], 
                        values='total_debit',
                        title="Cash In by Category",
                        color='total_debit',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.treemap(
                        cat_data, 
                        path=['category', 'sub_category'], 
                        values='total_credit',
                        title="Cash Out by Category",
                        color='total_credit',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Top categories tables
                st.subheader("🏆 Top Categories")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Top Cash In Categories**")
                    st.dataframe(
                        cat_data.nlargest(5, 'total_debit')[['category', 'sub_category', 'total_debit', 'transaction_count']]
                        .rename(columns={'total_debit': 'Amount', 'transaction_count': 'Transactions'})
                        .style.format({'Amount': '${:,.2f}'}),
                        hide_index=True
                    )
                
                with col2:
                    st.markdown("**Top Cash Out Categories**")
                    st.dataframe(
                        cat_data.nlargest(5, 'total_credit')[['category', 'sub_category', 'total_credit', 'transaction_count']]
                        .rename(columns={'total_credit': 'Amount', 'transaction_count': 'Transactions'})
                        .style.format({'Amount': '${:,.2f}'}),
                        hide_index=True
                    )
        
        with tab3:
            # Enhanced Party Analysis
            st.subheader("🧑‍💼 Party/Organization Analysis")
            
            if 'party_name' in cash_df.columns:
                # Prepare party data
                party_data = cash_df.groupby(['party_type', 'party_name']).agg(
                    total_debit=('debit', 'sum'),
                    total_credit=('credit', 'sum'),
                    transaction_count=('voucher_no', 'nunique'),
                    first_date=('payment_date', 'min'),
                    last_date=('payment_date', 'max'),
                    avg_amount=('amount', 'mean')
                ).reset_index()
                party_data['net_flow'] = party_data['total_debit'] - party_data['total_credit']
                party_data['activity_days'] = (party_data['last_date'] - party_data['first_date']).dt.days + 1
                
                # Top parties
                st.subheader("🔝 Top Parties")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Top Cash Receivers**")
                    st.dataframe(
                        party_data.nlargest(5, 'total_debit')[['party_name', 'party_type', 'total_debit', 'transaction_count']]
                        .rename(columns={'total_debit': 'Amount', 'transaction_count': 'Transactions'})
                        .style.format({'Amount': '${:,.2f}'}),
                        hide_index=True
                    )
                
                with col2:
                    st.markdown("**Top Cash Payees**")
                    st.dataframe(
                        party_data.nlargest(5, 'total_credit')[['party_name', 'party_type', 'total_credit', 'transaction_count']]
                        .rename(columns={'total_credit': 'Amount', 'transaction_count': 'Transactions'})
                        .style.format({'Amount': '${:,.2f}'}),
                        hide_index=True
                    )
                
                # Full party analysis with filtering
                st.subheader("🔍 Detailed Party Analysis")
                
                col1, col2 = st.columns(2)
                with col1:
                    party_type_filter = st.multiselect(
                        "Filter by Party Type",
                        options=party_data['party_type'].unique(),
                        default=party_data['party_type'].unique()
                    )
                
                with col2:
                    min_transactions = st.number_input(
                        "Minimum Transactions",
                        min_value=1,
                        value=1,
                        step=1
                    )
                
                filtered_parties = party_data[
                    (party_data['party_type'].isin(party_type_filter)) &
                    (party_data['transaction_count'] >= min_transactions)
                ]
                
                st.dataframe(
                    filtered_parties.sort_values('net_flow', ascending=False),
                    column_config={
                        "total_debit": st.column_config.NumberColumn("Received", format="$%.2f"),
                        "total_credit": st.column_config.NumberColumn("Paid", format="$%.2f"),
                        "net_flow": st.column_config.NumberColumn("Net Flow", format="$%.2f"),
                        "avg_amount": st.column_config.NumberColumn("Avg Amount", format="$%.2f"),
                        "transaction_count": "Transactions",
                        "activity_days": "Active Days"
                    },
                    hide_index=True,
                    use_container_width=True
                )
        
        with tab4:
            # Enhanced Transaction Details
            st.subheader("🧾 Detailed Transactions")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                category_filter = st.multiselect(
                    "Filter by Category",
                    options=cash_df['category'].unique() if 'category' in cash_df.columns else [],
                    key="txn_category_filter"
                )
            
            with col2:
                # Handle amount range slider with validation
                if 'amount' in cash_df.columns and not cash_df['amount'].isnull().all():
                    min_amount = float(cash_df['amount'].min())
                    max_amount = float(cash_df['amount'].max())
                    
                    if min_amount == max_amount:
                        # If all amounts are same, add buffer
                        max_amount = min_amount + 1
                        st.warning("All amounts are identical - adjusting range for visualization")
                    
                    amount_range = st.slider(
                        "Amount Range",
                        min_value=min_amount,
                        max_value=max_amount,
                        value=(min_amount, max_amount)
                    )
                else:
                    st.warning("Amount data not available for filtering")
                    amount_range = (0, 0)
            
            with col3:
                flow_type = st.multiselect(
                    "Flow Type",
                    options=["Cash In", "Cash Out"],
                    default=["Cash In", "Cash Out"]
                )
            
            # Apply filters
            filtered_df = cash_df.copy()
            
            if category_filter:
                filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
            
            if amount_range != (0, 0):
                filtered_df = filtered_df[
                    (filtered_df['amount'] >= amount_range[0]) & 
                    (filtered_df['amount'] <= amount_range[1])
                ]
            
            flow_filters = []
            if "Cash In" in flow_type:
                flow_filters.append(filtered_df['debit'] > 0)
            if "Cash Out" in flow_type:
                flow_filters.append(filtered_df['credit'] > 0)
            
            if flow_filters:
                filtered_df = filtered_df[np.logical_or.reduce(flow_filters)]
            
            # Column selection and display
            default_cols = ['payment_date', 'voucher_no', 'particulars', 'debit', 'credit']
            optional_cols = ['category', 'sub_category', 'party_name', 'account_head', 'reference', 'status']
            
            selected_cols = st.multiselect(
                "Select columns to display",
                options=optional_cols,
                default=optional_cols,
                key="txn_col_selector"
            )
            
            display_cols = default_cols + [col for col in selected_cols if col in cash_df.columns]
            
            # Display data with enhanced configuration
            st.dataframe(
                filtered_df[display_cols].sort_values('payment_date', ascending=False),
                column_config={
                    "payment_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "debit": st.column_config.NumberColumn("Cash In", format="$%.2f"),
                    "credit": st.column_config.NumberColumn("Cash Out", format="$%.2f"),
                    "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                    "status": st.column_config.TextColumn("Status")
                },
                hide_index=True,
                use_container_width=True,
                height=500
            )
            
            # Enhanced Export Options
            st.subheader("📤 Export Data")
            
            col1, col2 = st.columns(2)
            with col1:
                export_format = st.selectbox(
                    "Export Format",
                    ["CSV", "Excel"],
                    index=0
                )
            
            with col2:
                export_all = st.checkbox(
                    "Export All Columns",
                    value=False
                )
            
            export_cols = display_cols if not export_all else cash_df.columns
            
            if export_format == "CSV":
                csv = filtered_df[export_cols].to_csv(index=False).encode('utf-8')
                st.download_button(
                    "💾 Download CSV",
                    data=csv,
                    file_name=f"cash_transactions_{date_range[0]}_to_{date_range[1]}.csv",
                    mime='text/csv'
                )
            else:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    filtered_df[export_cols].to_excel(writer, index=False)
                excel_data = excel_buffer.getvalue()
                st.download_button(
                    "💾 Download Excel",
                    data=excel_data,
                    file_name=f"cash_transactions_{date_range[0]}_to_{date_range[1]}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

    else:
        st.warning("⚠️ No cash transactions found in the selected date range!")
# --------------------
# 🏦 Bankbook
# --------------------
elif choice == "🏦 Bankbook" and not df.empty:
    st.header("🏦 Bankbook Transaction Analysis")
    
    # Check required columns
    required_cols = ["bank_deposit", "bank_withdrawal", "account_head", "payment_date", "payment_method"]
    if all(col in df.columns for col in required_cols):
        
        # Convert to numeric and date
        numeric_cols = ['bank_deposit', 'bank_withdrawal', 'amount', 'debit', 'credit', 'payable', 'receivedable']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
        df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce') if 'due_date' in df.columns else None
        
        # Filter bank transactions
        bank_df = df[df['payment_method'].astype(str).str.lower().str.contains('bank', na=False)].copy()
        
        if not bank_df.empty:
            # Calculate totals
            total_deposit = bank_df['bank_deposit'].sum()
            total_withdrawal = bank_df['bank_withdrawal'].sum()
            net_flow = total_deposit - total_withdrawal
            
            # Date range selection
            min_date = bank_df['payment_date'].min().date()
            max_date = bank_df['payment_date'].max().date()
            date_range = st.date_input("Select Date Range", [min_date, max_date])
            
            if len(date_range) == 2:
                bank_df = bank_df[
                    (bank_df['payment_date'].dt.date >= date_range[0]) & 
                    (bank_df['payment_date'].dt.date <= date_range[1])
                ]
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Deposit", f"${total_deposit:,.2f}", "All Time")
            col2.metric("Total Withdrawal", f"${total_withdrawal:,.2f}", "All Time") 
            col3.metric("Net Flow", f"${net_flow:,.2f}", delta_color="inverse")
            
            if 'amount' in bank_df.columns:
                col4.metric("Total Amount", f"${bank_df['amount'].sum():,.2f}")
            
            # Account-wise analysis
            st.subheader("📊 Account Head Summary")
            account_summary = bank_df.groupby('account_head').agg(
                total_deposit=('bank_deposit', 'sum'),
                total_withdrawal=('bank_withdrawal', 'sum'),
                transactions=('voucher_no', 'nunique'),
                last_date=('payment_date', 'max')
            ).reset_index()
            
            account_summary['balance'] = account_summary['total_deposit'] - account_summary['total_withdrawal']
            st.dataframe(account_summary.sort_values('balance', ascending=False), hide_index=True)
            
            # Sub-category visualizations
            if 'sub_category' in bank_df.columns:
                st.subheader("📈 Sub-Category Analysis")
                
                # Prepare sub-category data
                subcat_data = bank_df.groupby(['category', 'sub_category']).agg(
                    total_deposit=('bank_deposit', 'sum'),
                    total_withdrawal=('bank_withdrawal', 'sum'),
                    count=('voucher_no', 'nunique')
                ).reset_index()
                
                # Create tabs for different visualizations
                tab1, tab2, tab3 = st.tabs(["Deposit Analysis", "Withdrawal Analysis", "Transaction Count"])
                
                with tab1:
                    st.markdown("#### Deposit by Sub-Category")
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        # Bar chart for deposits by sub-category
                        fig_bar = px.bar(
                            subcat_data.sort_values('total_deposit', ascending=False),
                            x='sub_category',
                            y='total_deposit',
                            color='category',
                            title="Deposit Amount by Sub-Category",
                            labels={'total_deposit': 'Deposit Amount', 'sub_category': 'Sub-Category'}
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        # Pie chart for deposit distribution
                        fig_pie = px.pie(
                            subcat_data,
                            values='total_deposit',
                            names='sub_category',
                            title="Deposit Distribution",
                            hole=0.3
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                with tab2:
                    st.markdown("#### Withdrawal by Sub-Category")
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        # Bar chart for withdrawals by sub-category
                        fig_bar = px.bar(
                            subcat_data.sort_values('total_withdrawal', ascending=False),
                            x='sub_category',
                            y='total_withdrawal',
                            color='category',
                            title="Withdrawal Amount by Sub-Category",
                            labels={'total_withdrawal': 'Withdrawal Amount', 'sub_category': 'Sub-Category'}
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        # Pie chart for withdrawal distribution
                        fig_pie = px.pie(
                            subcat_data,
                            values='total_withdrawal',
                            names='sub_category',
                            title="Withdrawal Distribution",
                            hole=0.3
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                with tab3:
                    st.markdown("#### Transaction Count by Sub-Category")
                    fig = px.bar(
                        subcat_data.sort_values('count', ascending=False),
                        x='sub_category',
                        y='count',
                        color='category',
                        title="Number of Transactions by Sub-Category",
                        labels={'count': 'Transaction Count', 'sub_category': 'Sub-Category'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Party analysis
            if 'party_name' in bank_df.columns:
                st.subheader("🧑‍💼 Party/Organization Analysis")
                party_summary = bank_df.groupby(['party_type', 'party_name']).agg(
                    total_amount=('amount', 'sum'),
                    transactions=('voucher_no', 'nunique'),
                    last_transaction=('payment_date', 'max'),
                    outstanding=('payable', 'sum') if 'payable' in bank_df.columns else ('receivedable', 'sum')
                ).reset_index()
                st.dataframe(party_summary, hide_index=True)
            
            # Time series analysis
            st.subheader("📅 Cash Flow Over Time")
            time_analysis = bank_df.set_index('payment_date').resample('M').agg({
                'bank_deposit': 'sum',
                'bank_withdrawal': 'sum',
                'amount': 'sum' if 'amount' in bank_df.columns else None
            }).dropna(how='all')
            st.line_chart(time_analysis)
            
            # Detailed transactions with filters
            st.subheader("🔍 Transaction Details")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                account_filter = st.multiselect(
                    "Filter by Account Head",
                    options=bank_df['account_head'].unique()
                )
            
            with col2:
                category_filter = st.multiselect(
                    "Filter by Category", 
                    options=bank_df['category'].unique() if 'category' in bank_df.columns else []
                )
            
            with col3:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=bank_df['status'].unique() if 'status' in bank_df.columns else []
                )
            
            filtered_df = bank_df.copy()
            if account_filter:
                filtered_df = filtered_df[filtered_df['account_head'].isin(account_filter)]
            if category_filter:
                filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
            if status_filter:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            
            # Select columns to display
            default_cols = [
                'payment_date', 'voucher_no', 'particulars', 
                'account_head', 'bank_deposit', 'bank_withdrawal'
            ]
            optional_cols = ['category', 'sub_category', 'party_name', 'payment_method', 'amount', 'status']
            selected_cols = st.multiselect(
                "Select columns to display",
                options=optional_cols,
                default=optional_cols
            )
            
            display_cols = default_cols + [col for col in selected_cols if col in bank_df.columns]
            
            st.dataframe(
                filtered_df[display_cols].sort_values('payment_date', ascending=False),
                hide_index=True,
                column_config={
                    "payment_date": "Date",
                    "bank_deposit": st.column_config.NumberColumn("Deposit", format="$%.2f"),
                    "bank_withdrawal": st.column_config.NumberColumn("Withdrawal", format="$%.2f"),
                    "amount": st.column_config.NumberColumn("Amount", format="$%.2f")
                }
            )
            
            # Export option
            csv = filtered_df[display_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name='bank_transactions.csv',
                mime='text/csv'
            )
            
        else:
            st.warning("No bank transactions found!")
    else:
        st.error("Required columns missing: bank_deposit, bank_withdrawal, payment_date, payment_method")

# ================= Laibity =================

elif choice == "📉 Liability" and not df.empty:
    st.header("📊 Liability Analysis")

    # Ensure required columns exist
    required_cols = ["amount", "due_date", "status", "party_name", "account_head", "sub_category", "party_type"]
    if all(col in df.columns for col in required_cols):

        # Convert types
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')

        # Define liability conditions
        liability_df = df[
            df['account_head'].str.contains("Liability|Loan", case=False, na=False) |
            df['sub_category'].str.contains("Loan|Liability", case=False, na=False) |
            df['party_type'].str.contains("Managing Director", case=False, na=False)
        ].copy()

        if not liability_df.empty:
            # Date range filter
            min_date = liability_df['due_date'].min().date()
            max_date = liability_df['due_date'].max().date()
            date_range = st.date_input("Select Due Date Range", [min_date, max_date])

            if len(date_range) == 2:
                liability_df = liability_df[
                    (liability_df['due_date'].dt.date >= date_range[0]) &
                    (liability_df['due_date'].dt.date <= date_range[1])
                ]

            # Metrics
            total_liabilities = liability_df['amount'].sum()
            overdue_liabilities = liability_df[liability_df['status'].str.lower() != 'paid']['amount'].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Liabilities", f"${total_liabilities:,.2f}")
            col2.metric("Overdue Liabilities", f"${overdue_liabilities:,.2f}")
            col3.metric("Outstanding Liabilities", f"${total_liabilities - overdue_liabilities:,.2f}")

            # Party-wise summary
            party_summary = liability_df.groupby('party_name').agg(
                total_amount=('amount', 'sum'),
                overdue_amount=('amount', lambda x: x[liability_df['status'].str.lower() != 'paid'].sum()),
                count=('voucher_no', 'count')
            ).reset_index()

            st.subheader("Party-wise Liability Summary")
            st.dataframe(party_summary.sort_values('total_amount', ascending=False), hide_index=True)

            # Visualizations
            fig1 = px.bar(party_summary, x='party_name', y='total_amount', title="Total Liabilities by Party")
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(party_summary, names='party_name', values='total_amount', title="Liability Distribution", hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)

            # Detailed transactions
            st.subheader("🔍 Detailed Liability Transactions")
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect("Filter by Status", options=liability_df['status'].unique(), default=liability_df['status'].unique())
            with col2:
                party_filter = st.multiselect("Filter by Party", options=liability_df['party_name'].unique(), default=liability_df['party_name'].unique())

            filtered_df = liability_df.copy()
            if status_filter:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            if party_filter:
                filtered_df = filtered_df[filtered_df['party_name'].isin(party_filter)]

            # Display columns
            default_cols = ['due_date', 'voucher_no', 'party_name', 'amount', 'status', 'account_head', 'sub_category']
            optional_cols = ['particulars', 'reference']
            selected_cols = st.multiselect("Select columns to display", options=optional_cols, default=optional_cols)
            display_cols = default_cols + [col for col in selected_cols if col in liability_df.columns]

            st.dataframe(
                filtered_df[display_cols].sort_values('due_date', ascending=False),
                hide_index=True,
                column_config={
                    "due_date": st.column_config.DateColumn("Due Date", format="YYYY-MM-DD"),
                    "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                    "status": st.column_config.TextColumn("Status")
                }
            )











# ================= INCOME SUMMARY =================
elif choice == "💰 Income" and not df.empty:
    st.header("💰 Income Summary")

    required_cols = ["amount", "payment_date", "account_head", "category", "sub_category", "party_name", "payment_method", "account_name"]
    if all(col in df.columns for col in required_cols):

        # Clean and convert
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')

        # Filter income entries
        income_df = df[
            df['account_head'].str.contains("Income|Revenue|Sales", case=False, na=False) |
            df['category'].str.contains("Income|Revenue", case=False, na=False) |
            df['sub_category'].str.contains("Income|Sales", case=False, na=False)
        ].copy()

        if not income_df.empty:
            # Date range filter
            min_date = income_df['payment_date'].min().date()
            max_date = income_df['payment_date'].max().date()
            date_range = st.date_input("Select Payment Date Range", [min_date, max_date])

            if len(date_range) == 2:
                income_df = income_df[
                    (income_df['payment_date'].dt.date >= date_range[0]) &
                    (income_df['payment_date'].dt.date <= date_range[1])
                ]

            # Additional filters
            col1, col2 = st.columns(2)
            with col1:
                method_filter = st.multiselect("Filter by Payment Method", income_df['payment_method'].dropna().unique())
            with col2:
                account_filter = st.multiselect("Filter by Account Name", income_df['account_name'].dropna().unique())

            if method_filter:
                income_df = income_df[income_df['payment_method'].isin(method_filter)]
            if account_filter:
                income_df = income_df[income_df['account_name'].isin(account_filter)]

            # Metrics
            total_income = income_df['amount'].sum()
            top_party = income_df.groupby('party_name')['amount'].sum().idxmax()
            top_amount = income_df.groupby('party_name')['amount'].sum().max()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"${total_income:,.2f}")
            col2.metric("Top Contributor", f"{top_party}")
            col3.metric("Top Contribution", f"${top_amount:,.2f}")

            # 📈 Line chart: Income over time
            trend_df = income_df.groupby(income_df['payment_date'].dt.to_period('M')).agg(total_income=('amount', 'sum')).reset_index()
            trend_df['payment_date'] = trend_df['payment_date'].dt.to_timestamp()
            fig_trend = px.line(trend_df, x='payment_date', y='total_income', markers=True, title="Monthly Income Trend")
            st.plotly_chart(fig_trend, use_container_width=True)

            # 📊 Category-wise summary
            category_summary = income_df.groupby('sub_category').agg(
                total_amount=('amount', 'sum'),
                transaction_count=('voucher_no', 'count')
            ).reset_index()

            st.subheader("Category-wise Income Summary")
            st.dataframe(category_summary.sort_values('total_amount', ascending=False), hide_index=True)

            fig1 = px.bar(category_summary, x='sub_category', y='total_amount', title="Income by Sub-Category")
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(category_summary, names='sub_category', values='total_amount', title="Income Distribution", hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)

            # 🔍 Detailed transactions with color-coded tags
            st.subheader("🔍 Detailed Income Transactions")
            party_filter = st.multiselect("Filter by Party", income_df['party_name'].unique(), default=income_df['party_name'].unique())
            filtered_df = income_df[income_df['party_name'].isin(party_filter)]

            # Add color-coded tags for high-value transactions
            def tag_amount(val):
                if val >= 100000:
                    return f"🟢 ${val:,.2f}"
                elif val >= 50000:
                    return f"🟡 ${val:,.2f}"
                else:
                    return f"🔴 ${val:,.2f}"

            display_df = filtered_df.copy()
            display_df['Tagged Amount'] = display_df['amount'].apply(tag_amount)

            display_cols = ['payment_date', 'voucher_no', 'party_name', 'Tagged Amount', 'account_head', 'sub_category', 'category', 'payment_method', 'account_name', 'particulars']
            st.dataframe(
                display_df[display_cols].sort_values('payment_date', ascending=False),
                hide_index=True,
                column_config={
                    "payment_date": st.column_config.DateColumn("Payment Date", format="YYYY-MM-DD"),
                    "Tagged Amount": st.column_config.TextColumn("Amount (Tagged)")
                }
            )


# ================= EXPENSE DETAILS =================
elif choice == "💸 Expense" and not df.empty:
    st.header("💸 Expense Details")

    required_cols = ["credit", "payment_date", "account_head", "category", "sub_category", "party_name"]
    if all(col in df.columns for col in required_cols):

        # --- Data Cleaning ---
        df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')

        # --- Filter expense entries ---
        expense_df = df[
            df['account_head'].str.contains("Expense|Purchase|Cost", case=False, na=False) |
            df['category'].str.contains("Expense|Purchase", case=False, na=False) |
            df['sub_category'].str.contains("Expense|Purchase", case=False, na=False)
        ].copy()

        if not expense_df.empty:
            # 📅 Date range filter
            min_date = expense_df['payment_date'].min().date()
            max_date = expense_df['payment_date'].max().date()
            date_range = st.date_input("Select Payment Date Range", [min_date, max_date])

            if len(date_range) == 2:
                expense_df = expense_df[
                    (expense_df['payment_date'].dt.date >= date_range[0]) &
                    (expense_df['payment_date'].dt.date <= date_range[1])
                ]

            # 📂 Sub-category-wise summary (using amount, not credit)
            subcat_summary = expense_df.groupby('sub_category').agg(
                total_amount=('credit', 'sum'),
                transaction_count=('voucher_no', 'count')
            ).reset_index()

            st.subheader("📂 Sub-Category-wise Expense Summary")
            st.dataframe(
                subcat_summary.sort_values('total_amount', ascending=False),
                hide_index=True
            )

            # 📊 Bar chart
            fig_bar = px.bar(
                subcat_summary,
                x='sub_category',
                y='total_amount',
                title="💸 Expenses by Sub-Category",
                labels={'sub_category': 'Sub-Category', 'total_amount': 'Total Amount'},
                color='total_amount',
                color_continuous_scale='Reds',
                hover_data={'transaction_count': True}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)

            # 🥧 Pie chart
            fig_pie = px.pie(
                subcat_summary,
                names='sub_category',
                values='total_amount',
                title="💰 Expense Distribution by Sub-Category",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # 📈 Line chart: Expense trend over time
            trend_df = expense_df.groupby(expense_df['payment_date'].dt.to_period('M')).agg(
                monthly_expense=('credit', 'sum')
            ).reset_index()
            trend_df['payment_date'] = trend_df['payment_date'].dt.to_timestamp()

            fig_line = px.line(
                trend_df,
                x='payment_date',
                y='monthly_expense',
                markers=True,
                title="📅 Monthly Expense Trend",
                labels={'payment_date': 'Month', 'monthly_expense': 'Total Expense'}
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # 🔍 Detailed transaction table
            st.subheader("🔍 Detailed Expense Transactions")
            party_filter = st.multiselect(
                "Filter by Party",
                options=sorted(expense_df['party_name'].dropna().unique()),
                default=sorted(expense_df['party_name'].dropna().unique())
            )
            filtered_df = expense_df[expense_df['party_name'].isin(party_filter)]

            display_cols = [
                'payment_date', 'voucher_no', 'party_name',
                'credit', 'account_head', 'sub_category', 'category', 'particulars'
            ]
            st.dataframe(
                filtered_df[display_cols].sort_values('payment_date', ascending=False),
                hide_index=True,
                column_config={
                    "payment_date": st.column_config.DateColumn("Payment Date", format="YYYY-MM-DD"),
                    "amount": st.column_config.NumberColumn("credit", format="$%.2f")
                }
            )
        else:
            st.warning("⚠️ No expense records found for the given criteria.")
    else:
        st.error(f"Missing required columns: {set(required_cols) - set(df.columns)}")



elif choice == "📑 MD Report":
    st.header("📑 Managing Director Report")
    
    # Convert date column if exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Date range filter with validation
    min_date = df['date'].min().date() if 'date' in df.columns else None
    max_date = df['date'].max().date() if 'date' in df.columns else None
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
    with col2:
        end_date = st.date_input(
            "📅 End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
    
    # Validate date range
    if start_date > end_date:
        st.error("⚠ End date must be after start date")
        st.stop()

    # Current date for letter header
    current_date = datetime.today().strftime("%d %B %Y")
    
    # Company information (configurable)
    company_name = st.text_input("Company Name", value="Metal Private Ltd")
    company_address = st.text_input("Company Address", value="Dhaka, Bangladesh")
    analyst_name = st.text_input("Analyst Name", value="Mujakkir Ahmad")
    
    # Letter-style Header with customization
    st.markdown(f"""
    <style>
        .report-header {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        .report-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
    </style>
    
    <div class="report-header">
        <div style="text-align: right;">Date: {current_date}</div>
        <div>To,</div>
        <div>Dear Managing Director</div>
        <div><strong>{company_name}</strong></div>
        <div>{company_address}</div>
        <br>
        <div><strong>Dear Sir,</strong></div>
        <div>This is the financial report for the selected date range <strong>{start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}</strong>.</div>
        <div>You can view <strong>sales, expenses, loans, payables, receivables</strong> summary here.</div>
        <div>If there are any unusual or extra expenses detected, please inform the <strong>Accounts Department</strong> for necessary action.</div>
        <br>
        <div><strong>Best Regards,</strong></div>
        <div>{analyst_name}</div>
        <div>Data Analyst</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if start_date and end_date:
        try:
            # Filter data and ensure numeric values
            mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
            filtered_df = df.loc[mask].copy()
            
            # Convert numeric columns safely
            numeric_cols = ['debit', 'credit', 'amount', 'bank_deposit', 'bank_withdrawal']
            for col in numeric_cols:
                if col in filtered_df.columns:
                    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce').fillna(0)
            
            # KPI Calculations with error handling
            total_sales = filtered_df[filtered_df['category'] == "Income"]['debit'].sum()
            total_expenses = filtered_df[filtered_df['category'] == "Expense"]['credit'].sum()
            total_loans = filtered_df[filtered_df['category'] == "Loan"]['debit'].sum()
            
            # Payables/Receivables with status check
            if 'status' in filtered_df.columns:
                total_payables = filtered_df[(filtered_df['party_type'] == "Vendor") & 
                                           (~filtered_df['status'].str.contains("Paid", na=False))]['amount'].sum()
                total_receivables = filtered_df[(filtered_df['party_type'] == "Customer") & 
                                               (~filtered_df['status'].str.contains("Received", na=False))]['amount'].sum()
            else:
                total_payables = filtered_df[filtered_df['party_type'] == "Vendor"]['amount'].sum()
                total_receivables = filtered_df[filtered_df['party_type'] == "Customer"]['amount'].sum()
            
            # Calculate balance
            total_balance = (filtered_df['debit'].sum() - filtered_df['credit'].sum()) + \
                          (filtered_df['bank_deposit'].sum() - filtered_df['bank_withdrawal'].sum())
            
            # KPI Cards with conditional coloring
            kpi_cols = st.columns(6)
            kpi_metrics = [
                ("💰 Sales", total_sales, None),
                ("💸 Expenses", total_expenses, "inverse"),
                ("🏦 Loans", total_loans, None),
                ("📂 Payables", total_payables, "inverse"),
                ("📥 Receivables", total_receivables, None),
                ("💳 Current Balance", total_balance, "normal")
            ]
            
            for i, (title, value, delta_type) in enumerate(kpi_metrics):
                with kpi_cols[i]:
                    formatted_value = f"{value:,.2f}" if not pd.isna(value) else "N/A"
                    if delta_type == "inverse" and value > 0:
                        st.metric(title, formatted_value, delta="⚠ High", delta_color="inverse")
                    elif delta_type == "normal" and value < 0:
                        st.metric(title, formatted_value, delta="⚠ Negative", delta_color="inverse")
                    else:
                        st.metric(title, formatted_value)
            
            st.markdown("---")
            
            # Drill-down details with improved display
            st.subheader("🔍 Category-wise Summary")
            
            if 'category' in filtered_df.columns:
                cat_summary = filtered_df.groupby(['category']).agg(
                    total_debit=('debit', 'sum'),
                    total_credit=('credit', 'sum'),
                    transaction_count=('amount', 'count')
                ).reset_index()
                
                # Add net amount calculation
                cat_summary['net_amount'] = cat_summary['total_debit'] - cat_summary['total_credit']
                
                # Display summary table with sorting options
                sort_option = st.selectbox("Sort by:", 
                                         ["Net Amount (High-Low)", "Net Amount (Low-High)", 
                                          "Transaction Count", "Category Name"])
                
                if sort_option == "Net Amount (High-Low)":
                    cat_summary = cat_summary.sort_values('net_amount', ascending=False)
                elif sort_option == "Net Amount (Low-High)":
                    cat_summary = cat_summary.sort_values('net_amount', ascending=True)
                elif sort_option == "Transaction Count":
                    cat_summary = cat_summary.sort_values('transaction_count', ascending=False)
                else:
                    cat_summary = cat_summary.sort_values('category')
                
                # Display expandable sections
                for _, row in cat_summary.iterrows():
                    with st.expander(f"{row['category']} - Net: {row['net_amount']:,.2f} (Transactions: {row['transaction_count']})"):
                        cat_data = filtered_df[filtered_df['category'] == row['category']]
                        
                        # Show summary stats
                        st.write(f"**Debit Total:** {row['total_debit']:,.2f}")
                        st.write(f"**Credit Total:** {row['total_credit']:,.2f}")
                        
                        # Show detailed transactions
                        st.dataframe(cat_data)
            else:
                st.warning("No 'category' column found in dataset")
            
            st.markdown("---")
            
            # Enhanced Balance Sheet with ratios
            st.subheader("📊 Financial Position Summary")
            
            assets = total_balance + total_receivables
            liabilities = total_payables + total_loans
            equity = assets - liabilities
            
            # Financial ratios
            current_ratio = (total_balance + total_receivables) / (total_payables + total_loans) if (total_payables + total_loans) != 0 else float('inf')
            debt_to_equity = (total_payables + total_loans) / equity if equity != 0 else float('inf')
            
            balance_df = pd.DataFrame({
                "Item": ["Assets", "Liabilities", "Equity"],
                "Amount": [assets, liabilities, equity]
            })
            
            # Display ratios
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Ratio", f"{current_ratio:.2f}", 
                          help="(Current Assets / Current Liabilities) - Higher is better")
            with col2:
                st.metric("Debt-to-Equity", f"{debt_to_equity:.2f}", 
                          help="(Total Liabilities / Shareholders' Equity) - Lower is better")
            
            # Interactive chart
            chart_type = st.radio("Chart Type:", ["Pie Chart", "Bar Chart"])
            
            if chart_type == "Pie Chart":
                fig = px.pie(balance_df, names='Item', values='Amount', 
                            title="Financial Position Composition",
                            hole=0.3)
            else:
                fig = px.bar(balance_df, x='Item', y='Amount', 
                            title="Financial Position Summary",
                            color='Item')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Download button for the report
            st.download_button(
                label="📥 Download Full Report",
                data=balance_df.to_csv(index=False),
                file_name=f"MD_Report_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"An error occurred while generating the report: {str(e)}")
            st.error("Please check your data format and try again")

# ================= ACCOUNTS PAYABLE =================
elif choice == "📂 Payables":
    st.header("📂 Accounts Payable (Vendors)")

    # Ensure date column type
    if "due_date" in df.columns:
        df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')

    # Filter vendor unpaid
    payable_df = df[
        (df['party_type'].str.lower() == "vendor") &
        (df['status'].str.lower() != "paid")
    ].copy()

    if payable_df.empty:
        st.info("✅ No outstanding payables. All vendor bills are paid.")
    else:
        # Highlight overdue
        today = pd.Timestamp.today()

        def highlight_overdue(row):
            if pd.notnull(row['due_date']) and row['due_date'] < today:
                return ['background-color: #ffcccc'] * len(row)
            return [''] * len(row)

        # Total payable
        total_payable = payable_df['amount'].sum()

        # Vendor-wise summary
        vendor_summary = (
            payable_df.groupby('party_name', dropna=False)
            .agg(total_due=('amount', 'sum'), invoice_count=('voucher_no', 'count'))
            .reset_index()
            .sort_values(by="total_due", ascending=False)
        )

        # Metrics
        st.metric("💰 Total Payable", f"{total_payable:,.2f}")

        # Pie chart vendor share
        fig = px.pie(vendor_summary, values='total_due', names='party_name',
                     title="Payable by Vendor", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

        # Table - highlighted overdue
        st.subheader("📄 Detailed Payable List")
        st.dataframe(payable_df.style.apply(highlight_overdue, axis=1))

        # Table - vendor summary
        st.subheader("📌 Vendor Summary")
        st.dataframe(vendor_summary)


# ================= ACCOUNTS RECEIVABLE =================
elif choice == "📥 Receivables":
    st.header("📂 Accounts Receivable Aging Report")
    
    # Convert date columns
    date_cols = ['date', 'invoice_date', 'due_date', 'payment_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Filter receivables (customer invoices not fully paid)
    if all(col in df.columns for col in ['party_type', 'status', 'amount']):
        receivable_df = df[
            (df['party_type'].str.lower().str.contains('customer')) &
            (~df['status'].str.lower().str.contains('received|paid'))
        ].copy()
    else:
        st.error("Required columns (party_type, status, amount) not found in dataset")
        st.stop()
    
    if receivable_df.empty:
        st.success("✅ No outstanding receivables. All customer payments are received.")
        st.stop()
    
    # Calculate aging
    today = pd.Timestamp.today()
    receivable_df['days_overdue'] = (today - receivable_df['due_date']).dt.days
    receivable_df['aging_bucket'] = pd.cut(
        receivable_df['days_overdue'],
        bins=[-1, 0, 30, 60, 90, float('inf')],
        labels=['Not Due', '0-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
    )
    
    # Total metrics
    total_receivable = receivable_df['amount'].sum()
    overdue_amount = receivable_df[receivable_df['days_overdue'] > 0]['amount'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Receivable", f"${total_receivable:,.2f}")
    col2.metric("⚠️ Overdue Amount", f"${overdue_amount:,.2f}", 
               delta=f"{overdue_amount/total_receivable:.0%} of total" if total_receivable > 0 else "N/A")
    col3.metric("🧾 Unpaid Invoices", len(receivable_df))
    
    # Aging analysis
    st.subheader("⏳ Receivable Aging Analysis")
    aging_summary = receivable_df.groupby('aging_bucket').agg(
        amount=('amount', 'sum'),
        count=('voucher_no', 'count')
    ).reset_index()
    
    # Visualizations
    tab1, tab2, tab3 = st.tabs(["Aging Chart", "Customer Breakdown", "Detailed List"])
    
    with tab1:
        fig1 = px.bar(aging_summary, x='aging_bucket', y='amount', 
                      title="Receivable Aging by Amount",
                      color='aging_bucket',
                      color_discrete_map={
                          'Not Due':'#636EFA',
                          '0-30 Days':'#00CC96',
                          '31-60 Days':'#FECB52',
                          '61-90 Days':'#EF553B',
                          '90+ Days':'#AB63FA'
                      })
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.pie(aging_summary, values='amount', names='aging_bucket',
                     title="Aging Distribution", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        customer_summary = receivable_df.groupby('party_name').agg(
            total_due=('amount', 'sum'),
            oldest_invoice=('due_date', 'min'),
            invoice_count=('voucher_no', 'count'),
            avg_days_overdue=('days_overdue', 'mean')
        ).sort_values('total_due', ascending=False)
        
        st.dataframe(
            customer_summary.style.format({
                'total_due': "${:,.2f}",
                'avg_days_overdue': "{:.1f} days"
            }).background_gradient(subset=['total_due'], cmap='Blues'),
            use_container_width=True
        )
        
        # Top 10 customers chart
        top_customers = customer_summary.head(10).reset_index()
        fig3 = px.bar(top_customers, x='party_name', y='total_due',
                      title="Top 10 Customers by Receivable Amount")
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab3:
        # Enhanced styling for detailed list
        def highlight_overdue(row):
            if row['days_overdue'] > 90:
                return ['background-color: #ffb3ba']*len(row)
            elif row['days_overdue'] > 60:
                return ['background-color: #ffdfba']*len(row)
            elif row['days_overdue'] > 30:
                return ['background-color: #ffffba']*len(row)
            elif row['days_overdue'] > 0:
                return ['background-color: #baffc9']*len(row)
            else:
                return ['']*len(row)
        
        # Select columns to display
        display_cols = ['date', 'due_date', 'party_name', 'voucher_no', 
                       'amount', 'days_overdue', 'aging_bucket', 'status']
        display_cols = [col for col in display_cols if col in receivable_df.columns]
        
        st.dataframe(
            receivable_df[display_cols].style
                .apply(highlight_overdue, axis=1)
                .format({
                    'amount': "${:,.2f}",
                    'days_overdue': "{:.0f}"
                }),
            use_container_width=True,
            height=600
        )
    
    # Export options
    st.download_button(
        label="📥 Download Aging Report (CSV)",
        data=receivable_df.to_csv(index=False),
        file_name="receivable_aging_report.csv",
        mime="text/csv"
    )
# ================= BANK TRANSACTIONS =================
elif choice == "🏧 Bank Txns" and not df.empty:
    st.header("🏦 Bank Transactions")

    # Ensure required columns exist
    required_cols = ["bank_deposit", "bank_withdrawal", "payment_date", "payment_method", "account_head"]
    if all(col in df.columns for col in required_cols):
        
        # Clean and convert types
        df['bank_deposit'] = pd.to_numeric(df['bank_deposit'], errors='coerce').fillna(0)
        df['bank_withdrawal'] = pd.to_numeric(df['bank_withdrawal'], errors='coerce').fillna(0)
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
        
        # Filter bank transactions
        bank_df = df[
            (df['account_head'].str.contains("Bank|Cash", case=False, na=False)) |
            (df['category'].str.contains("Bank|Cash", case=False, na=False)) |
            (df['sub_category'].str.contains("Bank|Cash", case=False, na=False))
        ].copy()
        
        if not bank_df.empty:
            # Date range filter
            min_date = bank_df['payment_date'].min().date()
            max_date = bank_df['payment_date'].max().date()
            date_range = st.date_input("Select Payment Date Range", [min_date, max_date])
            
            # Calculate totals
            total_deposit = bank_df['bank_deposit'].sum()
            total_withdrawal = bank_df['bank_withdrawal'].sum()
            net_flow = total_deposit - total_withdrawal
            
            # Filter by date range
            if len(date_range) == 2:
                bank_df = bank_df[
                    (bank_df['payment_date'].dt.date >= date_range[0]) & 
                    (bank_df['payment_date'].dt.date <= date_range[1])
                ]
            
            # Further filter by payment method if available
            if 'payment_method' in bank_df.columns:
                payment_methods = bank_df['payment_method'].dropna().unique()
                selected_methods = st.multiselect("Filter by Payment Method", options=payment_methods, default=payment_methods)
                if selected_methods:
                    bank_df = bank_df[bank_df['payment_method'].isin(selected_methods)]
                
                # Reapply date range filter after payment method selection
                bank_df = bank_df[
                    (bank_df['payment_date'].dt.date >= date_range[0]) & 
                    (bank_df['payment_date'].dt.date <= date_range[1])
                ]
            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Deposit", f"${total_deposit:,.2f}")
            col2.metric("Total Withdrawal", f"${total_withdrawal:,.2f}")
            col3.metric("Net Cash Flow", f"${net_flow:,.2f}")
            # Visualizations
            st.subheader("📊 Visualizations")  
            tab1, tab2, tab3 = st.tabs(["Deposit", "Withdrawal", "Transaction Count"])
            with tab1:
                st.markdown("#### Deposit by Sub-Category")
                col1, col2 = st.columns([3, 2])
                with col1:
                    # Bar chart for deposits by sub-category
                    subcat_data = bank_df.groupby(['sub_category', 'category']).agg(
                        total_deposit=('bank_deposit', 'sum'),
                        count=('voucher_no', 'nunique')
                    ).reset_index()
                    
                    fig_bar = px.bar(
                        subcat_data.sort_values('total_deposit', ascending=False),
                        x='sub_category',
                        y='total_deposit',
                        color='category',
                        title="Deposit Amount by Sub-Category",
                        labels={'total_deposit': 'Deposit Amount', 'sub_category': 'Sub-Category'}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Pie chart for deposit distribution
                    fig_pie = px.pie(
                        subcat_data,
                        values='total_deposit',
                        names='sub_category',
                        title="Deposit Distribution",
                        hole=0.3
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            with tab2:
                st.markdown("#### Withdrawal by Sub-Category")
                col1, col2 = st.columns([3, 2])
                with col1:
                    # Bar chart for withdrawals by sub-category
                    subcat_data = bank_df.groupby(['sub_category', 'category']).agg(
                        total_withdrawal=('bank_withdrawal', 'sum'),
                        count=('voucher_no', 'nunique')
                    ).reset_index()
                    
                    fig_bar = px.bar(
                        subcat_data.sort_values('total_withdrawal', ascending=False),
                        x='sub_category',
                        y='total_withdrawal',
                        color='category',
                        title="Withdrawal Amount by Sub-Category",
                        labels={'total_withdrawal': 'Withdrawal Amount', 'sub_category': 'Sub-Category'}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Pie chart for withdrawal distribution
                    fig_pie = px.pie(
                        subcat_data,
                        values='total_withdrawal',
                        names='sub_category',
                        title="Withdrawal Distribution",
                        hole=0.3
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            with tab3:
                st.markdown("#### Transaction Count by Sub-Category")
                col1, col2 = st.columns([3, 2])
                with col1:
                    # Bar chart for transaction count by sub-category
                    subcat_data = bank_df.groupby(['sub_category', 'category']).agg(
                        transaction_count=('voucher_no', 'nunique')
                    ).reset_index()
                    
                    fig_bar = px.bar(
                        subcat_data.sort_values('transaction_count', ascending=False),
                        x='sub_category',
                        y='transaction_count',
                        color='category',
                        title="Transaction Count by Sub-Category",
                        labels={'transaction_count': 'Transaction Count', 'sub_category': 'Sub-Category'}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Pie chart for transaction distribution
                    fig_pie = px.pie(
                        subcat_data,
                        values='transaction_count',
                        names='sub_category',
                        title="Transaction Distribution",
                        hole=0.3
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            # Detailed transactions
            st.subheader("🔍 Detailed Bank Transactions")
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect("Filter by Status", options=bank_df['status'].unique(), default=bank_df['status'].unique())  
            with col2:
                party_filter = st.multiselect("Filter by Party", options=bank_df['party_name'].unique(), default=bank_df['party_name'].unique())        
            filtered_df = bank_df.copy()
            if status_filter:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            if party_filter:
                filtered_df = filtered_df[filtered_df['party_name'].isin(party_filter)]
            # Display columns
            default_cols = ['payment_date', 'voucher_no', 'party_name', 'bank_deposit', 'bank_withdrawal', 'amount', 'payment_method', 'account_head', 'sub_category']
            optional_cols = ['particulars', 'reference']
            selected_cols = st.multiselect("Select columns to display", options=optional_cols, default=optional_cols)
            display_cols = default_cols + [col for col in selected_cols if col in bank_df.columns]
            st.dataframe(
                filtered_df[display_cols].sort_values('payment_date', ascending=False),
                hide_index=True,
                column_config={
                    "payment_date": st.column_config.DateColumn("Payment Date", format="YYYY-MM-DD"),
                    "voucher_no": st.column_config.TextColumn("Voucher No"),
                    "party_name": st.column_config.TextColumn("Party Name"),
                    "bank_deposit": st.column_config.NumberColumn("Deposit", format="$%.2f"),
                    "bank_withdrawal": st.column_config.NumberColumn("Withdrawal", format="$%.2f"),})
            st.markdown("**Note:** The above transactions are filtered based on the selected date range and payment methods. You can adjust the filters to view specific transactions.")



# ================= Forecasting =================
elif choice == "📈 Forecast":
    st.header("📈 Financial Forecasting")

    # Ensure date column exists
    if "date" not in df.columns:
        st.warning("❌ 'date' column not found in dataset.")
    else:
        # Convert to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert debit and credit columns to numeric, coercing errors to NaN
        df['debit'] = pd.to_numeric(df['debit'], errors='coerce')
        df['credit'] = pd.to_numeric(df['credit'], errors='coerce')
        
        # Fill NaN values with 0 for calculation
        df['debit'] = df['debit'].fillna(0)
        df['credit'] = df['credit'].fillna(0)

        # Group daily net cash flow
        daily_data = df.groupby('date').agg(
            total_debit=('debit', 'sum'),
            total_credit=('credit', 'sum')
        ).reset_index()

        daily_data['net_cashflow'] = daily_data['total_credit'] - daily_data['total_debit']

        # Prepare Prophet dataset
        forecast_df = daily_data[['date', 'net_cashflow']].rename(
            columns={"date": "ds", "net_cashflow": "y"}
        ).dropna()

        try:
            from prophet import Prophet
            model = Prophet()
            model.fit(forecast_df)

            # Future dates (next 90 days)
            future = model.make_future_dataframe(periods=90)
            forecast = model.predict(future)

            # Plot forecast
            fig1 = model.plot(forecast)
            st.pyplot(fig1)

            # Plot components (trend, yearly seasonality, etc.)
            fig2 = model.plot_components(forecast)
            st.pyplot(fig2)

            # Show forecast table
            st.subheader("🔮 Forecast Data")
            st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

        except ModuleNotFoundError:
            st.error("⚠ Prophet library not installed. Run: pip install prophet")
        except Exception as e:
            st.error(f"❗ An error occurred while forecasting: {e}")
        else:
            st.success("✅ Forecasting completed successfully!")


# ================= Balance Sheet =================
elif choice == "⚖ Balance Sheet":
    st.header("⚖ Balance Sheet")
    
    # Add explanatory text
    st.markdown("""
    This section provides a comprehensive view of your company's financial position, 
    showing assets, liabilities, and equity at a specific point in time.
    """)
    
    # Date range selector for balance sheet snapshot
    if 'date' in df.columns:
        try:
            df['date'] = pd.to_datetime(df['date'])
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            snapshot_date = st.date_input(
                "Select Balance Sheet Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                help="View balance sheet as of this date"
            )
            
            # Filter data up to selected date
            df = df[df['date'] <= pd.to_datetime(snapshot_date)]
        except Exception as e:
            st.warning(f"Could not filter by date: {str(e)}")
    
    # Ensure required columns exist with case-insensitive check
    required_cols = ["account_name", "account_type", "amount"]
    missing_cols = [col for col in required_cols if col.lower() not in [c.lower() for c in df.columns]]
    
    if missing_cols:
        st.warning(f"⚠ Required columns not found: {', '.join(missing_cols)}")
        st.info("Please ensure your dataset contains: account_name, account_type, and amount columns")
        st.stop()
    
    try:
        # Standardize column names (case-insensitive)
        col_mapping = {col: required_cols[i] for i, col in enumerate(df.columns) 
                      if col.lower() in [c.lower() for c in required_cols]}
        df = df.rename(columns=col_mapping)
        
        # Clean and convert data types
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        df['account_type'] = df['account_type'].astype(str).str.strip().str.lower()
        
        # Filter assets and liabilities with error handling
        valid_types = ['asset', 'liability', 'equity', 'capital', 'retained earnings']
        df_filtered = df[df['account_type'].isin(valid_types)].copy()
        
        # Map similar account types
        df_filtered['account_type'] = df_filtered['account_type'].replace({
            'capital': 'equity',
            'retained earnings': 'equity'
        })
        
        if df_filtered.empty:
            st.warning("No valid balance sheet accounts found (looking for types: asset, liability, equity)")
            st.stop()
        
        # Categorize accounts
        assets_df = df_filtered[df_filtered['account_type'] == "asset"]
        liabilities_df = df_filtered[df_filtered['account_type'] == "liability"]
        equity_df = df_filtered[df_filtered['account_type'] == "equity"]
        
        # Calculate totals
        total_assets = assets_df['amount'].sum()
        total_liabilities = liabilities_df['amount'].sum()
        total_equity = equity_df['amount'].sum() if not equity_df.empty else (total_assets - total_liabilities)
        
        # Balance sheet summary with ratios
        st.subheader("📊 Balance Sheet Summary")
        
        # Create balance sheet overview
        balance_sheet = pd.DataFrame({
            'Category': ['Assets', 'Liabilities', 'Equity'],
            'Amount': [total_assets, total_liabilities, total_equity]
        })
        
        # Display balance sheet with styling
        st.dataframe(
            balance_sheet.style.format({
                'Amount': "${:,.2f}"
            }).apply(lambda x: ['background-color: #e6f3ff' if x.name == 0 
                              else 'background-color: #ffe6e6' if x.name == 1
                              else 'background-color: #e6ffe6' for i, x in enumerate(balance_sheet.iterrows())], 
                    axis=1),
            hide_index=True,
            column_config={
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Amount": st.column_config.NumberColumn("Amount", format="$%.2f")
            }
        )
        
        # Financial ratios with color coding
        st.subheader("📈 Financial Health Indicators")
        
        current_ratio = total_assets / total_liabilities if total_liabilities != 0 else float('inf')
        debt_to_equity = total_liabilities / total_equity if total_equity != 0 else float('inf')
        working_capital = total_assets - total_liabilities
        
        # Determine colors for ratios
        def get_ratio_color(value, ratio_type):
            if ratio_type == "current":
                return "green" if value > 1.5 else "orange" if value > 1 else "red"
            elif ratio_type == "debt":
                return "green" if value < 0.5 else "orange" if value < 1 else "red"
            else:
                return "green" if value > 0 else "red"
        
        ratio_col1, ratio_col2, ratio_col3 = st.columns(3)
        ratio_col1.metric(
            "Current Ratio", 
            f"{current_ratio:.2f}", 
            help="Measures short-term liquidity (Assets / Liabilities)",
            delta_color="off"
        )
        ratio_col1.progress(
            min(1, current_ratio/3), 
            text=f"{'✅ Healthy' if current_ratio > 1.5 else '⚠ Caution' if current_ratio > 1 else '❌ Risk'}"
        )
        
        ratio_col2.metric(
            "Debt-to-Equity", 
            f"{debt_to_equity:.2f}",
            help="Measures financial leverage (Liabilities / Equity)",
            delta_color="off"
        )
        ratio_col2.progress(
            min(1, debt_to_equity/3),
            text=f"{'✅ Healthy' if debt_to_equity < 0.5 else '⚠ Caution' if debt_to_equity < 1 else '❌ Risk'}"
        )
        
        ratio_col3.metric(
            "Working Capital", 
            f"${working_capital:,.2f}",
            help="Measures operational liquidity (Assets - Liabilities)",
            delta_color="off"
        )
        ratio_col3.progress(
            min(1, working_capital/(total_assets+0.0001)),
            text=f"{'✅ Positive' if working_capital > 0 else '❌ Negative'}"
        )
        
        # Detailed breakdowns with tabs
        tab1, tab2, tab3 = st.tabs(["🧮 Assets", "📉 Liabilities", "📈 Equity"])
        
        with tab1:
            if not assets_df.empty:
                # Classify assets as current/fixed
                assets_df['asset_class'] = assets_df['account_name'].apply(
                    lambda x: "Current Assets" if any(word in x.lower() for word in ['cash', 'receivable', 'inventory']) 
                    else "Fixed Assets"
                )
                
                asset_class_summary = assets_df.groupby('asset_class').agg(
                    total_amount=('amount', 'sum')
                ).reset_index()
                
                st.plotly_chart(px.pie(
                    asset_class_summary, 
                    values='total_amount', 
                    names='asset_class',
                    title="Asset Classification",
                    hole=0.4,
                    color='asset_class',
                    color_discrete_map={'Current Assets':'lightblue','Fixed Assets':'darkblue'}
                ), use_container_width=True)
                
                asset_summary = assets_df.groupby('account_name').agg(
                    total_amount=('amount', 'sum'),
                    percentage=('amount', lambda x: (x.sum() / total_assets * 100) if total_assets != 0 else 0)
                ).sort_values('total_amount', ascending=False)
                
                st.dataframe(
                    asset_summary.style.format({
                        'total_amount': "${:,.2f}",
                        'percentage': "{:.1f}%"
                    }).bar(subset=['percentage'], color='#5fba7d'),
                    use_container_width=True,
                    height=400
                )
            else:
                st.warning("No asset accounts found")
        
        with tab2:
            if not liabilities_df.empty:
                # Classify liabilities as current/long-term
                liabilities_df['liability_class'] = liabilities_df['account_name'].apply(
                    lambda x: "Current Liabilities" if any(word in x.lower() for word in ['payable', 'short', 'due']) 
                    else "Long-Term Liabilities"
                )
                
                st.plotly_chart(px.pie(
                    liabilities_df.groupby('liability_class').sum().reset_index(),
                    values='amount', 
                    names='liability_class',
                    title="Liability Classification",
                    hole=0.4,
                    color='liability_class',
                    color_discrete_map={'Current Liabilities':'lightcoral','Long-Term Liabilities':'darkred'}
                ), use_container_width=True)
                
                liability_summary = liabilities_df.groupby('account_name').agg(
                    total_amount=('amount', 'sum'),
                    percentage=('amount', lambda x: (x.sum() / total_liabilities * 100) if total_liabilities != 0 else 0)
                ).sort_values('total_amount', ascending=False)
                
                st.dataframe(
                    liability_summary.style.format({
                        'total_amount': "${:,.2f}",
                        'percentage': "{:.1f}%"
                    }).bar(subset=['percentage'], color='#ff6b6b'),
                    use_container_width=True,
                    height=400
                )
            else:
                st.warning("No liability accounts found")
        
        with tab3:
            if not equity_df.empty:
                equity_summary = equity_df.groupby('account_name').agg(
                    total_amount=('amount', 'sum'),
                    percentage=('amount', lambda x: (x.sum() / total_equity * 100) if total_equity != 0 else 0)
                ).sort_values('total_amount', ascending=False)
                
                st.plotly_chart(px.pie(
                    equity_summary.reset_index(),
                    values='total_amount', 
                    names='account_name',
                    title="Equity Composition",
                    hole=0.4
                ), use_container_width=True)
                
                st.dataframe(
                    equity_summary.style.format({
                        'total_amount': "${:,.2f}",
                        'percentage': "{:.1f}%"
                    }).bar(subset=['percentage'], color='#a5d8ff'),
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("Equity calculated as Net Worth (Assets - Liabilities)")
        
        # Download section
        st.markdown("---")
        st.subheader("📤 Export Balance Sheet")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download as CSV",
                data=df_filtered.to_csv(index=False),
                file_name=f"balance_sheet_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download the full balance sheet data"
            )
        
        with col2:
            # Generate PDF report option
            if st.button("🖨 Generate PDF Report"):
                with st.spinner("Generating PDF report..."):
                    try:
                        from fpdf import FPDF
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.cell(200, 10, txt="Balance Sheet Report", ln=1, align="C")
                        pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=2, align="C")
                        
                        # Add summary to PDF
                        pdf.cell(200, 10, txt="Summary:", ln=3)
                        pdf.cell(200, 10, txt=f"Total Assets: ${total_assets:,.2f}", ln=4)
                        pdf.cell(200, 10, txt=f"Total Liabilities: ${total_liabilities:,.2f}", ln=5)
                        pdf.cell(200, 10, txt=f"Total Equity: ${total_equity:,.2f}", ln=6)
                        
                        # Save to temporary file
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            pdf.output(tmp.name)
                            with open(tmp.name, "rb") as f:
                                st.download_button(
                                    label="⬇ Download PDF",
                                    data=f,
                                    file_name="balance_sheet_report.pdf",
                                    mime="application/pdf"
                                )
                    except Exception as e:
                        st.error(f"Could not generate PDF: {str(e)}")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your data and try again")

# ================= ABOUT ================= 
elif choice == "👨‍⚖️ About":
    st.header("ℹ About this Application")

    st.markdown("""
    This application provides a comprehensive financial analysis tool for businesses. It allows users to:
    - View income and expense summaries
    - Analyze bank transactions
    - Generate balance sheets
    - Forecast financial trends
    - Manage accounts payable and receivable

    Developed by **Mujakkir Ahmad** for **Welburg Metal Pvt Ltd**.
    """)
      
    
# ================= SETTINGS =================
elif choice == "Settings":
    st.header("⚙️ Settings")

    st.subheader("🔧 Application Settings")
    st.markdown("""
    - **Theme:** Dark Mode""")
 


else:
    st.warning("Please upload a valid CSV file to view the financial analysis.")