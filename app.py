import os
import pandas as pd
import streamlit as st
import drawchat  # Assuming drawchat is a module in your project
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Optional
from uuid import uuid4

@dataclass
class Config:
    """Configuration class for file paths and constants"""
    DEFAULT_PATHS: Dict[str, str] = field(default_factory=lambda: {
        'mdi': 'data/MDI_final.csv',
        'mdi_bp': 'data/MDI_BP_23_26.csv',
        'tdi': 'data/VN_TDI_final.csv',
        'tdi_bp': 'data/VN_TDI_BP_23_27.csv',
        'tw_tdi_bp': 'data/TW_TDI_BP_23_27.csv',
        'tw_tdi': 'data/TW_TDI_final.csv'
    })
    
    SUPPLIERS: Dict[str, List[str]] = field(default_factory=lambda: {
        'mdi': ['covestro', 'tosoh', 'wanhua', 'kmc', 'basf', 'sabic', 'huntsman'],
        'tdi': ['covestro', 'mcns', 'wanhua', 'basf', 'hanwha', 'sabic', 'other'],
        'covestro': ['covestro']
    })
    
    CHART_TYPES: List[str] = field(default_factory=lambda: ["Customer Demand", "Account price vs Volume", "Business plan"])
    COUNTRIES: List[str] = field(default_factory=lambda: ["Vietnam", "Taiwan"])
    MATERIALS: List[str] = field(default_factory=lambda: ["TDI", "MDI"])

class DataLoader:
    """Handles data loading and file uploads"""
    
    @staticmethod
    def load_csv(file_path: str, uploaded_file=None) -> pd.DataFrame:
        """Load CSV from file path or uploaded file"""
        try:
            if uploaded_file:
                return pd.read_csv(uploaded_file)
            return pd.read_csv(file_path)
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return pd.DataFrame()

    @classmethod
    def load_country_data(cls, country: str, config: Config) -> Tuple[pd.DataFrame, ...]:
        """Load data based on country"""
        if country == "Vietnam":
            return (
                cls.load_csv(config.DEFAULT_PATHS['mdi']),
                cls.load_csv(config.DEFAULT_PATHS['mdi_bp']),
                cls.load_csv(config.DEFAULT_PATHS['tdi']),
                cls.load_csv(config.DEFAULT_PATHS['tdi_bp'])
            )
        return (
            cls.load_csv(config.DEFAULT_PATHS['tw_tdi_bp']),
            cls.load_csv(config.DEFAULT_PATHS['tw_tdi'])
        )

class Visualizer:
    """Handles visualization logic"""
    
    @staticmethod
    def get_chart_config(chart_type: str) -> Dict:
        """Return configuration for different chart types"""
        base_config = {
            'title_fontsize': 20,
            'axis_label_fontsize': 16,
            'tick_fontsize': 16,
            'legend_fontsize': 12,
            'value_label_fontsize': 14
        }
        
        if chart_type == "Account price vs Volume":
            base_config.update({
                'title_fontsize': 22,
                'axis_label_fontsize': 20,
                'tick_fontsize': 18,
                'legend_fontsize': 16,
                'legend_title_fontsize': 16,
                'price_annotation_fontsize': 16,
                'annotation_spacing': 25
            })
        elif chart_type == "Business plan":
            base_config.update({
                'title_fontsize': 22,
                'axis_label_fontsize': 20,
                'tick_fontsize': 20,
                'legend_fontsize': 18,
                'value_label_fontsize': 16
            })
        else:  # Customer Demand
            base_config.update({
                'legend_title_fontsize': 18
            })
        return base_config

    @classmethod
    def plot_chart(cls, chart_type: str, df: pd.DataFrame, customer_name: str, 
                  material: str, config: Config, is_taiwan: bool = False) -> None:
        """Plot chart based on type and material"""
        try:
            if df.empty or 'customer' not in df.columns:
                st.error("DataFrame is empty or missing 'customer' column")
                return

            chart_config = cls.get_chart_config(chart_type)
            df_filtered = df[df['customer'] == customer_name]
            
            if chart_type == "Customer Demand":
                if 'demand' not in df.columns:
                    st.error("Required 'demand' column not found in DataFrame")
                    return
                suppliers = config.SUPPLIERS['tdi' if material == 'TDI' else 'mdi']
                max_demand = df_filtered['demand'].max() if not df_filtered.empty else 0
                chart_figure = drawchat.plot_customer_demand1(
                    df=df,
                    customer_name=customer_name,
                    customer_column='customer',
                    suppliers=suppliers,
                    demand_ylim=(0, max_demand * 1.4),
                    **chart_config
                )
            elif chart_type == "Account price vs Volume":
                if 'demand' not in df.columns or 'pocket price' not in df.columns:
                    st.error("Required 'demand' or 'pocket price' column not found in DataFrame")
                    return
                max_demand = df_filtered['demand'].max() if not df_filtered.empty else 0
                max_price = df_filtered['pocket price'].max() if not df_filtered.empty else 0
                price_columns = ['pocket price', 'apac_pp'] if material == 'TDI' else ['pocket price', 'seap_pp', 'apac_pp']
                price_colors = ['red', 'green'] if material == 'TDI' else ['red', 'green', 'blue']
                chart_figure = drawchat.plot_customer_demand_with_price(
                    df, customer_name, 'customer',
                    config.SUPPLIERS['covestro'],
                    demand_ylim=(0, max_demand * 2),
                    price_ylim=(0.5, max_price * 1.5),
                    price_columns=price_columns,
                    price_colors=price_colors,
                    **chart_config
                )
            else:  # Business plan
                chart_figure = drawchat.plot_customer_business_plan(
                    df, customer_name, show_percentages=False,
                    **chart_config
                )
            st.pyplot(chart_figure)
        except ValueError as e:
            st.error(f"Error generating plot: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

def setup_page():
    """Setup Streamlit page configuration"""
    st.set_page_config(page_title="MDI and TDI Visualization", layout="wide")
    st.sidebar.title("Navigation")

def main():
    """Main application logic"""
    config = Config()
    setup_page()
    
    # Sidebar controls
    type_country = st.sidebar.selectbox("Select Country", config.COUNTRIES)
    type_chart = st.sidebar.radio("Select type of chart", config.CHART_TYPES)
    is_vietnam = type_country == "Vietnam"
    
    if is_vietnam:
        type_material = st.sidebar.selectbox("Select Material", config.MATERIALS)
    else:
        type_material = "TDI"  # Taiwan only supports TDI
        
    data_source = st.sidebar.radio("Select Data Source", ["Default Files", "Upload New Files"]) if is_vietnam else "Default Files"
    
    # Load data
    if is_vietnam:
        df_mdi, df_mdi_bp, df_tdi, df_tdi_bp = DataLoader.load_country_data("Vietnam", config)
        
        if data_source == "Upload New Files":
            st.sidebar.subheader("Upload Files")
            for key, label in [('mdi', 'MDI Customer Data'), ('mdi_bp', 'MDI Business Plan'),
                             ('tdi', 'TDI Customer Data'), ('tdi_bp', 'TDI Business Plan')]:
                uploaded_file = st.sidebar.file_uploader(f"Upload {label} (CSV)", key=f"{key}_file")
                if uploaded_file:
                    locals()[f"df_{key}"] = DataLoader.load_csv("", uploaded_file)
    else:
        df_tdi_bp, df_tdi = DataLoader.load_country_data("Taiwan", config)
    
    # Set page title
    st.title(f"{type_chart} Visualization")
    
    # Select appropriate dataframe based on chart type and material
    df = (df_tdi if type_material == 'TDI' else df_mdi) if type_chart != "Business plan" else \
         (df_tdi_bp if type_material == 'TDI' else df_mdi_bp)
    
    # Render visualization
    if not df.empty:
        customer_name = st.selectbox(f"Select Customer {type_material}", df['customer'].unique())
        if st.button(f"Plot {type_chart} for {customer_name}"):
            Visualizer.plot_chart(type_chart, df, customer_name, type_material, config, not is_vietnam)
    else:
        st.error("No data available to display. Please check your data files.")

if __name__ == "__main__":
    main()