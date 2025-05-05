import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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

    # Risk Level Indicator
    if volatility_score > 0.4 or skew_score > 2.0:
        risk_level = "High Risk"
        max_chaos_pct = 0.20
    elif volatility_score > 0.2 or skew_score > 1.0:
        risk_level = "Moderate Risk"
        max_chaos_pct = 0.10
    else:
        risk_level = "Low Risk"
        max_chaos_pct = 0.05

    # Premium % based on Volatility Score (DOUBLED)
    if volatility_score <= 0.1:
        vol_pct = 0.02
    elif volatility_score <= 0.2:
        vol_pct = 0.04
    elif volatility_score <= 0.3:
        vol_pct = 0.06
    elif volatility_score <= 0.4:
        vol_pct = 0.08
    else:
        vol_pct = 0.12

    # Premium % based on Skew Score (DOUBLED)
    if skew_score <= 0.5:
        skew_pct = 0.00
    elif skew_score <= 1.0:
        skew_pct = 0.04
    elif skew_score <= 1.5:
        skew_pct = 0.06
    elif skew_score <= 2.0:
        skew_pct = 0.08
    else:
        skew_pct = 0.12

    # Limit combined premium to max_chaos_pct of DAT average
    upper_spread = dat_high - dat_avg
    base_markup = base_markup_pct * r_buy
    raw_vol_premium = vol_pct * upper_spread
    raw_skew_premium = skew_pct * upper_spread
    raw_chaos_premium = raw_vol_premium + raw_skew_premium
    capped_chaos_premium = min(raw_chaos_premium, max_chaos_pct * dat_avg)

    # Split capped chaos proportionally
    if raw_chaos_premium > 0:
        vol_premium = capped_chaos_premium * (raw_vol_premium / raw_chaos_premium)
        skew_premium = capped_chaos_premium * (raw_skew_premium / raw_chaos_premium)
    else:
        vol_premium = 0
        skew_premium = 0

    chaos_premium = vol_premium + skew_premium
    sell_price = r_buy + base_markup + chaos_premium
    total_markup_pct = ((sell_price - r_buy) / r_buy) * 100
    chaos_pct_of_avg = (chaos_premium / r_buy) * 100
    chaos_pct_of_spread = (chaos_premium / upper_spread) * 100 if upper_spread > 0 else 0

    # Output
    st.subheader("Results")
    st.markdown(f"**Sell Price:** ${sell_price:,.2f}")
    st.markdown(f"**Total Markup %:** {total_markup_pct:.2f}%")
    st.markdown(f"**Risk Level:** {risk_level}")
    st.markdown("---")
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
    st.write(f"Chaos Premium as % of Upper Spread: {chaos_pct_of_spread:.2f}%")
    st.write(f"Chaos Premium as % of Lane Avg: {chaos_pct_of_avg:.2f}%")
    
    # Visual Lane Condition Chart
    st.subheader("Lane Condition Overview")
    fig, ax = plt.subplots()
    ax.bar(['Low', 'Avg', 'High'], [dat_low, dat_avg, dat_high], color=['#6c9cde', '#8bc34a', '#e57373'])
    ax.set_ylabel('Rate ($)')
    ax.set_title('DAT Lane Rate Distribution')
    st.pyplot(fig)
