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

    # MTS Score
    mts = 0.6 * volatility + 0.4 * skew

    # Volatility % Scaling Logic
    if mts * 100 <= 75:
        volatility_pct = 0.001
    elif mts * 100 <= 150:
        volatility_pct = 0.002
    elif mts * 100 <= 225:
        volatility_pct = 0.003
    elif mts * 100 <= 300:
        volatility_pct = 0.004
    else:
        volatility_pct = 0.005

    upper_spread = dat_high - dat_avg
    base_markup = base_markup_pct * r_buy
    volatility_impact = volatility_pct * upper_spread
    sell_price = r_buy + base_markup + volatility_impact
    total_markup_pct = ((sell_price - r_buy) / r_buy) * 100

    # Output
    st.subheader("Results")
    st.write(f"R_buy: {r_buy:,.3f}")
    st.write(f"Volatility: {volatility:.3f}")
    st.write(f"Skew: {skew:.3f}")
    st.write(f"MTS: {mts:.3f}")
    st.write(f"Volatility %: {volatility_pct:.3f}")
    st.write(f"Base Markup :{base_markup:,.2f}")
    st.write(f"Volatility *Impact* :{volatility_impact:,.2f}")
    st.write(f"**Sell Price: ${sell_price:,.2f}**")
    st.write(f"Total Markup %: {total_markup_pct:.2f}%")
