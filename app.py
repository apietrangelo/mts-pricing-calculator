import streamlit as st

def calculate_mts_price(high, avg, low, base_markup_pct):
    r_buy = avg
    base_markup_dollars = base_markup_pct * r_buy

    # Volatility and Skew
    volatility = (high - low) / avg
    skew = (high - avg) / (avg - low) if (avg - low) != 0 else 0
    
    # MTS Calculation
    mts = 0.6 * volatility + 0.4 * skew

    # Volatility Percent
    vol_pct = min(0.005 * (mts ** 1.25), 0.5)

    # Upside Range
    upside_range = high - avg
    
    # Volatility Impact in $
    volatility_dollars = vol_pct * upside_range

    # Final Sell Rate
    r_sell = r_buy + base_markup_dollars + volatility_dollars

    return {
        "R_buy": r_buy,
        "Volatility": volatility,
        "Skew": skew,
        "MTS": mts,
        "Volatility %": vol_pct,
        "Base Markup $": base_markup_dollars,
        "Volatility $ Impact": volatility_dollars,
        "Sell Price": r_sell
    }

# Streamlit UI
st.title("MTS-Based Freight Pricing Calculator")

high = st.number_input("DAT High ($)", min_value=0.0, value=3000.0)
avg = st.number_input("DAT Average ($)", min_value=0.0, value=2500.0)
low = st.number_input("DAT Low ($)", min_value=0.0, value=2000.0)
base_pct_input = st.number_input("Base Markup %", min_value=0.0, max_value=1.0, value=0.07)

if st.button("Calculate Sell Price"):
    result = calculate_mts_price(high, avg, low, base_pct_input)
    
    st.subheader("Results")
    for key, value in result.items():
        st.write(f"{key}: ${value:,.2f}" if "Price" in key or "$" in key else f"{key}: {value:.3f}")
