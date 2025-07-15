import os
from dotenv import load_dotenv
import requests
import streamlit as st
import pandas as pd
import drawchat # Assuming drawchat is a module in your project

# main.py
load_dotenv()  # Load environment variables from .env file
sec_key = os.getenv("MY_SECRET_KEY")

# Load data
df_mdi = pd.read_csv('data/MDI_final.csv')
df_tdi = pd.read_csv('data/TDI_final.csv')

# Select MDI suppliers
mdi_suppliers = ['covestro','tosoh', 'wanhua','kmc', 'basf', 'sabic','huntsman']

# Select TDI suppliers
tdi_suppliers = ['covestro','mcns', 'wanhua', 'basf', 'hanwha', 'sabic','other']

covestro_supplier =['covestro'] 

def Visual_customer_demand(type_material='TDI'):
    
    if type_material == 'MDI':
    # Select MDI customer
        mdi_customer_name = st.selectbox("Select Customer MDI", df_mdi['customer'].unique())
        if st.button("Plot MDI Demand"):
            try:
                df = df_mdi[df_mdi['customer'] == mdi_customer_name]
                max_demand = df['demand'].max()          
                chart_figure= drawchat.plot_customer_demand(
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
                chart_figure = drawchat.plot_customer_demand(
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
            
def Visual_account_price_volume(type_material='TDI'):
    
    # Select MDI customer
    
    if type_material == 'MDI':
        mdi_customer_name = st.selectbox("Select Customer MDI", df_mdi['customer'].unique())
        if st.button("Plot MDI Demand"):
            try:
                df = df_mdi[df_mdi['customer'] == mdi_customer_name]
                max_demand = df['demand'].max()
                max_price = df['pocket price'].max()     
                chart_figure = drawchat.plot_customer_demand_with_price( 
                    df_mdi,mdi_customer_name,'customer',
                                    covestro_supplier,
                                    demand_ylim=(0,max_demand*2),
                                    price_ylim=(0.5,max_price*1.5),
                                    price_columns=['pocket price','seap_pp','apac_pp'],
                                    price_colors=['red', 'green','blue'],
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
                    df_tdi,tdi_customer_name,'customer',
                                    covestro_supplier,
                                    demand_ylim=(0,max_demand*2),
                                    price_ylim=(0.5,max_price*1.5),
                                    price_columns=['pocket price','apac_pp'],
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
def Visual_business_plan():
    st.write("This feature is under development. Please check back later.")
        
if __name__ == "__main__":
    st.set_page_config(page_title="MDI and TDI Visualization")
    st.sidebar.title("Navigation")
    type_chart = st.sidebar.radio("Select type of chart", ["Customer Demand", "Account price vs Volume", "Business plan"], index=0)
    
    type_material = st.sidebar.selectbox("Select Customer MDI or TDI", ["TDI", "MDI"], index=0) 
    data_file = st.file_uploader('Upload your file data here :')
    st.title(f"The chart for {type_chart}")
    
    
    if data_file is not None:
        try:
            df_mdi = pd.read_csv(data_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error uploading file: {e}")
            
    if type_chart == 'Customer Demand':
        Visual_customer_demand(type_material)
    elif type_chart == 'Account price vs Volume':
        Visual_account_price_volume(type_material)
    else:
        Visual_business_plan()
  
    
    
