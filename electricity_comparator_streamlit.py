import streamlit as st
import pandas as pd

st.set_page_config(page_title="Electricity Quote Comparator", layout="wide")
st.title("⚡ Electricity Quote Comparator")

st.markdown("""
Enter your average **weekly usage in kWh**, and fill in provider details.
We'll compare them side-by-side based on weekly, monthly, and annual cost (after discounts).
""")

# --- Step 1: User inputs average weekly usage
weekly_usage = st.number_input("🔌 Average Weekly Usage (kWh)", min_value=0.0, value=100.0, step=1.0)

# --- Step 2: Dynamic provider input
st.subheader("🏢 Provider Information")

if "providers" not in st.session_state:
    st.session_state.providers = []

with st.form("add_provider_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Provider Name")
        rate = st.number_input("Rate per unit (kWh)", min_value=0.0, value=0.30)
    with col2:
        standing_charge = st.number_input("Daily Standing Charge", min_value=0.0, value=0.50)
        contract_months = st.number_input("Contract Length (months)", min_value=1, value=12)
    with col3:
        discount = st.number_input("Manual Discount (£)", min_value=0.0, value=0.0)

    submitted = st.form_submit_button("Add Provider")
    if submitted and name:
        st.session_state.providers.append({
            'Provider': name,
            'Rate': rate,
            'Standing Charge': standing_charge,
            'Contract (months)': contract_months,
            'Discount': discount
        })

# --- Step 3: Show provider table
if st.session_state.providers:
    st.markdown("### 📋 Providers Added")
    st.dataframe(pd.DataFrame(st.session_state.providers))

    # --- Step 4: Perform Calculations
    def calculate_costs(providers, weekly_usage):
        results = []
        for p in providers:
            weekly_units = p['Rate'] * weekly_usage
            weekly_standing = p['Standing Charge'] * 7
            weekly_total = weekly_units + weekly_standing

            annual_total = weekly_total * 52
            annual_after_discount = annual_total - p['Discount']
            monthly_after_discount = annual_after_discount / 12
            weekly_after_discount = annual_after_discount / 52

            results.append({
                "Provider": p['Provider'],
                "Weekly (£)": round(weekly_after_discount, 2),
                "Monthly (£)": round(monthly_after_discount, 2),
                "Annual (£)": round(annual_after_discount, 2)
            })
        return sorted(results, key=lambda x: x["Annual (£)"])

    results = calculate_costs(st.session_state.providers, weekly_usage)

    st.markdown("### 📊 Comparison Table (Sorted by Annual Cost)")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

    # Optional: Highlight best deal
    best = df_results.iloc[0]
    st.success(f"💡 Best Deal: **{best['Provider']}** at £{best['Annual (£)']:.2f}/year")

else:
    st.info("Add at least one provider to see comparison.")

# --- Reset button
if st.button("🔁 Reset Providers"):
    st.session_state.providers = []
