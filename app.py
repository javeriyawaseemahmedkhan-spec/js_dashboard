
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide"
)


# ==========================================
# 2. PROFESSIONAL CSS
# ==========================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at 10% 5%, #292052 0%, transparent 35%),
        radial-gradient(ellipse at 90% 20%, #102F52 0%, transparent 35%),
        #080D1B;
    color: #F8FAFC;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11182B, #0D1425);
    border-right: 1px solid #273451;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2 {
    color: white;
}

[data-testid="stSidebar"] label {
    color: #CBD5E1 !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #2C375B, #19233E);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(167, 139, 250, 0.3);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

div[data-testid="stMetricLabel"] {
    color: #C4B5FD;
}

div[data-testid="stMetricValue"] {
    color: white;
    font-weight: 800;
}

div[data-testid="stPlotlyChart"] {
    background: rgba(24, 34, 58, 0.55);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 10px;
}

h1, h2, h3 {
    color: #FFFFFF;
}

hr {
    border-color: rgba(148, 163, 184, 0.2);
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    data = pd.read_csv("ecommerce_customers.csv")

    return data


try:

    df = load_data()

except FileNotFoundError:

    st.error(
        "CSV file not found. Please keep "
        "ecommerce_customers.csv in the same folder as app.py."
    )

    st.stop()


# ==========================================
# 4. DATA PREPARATION
# ==========================================

numeric_cols = [
    "Avg. Session Length",
    "Time on App",
    "Time on Website",
    "Length of Membership",
    "Yearly Amount Spent"
]

required_cols = numeric_cols + ["Email"]

missing_cols = [
    col for col in required_cols
    if col not in df.columns
]

if missing_cols:

    st.error(f"Missing columns: {missing_cols}")

    st.stop()


for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


df = df.dropna(
    subset=numeric_cols
).copy()


if df.empty:

    st.error("No valid customer records found.")

    st.stop()


# ==========================================
# 5. DASHBOARD HEADER
# ==========================================

st.markdown(
    "<span style='color:#C4B5FD; font-weight:700; "
    "letter-spacing:3px;'>BUSINESS INTELLIGENCE</span>",
    unsafe_allow_html=True
)

st.title("🛍️ E-Commerce Analytics")

st.markdown(
    "Explore customer behavior, engagement and yearly "
    "purchase patterns through interactive analytics."
)

st.divider()


# ==========================================
# 6. SIDEBAR FILTERS
# ==========================================

st.sidebar.title("🎛️ Dashboard Filters")

st.sidebar.caption(
    "Customize your customer analysis."
)

st.sidebar.divider()


membership_min = float(
    df["Length of Membership"].min()
)

membership_max = float(
    df["Length of Membership"].max()
)

spending_min = float(
    df["Yearly Amount Spent"].min()
)

spending_max = float(
    df["Yearly Amount Spent"].max()
)


membership_range = st.sidebar.slider(
    "Membership Length",
    min_value=membership_min,
    max_value=membership_max,
    value=(membership_min, membership_max)
) if membership_min < membership_max else (
    membership_min, membership_max
)


spending_range = st.sidebar.slider(
    "Yearly Amount Spent",
    min_value=spending_min,
    max_value=spending_max,
    value=(spending_min, spending_max)
) if spending_min < spending_max else (
    spending_min, spending_max
)


# ==========================================
# 7. FILTER DATA
# ==========================================

filtered_df = df[
    (df["Length of Membership"] >= membership_range[0]) &
    (df["Length of Membership"] <= membership_range[1]) &
    (df["Yearly Amount Spent"] >= spending_range[0]) &
    (df["Yearly Amount Spent"] <= spending_range[1])
].copy()


if filtered_df.empty:

    st.warning("No customers found. Adjust your filters.")

    st.stop()


# ==========================================
# 8. BUSINESS OVERVIEW
# ==========================================

st.subheader("📊 Business Overview")

total_customers = filtered_df["Email"].nunique()

average_spending = filtered_df[
    "Yearly Amount Spent"
].mean()

average_membership = filtered_df[
    "Length of Membership"
].mean()

highest_spending = filtered_df[
    "Yearly Amount Spent"
].max()


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "👥 Total Customers",
    f"{total_customers:,}"
)

c2.metric(
    "💰 Average Spending",
    f"${average_spending:,.2f}"
)

c3.metric(
    "⏳ Avg. Membership",
    f"{average_membership:.2f} Years"
)

c4.metric(
    "🏆 Highest Spending",
    f"${highest_spending:,.2f}"
)


st.divider()


# ==========================================
# 9. CHART DESIGN FUNCTION
# ==========================================

def style_chart(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter",
            color="#E2E8F0"
        ),
        title_font=dict(
            size=19,
            color="white"
        ),
        margin=dict(
            l=35,
            r=35,
            t=65,
            b=35
        )
    )

    return fig


# ==========================================
# 10. UNIVARIATE ANALYSIS
# ==========================================

st.subheader("📈 Customer Spending Distribution")

fig1 = px.histogram(
    filtered_df,
    x="Yearly Amount Spent",
    nbins=25,
    title="Distribution of Yearly Customer Spending",
    color_discrete_sequence=["#A78BFA"]
)

fig1.update_layout(
    xaxis_title="Yearly Amount Spent ($)",
    yaxis_title="Number of Customers",
    bargap=0.15
)

st.plotly_chart(
    style_chart(fig1),
    use_container_width=True
)


# ==========================================
# 11. APP AND WEBSITE ANALYSIS
# ==========================================

st.subheader("🔍 Customer Engagement Analysis")

col1, col2 = st.columns(2)


with col1:

    fig2 = px.scatter(
        filtered_df,
        x="Time on App",
        y="Yearly Amount Spent",
        color="Length of Membership",
        title="Time on App vs Yearly Spending",
        color_continuous_scale="Purples"
    )

    fig2.update_layout(
        xaxis_title="Time on App",
        yaxis_title="Yearly Amount Spent ($)"
    )

    st.plotly_chart(
        style_chart(fig2),
        use_container_width=True
    )


with col2:

    fig3 = px.scatter(
        filtered_df,
        x="Time on Website",
        y="Yearly Amount Spent",
        color="Length of Membership",
        title="Time on Website vs Yearly Spending",
        color_continuous_scale="Blues"
    )

    fig3.update_layout(
        xaxis_title="Time on Website",
        yaxis_title="Yearly Amount Spent ($)"
    )

    st.plotly_chart(
        style_chart(fig3),
        use_container_width=True
    )


# ==========================================
# 12. MEMBERSHIP ANALYSIS
# ==========================================

st.subheader("⭐ Membership Analysis")

fig4 = px.scatter(
    filtered_df,
    x="Length of Membership",
    y="Yearly Amount Spent",
    color="Yearly Amount Spent",
    title="Membership Length vs Yearly Spending",
    color_continuous_scale="Viridis"
)

fig4.update_layout(
    xaxis_title="Length of Membership (Years)",
    yaxis_title="Yearly Amount Spent ($)"
)

st.plotly_chart(
    style_chart(fig4),
    use_container_width=True
)


# ==========================================
# 13. SESSION ANALYSIS
# ==========================================

st.subheader("⏱️ Session Analysis")

fig5 = px.histogram(
    filtered_df,
    x="Avg. Session Length",
    nbins=25,
    title="Average Customer Session Length",
    color_discrete_sequence=["#06B6D4"]
)

fig5.update_layout(
    xaxis_title="Average Session Length",
    yaxis_title="Number of Customers"
)

st.plotly_chart(
    style_chart(fig5),
    use_container_width=True
)


# ==========================================
# 14. CORRELATION HEATMAP
# ==========================================

st.subheader("🔥 Correlation Analysis")

corr = filtered_df[numeric_cols].corr()

fig6 = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Customer Behavior Correlation Heatmap"
)

st.plotly_chart(
    style_chart(fig6),
    use_container_width=True
)


# ==========================================
# 15. APP VS WEBSITE COMPARISON
# ==========================================

st.subheader("📱 App vs Website Performance")


if len(filtered_df) >= 2:

    app_corr = filtered_df[
        "Time on App"
    ].corr(
        filtered_df["Yearly Amount Spent"]
    )

    website_corr = filtered_df[
        "Time on Website"
    ].corr(
        filtered_df["Yearly Amount Spent"]
    )

    comparison = pd.DataFrame({
        "Platform": ["Mobile App", "Website"],
        "Correlation with Spending": [
            app_corr,
            website_corr
        ]
    })

    fig7 = px.bar(
        comparison,
        x="Platform",
        y="Correlation with Spending",
        color="Platform",
        text_auto=".3f",
        title="Platform Engagement vs Yearly Spending",
        color_discrete_sequence=[
            "#A78BFA",
            "#06B6D4"
        ]
    )

    fig7.update_layout(
        yaxis_title="Correlation with Spending"
    )

    st.plotly_chart(
        style_chart(fig7),
        use_container_width=True
    )

else:

    st.info("Select at least two customers for comparison.")


# ==========================================
# 16. BUSINESS INSIGHTS
# ==========================================

st.subheader("💡 Key Business Insights")


strongest_corr = (
    corr["Yearly Amount Spent"]
    .drop("Yearly Amount Spent")
    .abs()
    .idxmax()
)


if len(filtered_df) >= 2 and pd.notna(app_corr) and pd.notna(website_corr):

    if abs(app_corr) > abs(website_corr):

        stronger = "Mobile App"

    elif abs(website_corr) > abs(app_corr):

        stronger = "Website"

    else:

        stronger = "Both platforms have equal correlation"

    st.info(
        f"""
        **1. Total Customers:** {total_customers:,}

        **2. Average Spending:** ${average_spending:,.2f}

        **3. Platform Comparison:** {stronger} has the stronger
        correlation with yearly spending.

        **4. Strongest Relationship:** {strongest_corr}
        has the strongest absolute correlation with yearly spending.
        """
    )

else:

    st.info(
        "More customer records are needed to calculate platform insights."
    )


# ==========================================
# 17. RAW DATA TABLE
# ==========================================

st.subheader("📋 Customer Data")

show_data = st.checkbox("Show Raw Data Table")


if show_data:

    display_cols = [
        col for col in filtered_df.columns
        if col not in ["Email", "Address"]
    ]

    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True
    )


# ==========================================
# 18. FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:20px; color:#A5B4CC;">

    <h3 style="color:#C4B5FD;">
    E-Commerce Analytics Dashboard
    </h3>

    Customer Behavior & Purchase Pattern Analysis

    <br><br>

    Built with Python | Streamlit | Pandas | Plotly

    </div>
    """,
    unsafe_allow_html=True
)
