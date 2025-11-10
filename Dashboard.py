import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_excel("Data.xlsx", sheet_name="data")

# Filter step relevan
relevant_steps = ["01. Leads from DM", "02. Uploaded by Telesales", "04. Connected", "06. Presented", "07. Agree"]
df_filtered = df[df["Step"].isin(relevant_steps)]

# Agregasi
agg_df = df_filtered.groupby(["Periode", "Product", "Campaign", "Step"], as_index=False)["Total"].sum()

# Pivot
pivot_df = agg_df.pivot_table(index=["Periode", "Product", "Campaign"], columns="Step", values="Total", fill_value=0).reset_index()
pivot_df.columns.name = None
pivot_df = pivot_df.rename(columns={
    "01. Leads from DM": "Lead from DM",
    "02. Uploaded by Telesales": "Uploaded",
    "04. Connected": "Connected",
    "06. Presented": "Presented",
    "07. Agree": "Agree"
})

# Hitung metrik
pivot_df["Contacted %"] = (pivot_df["Connected"] / pivot_df["Uploaded"]) * 100
pivot_df["Agree %"] = (pivot_df["Agree"] / pivot_df["Uploaded"]) * 100
pivot_df["Presented %"] = (pivot_df["Presented"] / pivot_df["Agree"]) * 100
pivot_df["Periode"] = pd.to_datetime(pivot_df["Periode"])

# Sidebar filter
st.sidebar.header("Filter")
products = list(pivot_df["Product"].unique())
selected_products = st.sidebar.multiselect("Product", ["All"] + products, default=["All"])

# Filter campaign sesuai product
if "All" in selected_products:
    campaigns = list(pivot_df["Campaign"].unique())
else:
    campaigns = list(pivot_df[pivot_df["Product"].isin(selected_products)]["Campaign"].unique())

selected_campaigns = st.sidebar.multiselect("Campaign", ["All"] + campaigns, default=["All"])
selected_period = st.sidebar.date_input("Periode", [pivot_df["Periode"].min(), pivot_df["Periode"].max()])

# Filter data
filtered_df = pivot_df[
    (pivot_df["Periode"] >= pd.to_datetime(selected_period[0])) &
    (pivot_df["Periode"] <= pd.to_datetime(selected_period[1]))
]

if "All" not in selected_products:
    filtered_df = filtered_df[filtered_df["Product"].isin(selected_products)]

if "All" not in selected_campaigns:
    filtered_df = filtered_df[filtered_df["Campaign"].isin(selected_campaigns)]

# Fungsi grafik panjang
def plot_line_chart(df, column, title, color):
    fig = px.line(df, x="Periode", y=column, title=title, markers=True,
                  labels={"Periode": "Periode", column: column}, color_discrete_sequence=[color])
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Tampilkan grafik
plot_line_chart(filtered_df, "Lead from DM", "Lead from DM", "red")
plot_line_chart(filtered_df, "Contacted %", "Contacted / Uploaded (%)", "blue")
plot_line_chart(filtered_df, "Agree %", "Agree / Uploaded (%)", "green")

plot_line_chart(filtered_df, "Presented %", "Agree / Presented (%)", "lightblue")
