# Streamlit MTS Pricing Calculator v2 (with Skew Dampening)

import streamlit as st

def calculate_mts(volatility, skew, skew_dampening):
    mts_raw = 0.6 * volatility + 0.4 * skew
    if skew_dampening:
        skew_modifier = skew if skew < 1 else 1
        mts_raw *= skew_modifier
    mts_score = mts_raw * 100
    return mts_score

def get_mts_premium(mts_score, method="table"):
    if method == "formula":
        # Revised chaos premium logic with softer scaling
        chaos_pct = min(0.0003 * (mts_score ** 1.4), 0.35)
    else:
        # Table method: fixed zones
        if mts_score <= 30:
            chaos_pct = 0.05
        elif mts_score <= 60:
            chaos_pct = 0.15
        elif mts_score <= 80:
            chaos_pct = 0.30
        else:
            chaos_pct = 0.50
    return chaos_pct

def main():
    st.title("Market Tightness Score (MTS) Pricing Calculator")

    st.header("Inputs")
    dat_high = st.number_input("DAT High ($)", min_value=0.0, value=1100.0)
    dat_avg = st.number_input("DAT Average ($)", min_value=0.0, value=1000.0)
    dat_low = st.number_input("DAT Low ($)", min_value=0.0, value=900.0)
    base_markup_pct = st.number_input("Base Markup (%)", min_value=0.0, value=7.0)
    r_buy = st.number_input("Carrier Buy Rate ($)", min_value=0.0, value=1000.0)

    method = st.radio("Choose MTS Adjustment Method", ("table", "formula"))
    skew_dampening = st.checkbox("Apply Skew Dampening (reduce MTS when avg is near high)", value=True)

    if st.button("Calculate Pricing"):
        # Step 1: Calculate volatility and skew
        volatility = (dat_high - dat_low) / dat_avg
        skew = (dat_high - dat_avg) / (dat_avg - dat_low) if (dat_avg - dat_low) != 0 else 0

        # Step 2: Calculate MTS Score (with optional dampening)
        mts_score = calculate_mts(volatility, skew, skew_dampening)

        # Step 3: Get chaos premium based on method
        chaos_premium_pct = get_mts_premium(mts_score, method)

        # Step 4: Calculate Sell Price
        base_markup_amount = base_markup_pct / 100 * r_buy
        upside_range = dat_high - dat_avg
        chaos_markup_amount = chaos_premium_pct * upside_range
        raw_price = r_buy + base_markup_amount + chaos_markup_amount
        final_price = min(raw_price, dat_high)  # Hard cap at DAT High

        st.header("Results")
        st.write(f"**Volatility Ratio:** {volatility:.3f}")
        st.write(f"**Skew Ratio:** {skew:.3f}")
        st.write(f"**MTS Score:** {mts_score:.1f}")
        st.write(f"**Chaos Premium (% of Upside Spread):** {chaos_premium_pct * 100:.1f}%")
        st.write(f"**Base Markup ($):** {base_markup_amount:.2f}")
        st.write(f"**Chaos Markup ($):** {chaos_markup_amount:.2f}")
        st.success(f"**Final Sell Price (capped at DAT High): ${final_price:.2f}**")

if __name__ == "__main__":
    main()
