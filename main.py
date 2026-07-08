import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# Set modern, wide-layout application configurations
st.set_page_config(
    page_title="Golden Beach Resort RMS",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------------------------------------------------------
# SIDEBAR CONTROL DECK
# -----------------------------------------------------------------------------
st.sidebar.markdown("# 🏨 Control Deck")
st.sidebar.markdown("---")

selected_room = st.sidebar.selectbox(
    "Select Target Asset Category",
    options=['Standard', 'Deluxe', 'Suite', 'Family', 'Superior']
)

st.sidebar.markdown("### Live Capacity Configuration")
allocated_capacity = st.sidebar.slider(
    "Physical Operational Capacity",
    min_value=10, max_value=250, value=100, step=5
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Adjust variables to trigger automated EMSR-b pricing limit variations in real time.")

# -----------------------------------------------------------------------------
# DATA INGESTION SECURITY LAYER
# -----------------------------------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("Daily_Fare_Class_Demand_2022_2025.csv")

df =load_data()

df["Arrival_Date"] = pd.to_datetime(df["Arrival_Date"])

# -----------------------------------------------------------------------------
# CORE APP WORKSPACE NAVIGATION LAYOUT
# -----------------------------------------------------------------------------
st.title("Golden Beach Resort — Revenue Management System")
tab_analytics, tab_forecast, tab_emsr, tab_health = st.tabs([
    "📈 Historical Demand Analytics",
    "🔮 Predictive Demand Forecasting",
    "🎯 Live EMSR Optimization Solver",
    "🔬 Model Validation & Performance"
])

# -----------------------------------------------------------------------------
# TAB 1: HISTORICAL DEMAND ANALYTICS
# -----------------------------------------------------------------------------




with tab_analytics:


    st.header(f"Retrospective Operational Analytics — {selected_room} Rooms")

    # ----------------------------------------------------------------
    # Add filter
    # ----------------------------------------------------------------

    df["Arrival_Date"] = pd.to_datetime(df["Arrival_Date"])

    col1, col2 = st.columns(2)

    with col1:
        fare_class = st.multiselect(
            "Fare Class",
            options=sorted(df["Fare_Class"].unique()),
            default=["Y2_Medium"]
        )

    with col2:
        start_date, end_date = st.date_input(
            "Select Date Range",
            value=(
                df["Arrival_Date"].min().date(),
                df["Arrival_Date"].max().date()
            )
        )


    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)


    df_filtering = df[
        (df["Fare_Class"].isin(fare_class)) &
        (df["Arrival_Date"].between(start_date, end_date))
        ]

    # # ---------------------------------------------------------------
    # # ---------------------------------------------------------------

    room_hist = df_filtering[df_filtering['Room_Category'] == selected_room]

    if not room_hist.empty:
        # Calculate structural high-level KPI blocks
        total_showups = room_hist['Actual_Showups'].sum()
        total_unconstrained = int(room_hist['Total_Unconstrained_Demand'].sum())
        revenue_leakage_spill = total_unconstrained - total_showups
        Average_Daily_showups = int(room_hist["Actual_Showups"].mean())
        Average_Daily_Demand = int(df_filtering["Total_Unconstrained_Demand"].mean())
        Average_cancellation = int(df_filtering["Simulated_Cancellations"].mean())

        kpi_1, kpi_2, kpi_3 = st.columns(3)
        kpi_1.metric("Observed Actual Bookings", f"{total_showups:,} Nights")
        kpi_2.metric("True Market Latent Demand", f"{total_unconstrained:,} Nights")
        kpi_3.metric("Capacity Spill Drain (Lost Opportunity)", f"{revenue_leakage_spill:,} Nights", delta="-Deficit",
                     delta_color="inverse")

        st.markdown("---")
        kpi_1, kpi_2, kpi_3 = st.columns(3)
        kpi_1.metric("Average Actual Bookings", f"{Average_Daily_showups:,} Nights")
        kpi_2.metric("Average True Market Demand", f"{Average_Daily_Demand:,} Nights")
        kpi_3.metric("Average Capacity Spill Drain", f"{Average_cancellation:,} Nights")

        st.markdown("---")
        st.subheader("Temporal Distribution: Constrained vs. Unconstrained Demand")

        # Compress tracking parameters to monthly frequency for visualization scannability
        room_hist['Arrival_Date'] = pd.to_datetime(room_hist['Arrival_Date'])

        monthly_hist = (
            room_hist
            .set_index('Arrival_Date')
            .resample('ME')[['Actual_Showups', 'Total_Unconstrained_Demand']]
            .sum()
            .reset_index()
        )

        fig_hist = go.Figure()
        fig_hist.add_trace(
            go.Scatter(x=monthly_hist['Arrival_Date'], y=monthly_hist['Actual_Showups'], name="Observed Capacity Limit",
                       line=dict(color='#2ecc71', width=2)))
        fig_hist.add_trace(go.Scatter(x=monthly_hist['Arrival_Date'], y=monthly_hist['Total_Unconstrained_Demand'],
                                      name="Unconstrained Market Demand",
                                      line=dict(color='#e74c3c', width=2, dash='dot'), fill='tonexty',
                                      fillcolor='rgba(231, 76, 60, 0.1)'))

        fig_hist.update_layout(template="plotly_white", xaxis_title="Timeline Axis", yaxis_title="Room Nights Volume",
                               legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("No historical operational data points located for this asset specification.")


# -----------------------------------------------------------------------------
# TAB 2: PREDICTIVE DEMAND FORECASTING
# -----------------------------------------------------------------------------


# ------------------- Load Data ----------------------------

@st.cache_data
def load_data():
    return pd.read_csv("forecast_30day_mu_sigma.csv")
df_demand =load_data()

df_demand["Arrival_Date"] = pd.to_datetime(df_demand["Arrival_Date"])
#--------------------------------------------------------------

with tab_forecast:
    st.header("📊 Demand Forcasting")
    st.markdown("---")
    df_demand["Arrival_Date"] = pd.to_datetime(df_demand["Arrival_Date"])

    col1, col2 = st.columns(2)

    with col1:
        fare_class2 = st.selectbox(
            "Fare Class",
            (df_demand["Fare_Class"].unique()),
            key="room_type_1"
        )

    with col2:
        arr_date = st.date_input(
            "Enter Date",
            value=date(2025, 9, 25)
        )
    arr_date= pd.to_datetime(arr_date)
    df_filtering2 = df_demand[
        (df_demand["Fare_Class"]==fare_class2) &
        (df_demand["Arrival_Date"] == arr_date)
        ]

    room_hist2 = df_filtering2[df_filtering2['Room_Category'] == selected_room]

    if not room_hist2.empty:
        Demand = float(room_hist2["forecast_mu"].max())
       # kpi_1 = st.columns(1)[0]
        st.metric(
            "Demand Average Forecasting",
            f"{Demand:,.2f} Nights"
        )

    st.markdown("---")

# -----------------------------------------------------------------------------
# TAB 3: LIVE EMSR OPTIMIZATION CONTROL SOLVER
# -----------------------------------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("emsr_protection_levels.csv")
df_demand =load_data()

@st.cache_data
def load_data():
    return pd.read_csv("Overbooking_limits.csv")
overbooking =load_data()

df_demand["Arrival_Date"] = pd.to_datetime(df_demand["Arrival_Date"])


with tab_emsr:
    st.header("📊 Overbooking and Protection Levels")
    st.markdown("---")
    df_demand["Arrival_Date"] = pd.to_datetime(df_demand["Arrival_Date"])

    col1, col2 = st.columns(2)

    with col1:
        fare_class2 = st.selectbox(
            "Fare Class",
            (df_demand["Fare_Class"].unique()),
            key="room_type_3"
        )

    with col2:
        selected_date = st.date_input(
            "Select Date",
            value = date(2025, 10, 25)
        )
    selected_date = pd.to_datetime(selected_date)
    df_filtering3 = df_demand[
        (df_demand["Fare_Class"]==fare_class2) &
        (df_demand["Arrival_Date"] == selected_date)
        ]

    room_hist = df_filtering3[df_filtering3['Room_Category'] == selected_room]

    if not room_hist.empty:
        protection_level = int(room_hist["protection_level"].min())
        booking_limit = int(room_hist["booking_limit"].min())
        kpi_1,kpi_2 = st.columns(2)
        kpi_1.metric(
            "Protection Level",
            f"{protection_level:} Rooms"
        )
        kpi_2.metric(
            "Booking Limit",
            f"{booking_limit:} Rooms"
        )

    st.markdown("---")

    st.header("Overbooking")
    risk_level = st.selectbox(
        "Fare Class",
        (overbooking["Risk_Level"].unique())
    )

    overbooking = overbooking[(overbooking["Risk_Level"] == risk_level)]
    if not overbooking.empty:
        save_overbooking = int(overbooking["Safe_Overbooking_Limit_Binomial"].min())
        expected_showups = int(overbooking["Expected_ShowUps"].min())
        kpi_1, kpi_2 = st.columns(2)
        kpi_1.metric(
            "Save Overbooking",
            f"{save_overbooking:} Rooms"
        )
        kpi_2.metric(
            "Expected ShowUps",
            f"{expected_showups:} Nights"
        )

        st.write("Note:")
        st.write("- Hotel's room capacity is 437")
        st.write("- Cancellation rate = 15%")

    st.markdown("---")






# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# TAB 4: MODEL PERFORMANCE & HEALTH VERIFICATION
# -----------------------------------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_csv("accuracy_metrics.csv")

filtered_df = load_data()


with tab_health:
    st.header("📊 Predictive Model Precision & Validation Logs")
    st.markdown("---")

    fare_class = st.selectbox(
        "Fare Class",
        (filtered_df["Fare_Class"].unique()),
        key="room_type_2"

    )


    room_metrics = filtered_df[(filtered_df['Room_Category'] == selected_room) & (filtered_df['Fare_Class'] == fare_class)]


    if not room_metrics.empty:
        MAPE = room_metrics['MAPE_%'].max()
        sMAPE = room_metrics['sMAPE_%'].max()
        RMSE = room_metrics['RMSE'].max()
        MAE = room_metrics['MAE'].max()
        st.subheader("Statistical Error Auditing Matrix")
        kpi_1, kpi_2, kpi_3,kpi_4 = st.columns(4)
        kpi_1.metric("MAPE", f"{MAPE:,} ")
        kpi_2.metric("sMAPE", f"{sMAPE:,} ")
        kpi_3.metric("RMSE", f"{RMSE:,} ")
        kpi_4.metric("MAE", f"{MAE:,} ")
        st.dataframe(room_metrics, use_container_width=True, hide_index=True)




        st.markdown("### Structural Metrics Interpretation Guides")
        st.markdown("""
        * **MAPE (Mean Absolute Percentage Error):** Evaluates variation variance. Lower values denote higher forecast reliability. Operational benchmarks below **12%** are optimal for peak holiday environments.
        * **RMSE (Root Mean Squared Error):** Quantifies variance penalty deviations. Highlights and targets extreme statistical demand estimation deviations.
        """)

    btn = st.button("Show Entire Statistical Error Auditing")
    if btn:
        st.dataframe(filtered_df)





