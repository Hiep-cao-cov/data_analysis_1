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

def Visual_customer_demand():
    st.title("Customer Demand Visualization") 
    
    # Select MDI customer
    mdi_customer_name = st.selectbox("Select Customer MDI", df_mdi['customer'].unique())
   
    
    if st.button("Plot MDI Demand"):
        try:
            chart_figure,max_demand_volume = drawchat.plot_customer_demand(
                df=df_mdi,
                customer_name=mdi_customer_name,
                customer_column='customer',
                suppliers=mdi_suppliers
            )
            st.pyplot(chart_figure)         
        except ValueError as e:
            st.error(str(e))
    # Select TDI customer        
    tdi_customer_name = st.selectbox("Select Customer TDI", df_tdi['customer'].unique())
    
    if st.button("Plot TDI Demand"):
        try:
            chart_figure,max_demand_volume = drawchat.plot_customer_demand(
                df=df_tdi,
                customer_name=tdi_customer_name,
                customer_column='customer',
                suppliers=tdi_suppliers
            )
            st.pyplot(chart_figure)    
        except ValueError as e:
            st.error(str(e))
            
def Visual_account_price_volume():
    # Select MDI customer
    st.title("Business Plan Visualization")
    mdi_customer_name = st.selectbox("Select Customer MDI", df_mdi['customer'].unique())  
    
    if st.button("Plot MDI Demand"):
        try:
            chart_figure,max_demand,max_price = drawchat.plot_customer_demand_with_price(
                df_mdi,mdi_customer_name,'customer',
                                covestro_supplier,
                                #demand_ylim=(0,800),
                                #price_ylim=(0.5,3),
                                price_columns=['pocket price','seap_pp','apac_pp'],
                                price_colors=['red', 'green','blue'],
                                title_fontsize=22, axis_label_fontsize=20, 
                                tick_fontsize=18, legend_fontsize=16, 
                                legend_title_fontsize=16, value_label_fontsize=18,
                                price_annotation_fontsize=16,
                                annotation_spacing=25
                                )         
            st.pyplot(chart_figure)
            st.write(f"Maximum demand volume: {max_demand}")         
            st.write(f"Maximum price: {max_price}")
        except ValueError as e:
            st.error(str(e))
    # Select TDI customer        
    tdi_customer_name = st.selectbox("Select Customer TDI", df_tdi['customer'].unique())
    
    if st.button("Plot TDI Demand"):
        try:
            chart_figure,max_demand,max_price = drawchat.plot_customer_demand_with_price(
                df_tdi,tdi_customer_name,'customer',
                                covestro_supplier,
                                #demand_ylim=(0, 3800),
                                #price_ylim=(0,3),
                                price_columns=['pocket price','apac_pp'],
                                price_colors=['red', 'green'],
                                title_fontsize=22, axis_label_fontsize=20, 
                                tick_fontsize=18, legend_fontsize=16, 
                                legend_title_fontsize=16, value_label_fontsize=18,
                                price_annotation_fontsize=16,
                                annotation_spacing=25
                                )
            st.pyplot(chart_figure)
            st.write(f"Maximum demand volume: {max_demand}")         
            st.write(f"Maximum price: {max_price}")    
        except ValueError as e:
            st.error(str(e))
def Visual_business_plan():
    st.title("Business Plan Visualization")
    st.write("This feature is under development. Please check back later.")
        
if __name__ == "__main__":
    st.title('Creating Radio Buttons')
    type_chart = ('Customer Demand', 'Account price vs Volume', 'Business plan')
    type_chart = st.radio('Select Chart Type', type_chart, index=0)
    if type_chart == 'Customer Demand':
        Visual_customer_demand()
    elif type_chart == 'Account price vs Volume':
        Visual_account_price_volume()
    else:
        Visual_business_plan()
    
    
    
