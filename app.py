import streamlit as st

st.title("MTS-Based Freight Pricing Calculator")

# User Inputs
dat_high = st.number_input("DAT High ($)", value=1859.00)
dat_avg = st.number_input("DAT Average ($)", value=1640.00)
dat_low = st.number_input("DAT Low ($)", value=1480.00)
base_markup_pct = st.number_input("Base Markup %", value=0.07)

if st.button("Calculate Sell Price"):
    r_buy = dat_avg  # Use DAT Average as Carrier Buy Rate

    # Volatility and Skew
    volatility = (dat_high - dat_low) / dat_avg
    skew = (dat_high - dat_avg) / (dat_avg - dat_low) if (dat_avg - dat_low) != 0 else 0

    # Score Scaling (0–1 range for both)
    volatility_score = volatility
    skew_score = skew

    # Premium % based on Volatility Score
    if volatility_score <= 0.1:
        vol_pct = 0.01
    elif volatility_score <= 0.2:
        vol_pct = 0.02
    elif volatility_score <= 0.3:
        vol_pct = 0.03
    elif volatility_score <= 0.4:
        vol_pct = 0.04
    else:
        vol_pct = 0.05

    # Premium % based on Skew Score
    if skew_score <= 0.5:
        skew_pct = 0.00
    elif skew_score <= 1.0:
        skew_pct = 0.01
    elif skew_score <= 1.5:
        skew_pct = 0.02
    elif skew_score <= 2.0:
        skew_pct = 0.03
    else:
        skew_pct = 0.04

    # Markup Calculations
    upper_spread = dat_high - dat_avg
    base_markup = base_markup_pct * r_buy
    vol_premium = vol_pct * upper_spread
    skew_premium = skew_pct * upper_spread
    chaos_premium = vol_premium + skew_premium

    sell_price = r_buy + base_markup + chaos_premium
    total_markup_pct = ((sell_price - r_buy) / r_buy) * 100

    # Output
    st.subheader("Results")
    st.write(f"Sell Price: ${sell_price:,.2f}")
    st.write(f"R_buy (DAT Avg): ${r_buy:,.2f}")
    st.write(f"Volatility: {volatility:.3f}")
    st.write(f"Skew: {skew:.3f}")
    st.write(f"Volatility % Applied: {vol_pct:.2%}")
    st.write(f"Skew % Applied: {skew_pct:.2%}")
    st.write(f"Upper Spread: ${upper_spread:,.2f}")
    st.write(f"Base Markup: ${base_markup:,.2f}")
    st.write(f"Volatility Premium: ${vol_premium:,.2f}")
    st.write(f"Skew Premium: ${skew_premium:,.2f}")
    st.write(f"Chaos Premium: ${chaos_premium:,.2f}")
    st.write(f"Total Markup %: {total_markup_pct:.2f}%")
