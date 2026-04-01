import streamlit as st
from main import FamilyExpenseTracker
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from pathlib import Path
import pandas as pd

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Smart Expense Analyzer")
st.markdown("Track & analyze your expenses smartly 🚀")

# -------------------- CSS --------------------
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "main.css"

if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------- SESSION --------------------
if "expense_tracker" not in st.session_state:
    st.session_state.expense_tracker = FamilyExpenseTracker()

expense_tracker = st.session_state.expense_tracker

# -------------------- NAVBAR --------------------
selected = option_menu(
    menu_title=None,
    options=["Add Expense", "View Data", "Analytics"],
    icons=["pencil-fill", "clipboard2-data", "bar-chart-fill"],
    orientation="horizontal",
)

# ==================== ADD EXPENSE ====================
if selected == "Add Expense":

    st.header("👨‍👩‍👧 Add Family Member")

    with st.expander("Add Family Member"):
        name = st.text_input("Name").title()
        earning_status = st.checkbox("Earning Status")

        earnings = st.number_input("Earnings", min_value=0) if earning_status else 0

        if st.button("Add Member"):
            try:
                members = [m for m in expense_tracker.members if m.name == name]

                if not members:
                    expense_tracker.add_family_member(name, earning_status, earnings)
                    st.success("Member added successfully!")
                else:
                    expense_tracker.update_family_member(members[0], earning_status, earnings)
                    st.success("Member updated successfully!")

            except ValueError as e:
                st.error(str(e))

    st.header("💸 Add Expense")

    with st.expander("Add Expense"):
        category = st.selectbox("Category", [
            "Food", "Travel", "Shopping", "Bills", "Medical", "Other"
        ])

        description = st.text_input("Description").title()
        value = st.number_input("Amount", min_value=0)
        date = st.date_input("Date")

        if st.button("Add Expense"):
            try:
                expense_tracker.merge_similar_category(
                    value, category, description, date
                )
                st.success("Expense added successfully!")
            except ValueError as e:
                st.error(str(e))

# ==================== VIEW DATA ====================
elif selected == "View Data":

    st.header("📄 Family Members")

    if not expense_tracker.members:
        st.info("No members added yet.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.write("**Name**")
        col2.write("**Status**")
        col3.write("**Earnings**")
        col4.write("**Action**")

        for m in expense_tracker.members:
            col1.write(m.name)
            col2.write("Earning" if m.earning_status else "Not Earning")
            col3.write(m.earnings)

            if col4.button(f"Delete {m.name}"):
                expense_tracker.delete_family_member(m)
                st.rerun()

    st.header("💸 Expenses")

    if not expense_tracker.expense_list:
        st.info("No expenses added yet.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.write("**Amount**")
        col2.write("**Category**")
        col3.write("**Description**")
        col4.write("**Date**")
        col5.write("**Delete**")

        for e in expense_tracker.expense_list:
            col1.write(e.value)
            col2.write(e.category)
            col3.write(e.description)
            col4.write(e.date)

            if col5.button(f"Delete {e.category}"):
                expense_tracker.delete_expense(e)
                st.rerun()

    total_earnings = expense_tracker.calculate_total_earnings()
    total_expense = expense_tracker.calculate_total_expenditure()
    balance = total_earnings - total_expense

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Earnings", f"{total_earnings}")
    c2.metric("💸 Total Expense", f"{total_expense}")
    c3.metric("📊 Balance", f"{balance}")

# ==================== ANALYTICS ====================
elif selected == "Analytics":

    st.header("📊 Expense Insights Dashboard")

    data = []

    for exp in expense_tracker.expense_list:
        data.append({
            "Amount": exp.value,
            "Category": exp.category,
            "Date": exp.date
        })

    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No data available. Add some expenses first.")
    else:
        # Table
        st.subheader("📄 Data")
        st.dataframe(df)

        # Pie Chart
        st.subheader("💸 Category-wise Spending")
        category_data = df.groupby("Category")["Amount"].sum()

        fig, ax = plt.subplots()
        ax.pie(category_data, labels=category_data.index, autopct="%1.1f%%")
        st.pyplot(fig)

        # Monthly Trend
        df["Date"] = pd.to_datetime(df["Date"])
        monthly = df.groupby(df["Date"].dt.month)["Amount"].sum()

        st.subheader("📅 Monthly Trend")
        st.line_chart(monthly)

        # Total
        total = df["Amount"].sum()
        st.metric("💰 Total Spending", f"₹ {total}")

        # Download CSV
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Report",
            data=csv,
            file_name="expense_report.csv",
            mime="text/csv"
        )