import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Advanced MTS-Based Freight Pricing Calculator")

# Section: DAT Inputs (Required)
st.header("DAT Market Data (Required)")
dat_high = st.number_input("DAT High ($)", value=1859.00)
dat_avg = st.number_input("DAT Average ($)", value=1640.00)
dat_low = st.number_input("DAT Low ($)", value=1480.00)
origin_mci = st.number_input("Origin Outbound MCI", value=50)
destination_mci = st.number_input("Destination Outbound MCI", value=50)

# Section: Greenscreens Inputs (Optional)
st.header("Greenscreens Market Data (Optional)")
gs_avg = st.number_input("Greenscreens Average ($)", value=0.0)
gs_confidence = st.number_input("Greenscreens Confidence Score", value=0)

# Section: Markup Inputs
st.header("Markup Settings")
base_markup_pct = st.number_input("Base Markup %", value=0.07)

if st.button("Calculate Sell Price"):
    # Determine Base Rate
    if gs_avg > 0 and gs_confidence >= 89:
        base_rate = 0.5 * dat_avg + 0.5 * gs_avg
        blend_label = "50/50 DAT:GS"
    elif gs_avg > 0 and gs_confidence >= 76:
        base_rate = 0.65 * dat_avg + 0.35 * gs_avg
        blend_label = "65/35 DAT:GS"
    else:
        base_rate = dat_avg
        blend_label = "100% DAT (Fallback)"

    # Discrepancy warning
    if gs_avg > 0:
        discrepancy_pct = abs(dat_avg - gs_avg) / dat_avg * 100
        if discrepancy_pct > 20:
            st.warning("🚨 GS and DAT differ by more than 20%. Recommend close inspection — default to DAT.")
        elif discrepancy_pct > 10:
            st.warning("⚠️ GS and DAT differ by more than 10%.")

    # MCI Adjustments on Base Rate
    origin_mci_adj = 0
    if origin_mci >= 90:
        origin_mci_adj = 0.02
    elif origin_mci >= 75:
        origin_mci_adj = 0.015
    elif origin_mci >= 50:
        origin_mci_adj = 0.01
    elif origin_mci <= -75:
        origin_mci_adj = 0.01

    dest_mci_adj = 0
    if destination_mci >= 75:
        dest_mci_adj = -0.02
    elif destination_mci >= 50:
        dest_mci_adj = -0.01
    elif destination_mci <= -75:
        dest_mci_adj = 0.015

    # Adjusted base rate after MCI
    mci_adjustment_pct = origin_mci_adj + dest_mci_adj
    adjusted_base_rate = base_rate * (1 + mci_adjustment_pct)

    # Base Markup
    base_markup = adjusted_base_rate * base_markup_pct

    # Volatility and Skew
    volatility = (dat_high - dat_low) / dat_avg
    skew = (dat_high - dat_avg) / (dat_avg - dat_low) if (dat_avg - dat_low) != 0 else 0
    upper_spread = dat_high - dat_avg

    # Risk Level and Cap
    if volatility > 0.4 or skew > 2.0:
        risk_level = "High Risk"
        max_chaos_pct = 0.20
    elif volatility > 0.2 or skew > 1.0:
        risk_level = "Moderate Risk"
        max_chaos_pct = 0.10
    else:
        risk_level = "Low Risk"
        max_chaos_pct = 0.05

    # Volatility % Table
    if volatility <= 0.1:
        vol_pct = 0.02
    elif volatility <= 0.2:
        vol_pct = 0.04
    elif volatility <= 0.3:
        vol_pct = 0.06
    elif volatility <= 0.4:
        vol_pct = 0.08
    else:
        vol_pct = 0.12

    # Skew % Table
    if skew <= 0.5:
        skew_pct = 0.00
    elif skew <= 1.0:
        skew_pct = 0.04
    elif skew <= 1.5:
        skew_pct = 0.06
    elif skew <= 2.0:
        skew_pct = 0.08
    else:
        skew_pct = 0.12

    # Raw Chaos Premiums
    raw_vol_premium = vol_pct * upper_spread
    raw_skew_premium = skew_pct * upper_spread
    raw_chaos_premium = raw_vol_premium + raw_skew_premium
    capped_chaos_premium = min(raw_chaos_premium, max_chaos_pct * adjusted_base_rate)

    if raw_chaos_premium > 0:
        vol_premium = capped_chaos_premium * (raw_vol_premium / raw_chaos_premium)
        skew_premium = capped_chaos_premium * (raw_skew_premium / raw_chaos_premium)
    else:
        vol_premium = 0
        skew_premium = 0

    chaos_premium = vol_premium + skew_premium

    # Final Sell Price
    sell_price = adjusted_base_rate + base_markup + chaos_premium
    total_markup_pct = ((sell_price - base_rate) / base_rate) * 100

    # Output
    st.subheader("Results")
    st.markdown(f"**Final Sell Price:** ${sell_price:,.2f}")
    st.markdown(f"**Total Markup % over Raw Base Rate:** {total_markup_pct:.2f}%")
    st.markdown(f"**Base Rate Source:** {blend_label}")
    st.markdown(f"**Risk Level:** {risk_level}")
    st.markdown("---")
    st.write(f"Base Rate Before MCI Adj: ${base_rate:,.2f}")
    st.write(f"MCI Adjustment %: {mci_adjustment_pct * 100:.2f}%")
    st.write(f"Adjusted Base Rate: ${adjusted_base_rate:,.2f}")
    st.write(f"Base Markup: ${base_markup:,.2f}")
    st.write(f"Volatility: {volatility:.3f}")
    st.write(f"Skew: {skew:.3f}")
    st.write(f"Volatility Premium: ${vol_premium:,.2f}")
    st.write(f"Skew Premium: ${skew_premium:,.2f}")
    st.write(f"Chaos Premium (Capped): ${chaos_premium:,.2f}")

    # Pie Chart
    st.subheader("Markup Composition")
    labels = [
        f'Base Markup (${base_markup:,.2f})',
        f'Volatility Premium (${vol_premium:,.2f})',
        f'Skew Premium (${skew_premium:,.2f})',
        f'MCI Adjustment (${adjusted_base_rate - base_rate:,.2f})'
    ]
    sizes = [base_markup, vol_premium, skew_premium, adjusted_base_rate - base_rate]
    fig2, ax2 = plt.subplots()
    ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)
