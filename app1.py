import os
import requests
import streamlit as st
import pandas as pd
import drawchat  # Assuming drawchat is a module in your project

# Initialize default file paths
DEFAULT_MDI_PATH = 'data/MDI_final.csv'
DEFAULT_MDI_BP_PATH = 'data/MDI_BP_23_26.csv'
DEFAULT_TDI_PATH = 'data/TDI_final.csv'
DEFAULT_TDI_BP_PATH = 'data/TDI_BP_23_27.csv'

# Load default data
def load_default_data():
    df_mdi = pd.read_csv(DEFAULT_MDI_PATH)
    df_mdi_BP = pd.read_csv(DEFAULT_MDI_BP_PATH)
    df_tdi = pd.read_csv(DEFAULT_TDI_PATH)
    df_tdi_BP = pd.read_csv(DEFAULT_TDI_BP_PATH)
    return df_mdi, df_mdi_BP, df_tdi, df_tdi_BP

# Select MDI suppliers
mdi_suppliers = ['covestro', 'tosoh', 'wanhua', 'kmc', 'basf', 'sabic', 'huntsman']

# Select TDI suppliers
tdi_suppliers = ['covestro', 'mcns', 'wanhua', 'basf', 'hanwha', 'sabic', 'other']

covestro_supplier = ['covestro']

def Visual_customer_demand(type_material, df_mdi, df_tdi):
    if type_material == 'MDI':
        # Select MDI customer
        mdi_customer_name = st.selectbox("Select Customer MDI", df_mdi['customer'].unique())
        if st.button("Plot MDI Demand"):
            try:
                df = df_mdi[df_mdi['customer'] == mdi_customer_name]
                max_demand = df['demand'].max()
                chart_figure = drawchat.plot_customer_demand1(
                    df=df_mdi,
                    customer_name=mdi_customer_name,
                    customer_column='customer',
                    suppliers=mdi_suppliers,
                    demand_ylim=(0, max_demand*1.4),
                    title_fontsize=20, axis_label_fontsize=16,
                    tick_fontsize=16, legend_fontsize=12,
                    legend_title_fontsize=18, value_label_fontsize=14,
                    demand_label_fontsize=18
                )
                st.pyplot(chart_figure)
            except ValueError as e:
                st.error(str(e))
    else:
        # Select TDI customer
        tdi_customer_name = st.selectbox("Select Customer TDI", df_tdi['customer'].unique())
        if st.button("Plot TDI Demand"):
            try:
                df = df_tdi[df_tdi['customer'] == tdi_customer_name]
                max_demand = df['demand'].max()
                chart_figure = drawchat.plot_customer_demand1(
                    df=df_tdi,
                    customer_name=tdi_customer_name,
                    customer_column='customer',
                    suppliers=tdi_suppliers,
                    demand_ylim=(0, max_demand*1.4),
                    title_fontsize=20, axis_label_fontsize=16,
                    tick_fontsize=16, legend_fontsize=12,
                    legend_title_fontsize=18, value_label_fontsize=14,
                    demand_label_fontsize=18
                )
                st.pyplot(chart_figure)
            except ValueError as e:
                st.error(str(e))

def Visual_account_price_volume(type_material, df_mdi, df_tdi):
    if type_material == 'MDI':
        mdi_customer_name = st.selectbox("Select Customer MDI", df_mdi['customer'].unique())
        if st.button("Plot MDI Demand"):
            try:
                df = df_mdi[df_mdi['customer'] == mdi_customer_name]
                max_demand = df['demand'].max()
                max_price = df['pocket price'].max()
                chart_figure = drawchat.plot_customer_demand_with_price(
                    df_mdi, mdi_customer_name, 'customer',
                    covestro_supplier,
                    demand_ylim=(0, max_demand*2),
                    price_ylim=(0.5, max_price*1.5),
                    price_columns=['pocket price', 'seap_pp', 'apac_pp'],
                    price_colors=['red', 'green', 'blue'],
                    title_fontsize=22, axis_label_fontsize=20,
                    tick_fontsize=18, legend_fontsize=16,
                    legend_title_fontsize=16, value_label_fontsize=18,
                    price_annotation_fontsize=16,
                    annotation_spacing=25
                )
                st.pyplot(chart_figure)
            except ValueError as e:
                st.error(str(e))
    else:
        tdi_customer_name = st.selectbox("Select Customer TDI", df_tdi['customer'].unique())
        if st.button("Plot TDI Demand"):
            try:
                df = df_tdi[df_tdi['customer'] == tdi_customer_name]
                max_demand = df['demand'].max()
                max_price = df['pocket price'].max()
                chart_figure = drawchat.plot_customer_demand_with_price(
                    df_tdi, tdi_customer_name, 'customer',
                    covestro_supplier,
                    demand_ylim=(0, max_demand*2),
                    price_ylim=(0.5, max_price*1.5),
                    price_columns=['pocket price', 'apac_pp'],
                    price_colors=['red', 'green'],
                    title_fontsize=22, axis_label_fontsize=20,
                    tick_fontsize=18, legend_fontsize=16,
                    legend_title_fontsize=16, value_label_fontsize=18,
                    price_annotation_fontsize=16,
                    annotation_spacing=25
                )
                st.pyplot(chart_figure)
            except ValueError as e:
                st.error(str(e))

def Visual_business_plan(type_material, df_mdi_BP, df_tdi_BP):
    if type_material == 'MDI':
        mdi_customer_name = st.selectbox("Select Customer MDI", df_mdi_BP['customer'].unique())
        if st.button("Plot MDI Demand"):
            try:
                chart_figure = drawchat.plot_customer_business_plan(
                    df_mdi_BP, mdi_customer_name, show_percentages=False,
                    title_fontsize=22, axis_label_fontsize=20,
                    tick_fontsize=20, legend_fontsize=18,
                    value_label_fontsize=16
                )
                st.pyplot(chart_figure)
            except ValueError as e:
                st.error(str(e))
    else:
        tdi_customer_name = st.selectbox("Select Customer TDI", df_tdi_BP['customer'].unique())
        if st.button("Plot TDI Demand"):
            try:
                chart_figure = drawchat.plot_customer_business_plan(
                    df_tdi_BP, tdi_customer_name, show_percentages=False,
                    title_fontsize=22, axis_label_fontsize=20,
                    tick_fontsize=20, legend_fontsize=18,
                    value_label_fontsize=16
                )
                st.pyplot(chart_figure)
            except ValueError as e:
                st.error(str(e))

if __name__ == "__main__":
    st.set_page_config(page_title="MDI and TDI Visualization")
    st.sidebar.title("Navigation")
    type_chart = st.sidebar.radio("Select type of chart", ["Customer Demand", "Account price vs Volume", "Business plan"], index=0)
    type_material = st.sidebar.selectbox("Select Customer MDI or TDI", ["TDI", "MDI"], index=0)

    # Sidebar for data source selection
    data_source = st.sidebar.radio("Select Data Source", ["Default Files", "Upload New Files"], index=0)

    # Initialize dataframes
    df_mdi, df_mdi_BP, df_tdi, df_tdi_BP = load_default_data()

    if data_source == "Upload New Files":
        st.sidebar.subheader("Upload MDI Files")
        mdi_file = st.sidebar.file_uploader("Upload MDI Customer Data (CSV)", key="mdi_file")
        mdi_bp_file = st.sidebar.file_uploader("Upload MDI Business Plan (CSV)", key="mdi_bp_file")
        
        st.sidebar.subheader("Upload TDI Files")
        tdi_file = st.sidebar.file_uploader("Upload TDI Customer Data (CSV)", key="tdi_file")
        tdi_bp_file = st.sidebar.file_uploader("Upload TDI Business Plan (CSV)", key="tdi_bp_file")

        # Load uploaded files if provided
        if mdi_file is not None:
            try:
                df_mdi = pd.read_csv(mdi_file)
                st.sidebar.success("MDI Customer Data uploaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error uploading MDI Customer Data: {e}")
        
        if mdi_bp_file is not None:
            try:
                df_mdi_BP = pd.read_csv(mdi_bp_file)
                st.sidebar.success("MDI Business Plan uploaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error uploading MDI Business Plan: {e}")
        
        if tdi_file is not None:
            try:
                df_tdi = pd.read_csv(tdi_file)
                st.sidebar.success("TDI Customer Data uploaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error uploading TDI Customer Data: {e}")
        
        if tdi_bp_file is not None:
            try:
                df_tdi_BP = pd.read_csv(tdi_bp_file)
                st.sidebar.success("TDI Business Plan uploaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error uploading TDI Business Plan: {e}")

    st.title(f"The chart for {type_chart}")

    # Call visualization functions with loaded data
    if type_chart == 'Customer Demand':
        Visual_customer_demand(type_material, df_mdi, df_tdi)
    elif type_chart == 'Account price vs Volume':
        Visual_account_price_volume(type_material, df_mdi, df_tdi)
    else:
        Visual_business_plan(type_material, df_mdi_BP, df_tdi_BP)