# Streamlit MTS Pricing Calculator v3 (Split Volatility & Skew with Sliders)

import streamlit as st

def scale_to_range(value, input_min, input_max, output_min, output_max):
    if value < input_min:
        return output_min
    elif value > input_max:
        return output_max
    else:
        ratio = (value - input_min) / (input_max - input_min)
        return output_min + ratio * (output_max - output_min)

def main():
    st.title("Market Tightness Pricing Calculator v3")

    st.header("Inputs")
    dat_high = st.number_input("DAT High ($)", min_value=0.0, value=4260.0)
    dat_avg = st.number_input("DAT Average ($)", min_value=0.0, value=3311.0)
    dat_low = st.number_input("DAT Low ($)", min_value=0.0, value=2787.0)
    base_markup_pct = st.number_input("Base Markup (%)", min_value=0.0, value=7.0)
    r_buy = st.number_input("Carrier Buy Rate ($)", min_value=0.0, value=3311.0)

    st.header("Tuning Controls")
    vol_min_pct = st.slider("Min Volatility Premium %", 0.0, 20.0, 5.0)
    vol_max_pct = st.slider("Max Volatility Premium %", 10.0, 40.0, 20.0)
    skew_min_pct = st.slider("Min Skew Premium %", 0.0, 10.0, 0.0)
    skew_max_pct = st.slider("Max Skew Premium %", 5.0, 30.0, 10.0)

    # Scoring Ranges
    vol_input_min, vol_input_max = 0.10, 0.60
    skew_input_min, skew_input_max = 0.7, 2.5

    if st.button("Calculate Pricing"):
        # Step 1: Core Metrics
        upper_spread = dat_high - dat_avg
        volatility = (dat_high - dat_low) / dat_avg if dat_avg else 0
        skew = (dat_high - dat_avg) / (dat_avg - dat_low) if (dat_avg - dat_low) != 0 else 0

        # Step 2: Map to %
        vol_pct = scale_to_range(volatility, vol_input_min, vol_input_max, vol_min_pct / 100, vol_max_pct / 100)
        skew_pct = scale_to_range(skew, skew_input_min, skew_input_max, skew_min_pct / 100, skew_max_pct / 100)

        # Step 3: Dollar Markups
        vol_markup = vol_pct * upper_spread
        skew_markup = skew_pct * upper_spread
        base_markup = base_markup_pct / 100 * r_buy

        final_price = r_buy + base_markup + vol_markup + skew_markup
        total_markup = final_price - r_buy
        total_markup_pct = (total_markup / r_buy) * 100 if r_buy else 0

        st.header("Results")
        st.write(f"**Volatility Ratio:** {volatility:.3f}")
        st.write(f"**Skew Ratio:** {skew:.3f}")
        st.write(f"**Upper Spread ($):** {upper_spread:.2f}")
        st.write(f"**Volatility Premium %:** {vol_pct * 100:.2f}% → ${vol_markup:.2f}")
        st.write(f"**Skew Premium %:** {skew_pct * 100:.2f}% → ${skew_markup:.2f}")
        st.write(f"**Base Markup ($):** ${base_markup:.2f}")
        st.success(f"**Final Sell Price: ${final_price:.2f}**")
        st.info(f"**Total Markup: ${total_markup:.2f} ({total_markup_pct:.2f}%)**")

if __name__ == "__main__":
    main()
