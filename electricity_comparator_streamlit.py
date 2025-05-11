import streamlit as st
import pandas as pd

st.set_page_config(page_title="Σύγκριση Παρόχων Ρεύματος", layout="wide")
st.title("⚡ Σύγκριση Προσφορών Παρόχων Ηλεκτρικού Ρεύματος")

st.markdown("""
Εισάγετε την **κατανάλωση ρεύματος**, επιλέγοντας αν είναι εβδομαδιαία, μηνιαία ή ετήσια.
Στη συνέχεια, προσθέστε τους παρόχους για να δείτε ποιος προσφέρει την καλύτερη τιμή.
""")

# === Κατανάλωση & Επιλογή Μονάδας ===
col_input = st.columns(2)
with col_input[0]:
    usage_unit = st.selectbox("Μονάδα Κατανάλωσης", ["Εβδομαδιαία (kWh)", "Μηνιαία (kWh)", "Ετήσια (kWh)"])
with col_input[1]:
    raw_usage = st.number_input("Κατανάλωση Ρεύματος", min_value=0.0, value=100.0, step=1.0)

# --- Μετατροπή σε εβδομαδιαία βάση
if "Εβδομαδιαία" in usage_unit:
    weekly_usage = raw_usage
elif "Μηνιαία" in usage_unit:
    weekly_usage = raw_usage / 4.345  # average weeks/month
else:  # Ετήσια
    weekly_usage = raw_usage / 52

# --- Πληροφορίες Παρόχου
st.subheader("🏢 Στοιχεία Παρόχου")

if "providers" not in st.session_state:
    st.session_state.providers = []

with st.form("add_provider_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Όνομα Παρόχου")
        rate = st.number_input("Χρέωση ανά kWh (€)", min_value=0.0, value=0.30)
    with col2:
        standing_charge = st.number_input("Πάγιο (Μηνιαίο, €)", min_value=0.0, value=15.0)
        contract_months = st.number_input("Διάρκεια Συμβολαίου (μήνες)", min_value=1, value=12)
    with col3:
        discount = st.number_input("Έκπτωση/Προσφορά (€)", min_value=0.0, value=0.0)

    submitted = st.form_submit_button("Προσθήκη Παρόχου")
    if submitted and name:
        st.session_state.providers.append({
            'Πάροχος': name,
            'Χρέωση': rate,
            'Πάγιο': standing_charge,
            'Μήνες': contract_months,
            'Έκπτωση': discount
        })

# --- Πίνακας Παρόχων
if st.session_state.providers:
    st.markdown("### 📋 Προστιθέμενοι Πάροχοι")
    st.dataframe(pd.DataFrame(st.session_state.providers))

    def calculate_costs(providers, weekly_usage):
        results = []
        for p in providers:
            weekly_units = p['Χρέωση'] * weekly_usage
            weekly_standing = p['Πάγιο'] / 4.345  # Μηνιαίο -> Εβδομαδιαίο
            weekly_total = weekly_units + weekly_standing

            annual_total = weekly_total * 52
            annual_after_discount = annual_total - p['Έκπτωση']
            monthly_after_discount = annual_after_discount / 12
            weekly_after_discount = annual_after_discount / 52

            results.append({
                "Πάροχος": p['Πάροχος'],
                "Εβδομαδιαίο (€)": round(weekly_after_discount, 2),
                "Μηνιαίο (€)": round(monthly_after_discount, 2),
                "Ετήσιο (€)": round(annual_after_discount, 2)
            })
        return sorted(results, key=lambda x: x["Ετήσιο (€)"])

    results = calculate_costs(st.session_state.providers, weekly_usage)

    st.markdown("### 📊 Πίνακας Σύγκρισης (Κατά Ετήσιο Κόστος)")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

    best = df_results.iloc[0]
    st.success(f"💡 Καλύτερη Επιλογή: **{best['Πάροχος']}** με κόστος €{best['Ετήσιο (€)']:.2f} / έτος")

else:
    st.info("Προσθέστε τουλάχιστον έναν πάροχο για να δείτε συγκριτικά στοιχεία.")

# --- Κουμπί Επαναφοράς
if st.button("🔁 Εκκαθάριση Παρόχων"):
    st.session_state.providers = []
