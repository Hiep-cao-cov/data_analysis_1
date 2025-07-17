import pandas as pd
from typing import Dict, List, Optional

def get_default_customer_mapping() -> Dict[str, str]:
    """Default customer name mapping for standardization."""
    return {
        'HEADWAY ADVANCED MATERIALS INC': 'HEADWAY',
        'Headway Advanced Materials Inc.': 'HEADWAY',
        'KUN CHING KEY-INDUSTRY CO LTD': 'KUN CHING',
        'KUN CHING INDUSTRIAL CO., LTD.': 'KUN CHING',
        'CHEN CHI HSIANG INDUSTRY': 'CHEN CHI HSIANG',
        'Chiao Fu Enterprise Co.Ltd': 'CHIAO FU',
        'Chiao Fu Enterprises Co., Ltd': 'CHIAO FU',
        'JIANN FONG POLYURETHANE': 'JIANN FONG',
        'TONG FONG TRADING CO LTD': 'TONG FONG',
        'TONG FONG TRADING CO., LTD.': 'TONG FONG',
        'Len Wa Enterprise Corp.': 'LEN WA',
        'Tayfull Industrial Co.Ltd': 'TAYFULL',
    }

def get_default_competitor_list() -> List[str]:
    """Default list of competitors for analysis."""
    return ['mcns', 'wanhua', 'basf', 'hanwha', 'sabic', 'other']


def load_and_clean_data(filename: str) -> pd.DataFrame:
    """Load CSV file and perform initial data cleaning."""
    try:
        df = pd.read_csv(filename)
        # Clean column names by removing leading/trailing spaces
        df = df.rename(mapper=str.strip, axis='columns')
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"File {filename} not found")
    except Exception as e:
        raise Exception(f"Error loading file: {str(e)}")

def process_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Process and validate date columns."""
    df = df.copy()
    
    # Convert date to string format
    df['date'] = df['date'].astype(str)
    
    try:
        # Parse date and extract year
        df['date_1'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
        df['year'] = df['date_1'].dt.year
    except Exception as e:
        raise ValueError(f"Error processing dates. Expected format: DD.MM.YYYY. Error: {str(e)}")
    
    # Sort by date and reset index
    df = df.sort_values(by='date_1').reset_index(drop=True)
    
    return df

def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert relevant columns to numeric types."""
    df = df.copy()
    
    # Convert price and margin columns to numeric
    df['pp'] = pd.to_numeric(df['pp'], errors='coerce')
    df['margin'] = pd.to_numeric(df['margin'], errors='coerce')
    
    # Handle volume column (replace comma with dot for decimal conversion)
    df['volume'] = df['volume'].str.replace(',', '.').astype(float)
    
    return df

def filter_required_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Select only required columns and remove invalid records."""
    required_columns = [
        'year', 'date_1', 'sold_to_customer', 'soldto_code', 
        'material', 'material_code', 'volume', 'nasp', 'pp'
    ]
    
    # Select required columns and drop rows with missing NASP values
    filtered_df = df[required_columns].copy()
    filtered_df = filtered_df.dropna(subset=['nasp'])
    
    return filtered_df

def map_tdi_customers(df: pd.DataFrame, customer_mapping: Dict[str, str]) -> pd.DataFrame:
    """Map customer names and filter for TDI customers only."""
    df = df.copy()
    
    # Map customer names to standardized versions
    df['tdi_customer'] = df['sold_to_customer'].map(customer_mapping)
    
    # Filter for TDI customers only (those that exist in mapping)
    tdi_df = df[df['sold_to_customer'].isin(customer_mapping.keys())].copy()
    
    if tdi_df.empty:
        print("Warning: No TDI customers found in the data")
    
    return tdi_df

def aggregate_customer_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data by year and customer."""
    if df.empty:
        return df
    
    # Group by year and customer, calculate mean price and total volume
    grouped_df = df.groupby(['year', 'tdi_customer']).agg({
        'pp': 'mean',
        'volume': 'sum'
    }).reset_index()
    
    # Round values for better readability
    grouped_df['pp'] = grouped_df['pp'].round(2)
    grouped_df['volume'] = grouped_df['volume'].round(2)
    
    return grouped_df

def add_competitor_analysis(df: pd.DataFrame, competitor_list: List[str]) -> pd.DataFrame:
    """Add competitor columns and calculate total demand."""
    if df.empty:
        return df
    
    result_df = df.copy()
    
    # Initialize all competitor columns with 0.0
    for competitor in competitor_list:
        result_df[competitor] = 0.0
    
    # Calculate total demand (current volume + competitor volumes)
    competitor_sum = result_df[competitor_list].sum(axis=1)
    result_df['demand'] = result_df['volume'] + competitor_sum
    
    # Reorder columns for better presentation
    column_order = ['year', 'tdi_customer', 'pp', 'demand', 'volume'] + competitor_list
    result_df = result_df[column_order]
    
    return result_df

def validate_data_quality(df: pd.DataFrame) -> None:
    """Perform basic data quality checks and print summary."""
    print(f"Data Summary:")
    print(f"- Total records: {len(df)}")
    print(f"- Date range: {df['year'].min()} - {df['year'].max()}")
    print(f"- Unique customers: {df['tdi_customer'].nunique()}")
    print(f"- Total volume: {df['volume'].sum():.2f}")
    print(f"- Average price: {df['pp'].mean():.2f}")

def explore_data(filename: str, 
                customer_mapping: Optional[Dict[str, str]] = None,
                competitor_list: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Explore and process TDI customer data from CSV file.
    
    Args:
        filename (str): The path to the CSV file containing sales data.
        customer_mapping (Dict[str, str], optional): Custom customer name mapping.
                                                   If None, uses default mapping.
        competitor_list (List[str], optional): Custom list of competitors.
                                             If None, uses default list.
    
    Returns:
        pd.DataFrame: Processed TDI customer data with competitor analysis.
    """
    
    # Use provided configuration or defaults
    if customer_mapping is None:
        customer_mapping = get_default_customer_mapping()
    
    if competitor_list is None:
        competitor_list = get_default_competitor_list()
    
    # Validate inputs
    if not isinstance(customer_mapping, dict):
        raise ValueError("customer_mapping must be a dictionary")
    
    if not isinstance(competitor_list, list):
        raise ValueError("competitor_list must be a list")
    
    print(f"Using {len(customer_mapping)} customer mappings")
    print(f"Using {len(competitor_list)} competitors: {competitor_list}")
    
    # Process data step by step (same as before)
    print("Loading and cleaning data...")
    df = load_and_clean_data(filename)
    
    print("Processing dates...")
    df = process_dates(df)
    
    print("Converting numeric columns...")
    df = convert_numeric_columns(df)
    
    print("Filtering required columns...")
    df = filter_required_columns(df)
    
    print("Mapping TDI customers...")
    df = map_tdi_customers(df, customer_mapping)
    
    print("Aggregating customer data...")
    df = aggregate_customer_data(df)
    
    print("Adding competitor analysis...")
    df = add_competitor_analysis(df, competitor_list)
    
    # Validate and summarize results
    if not df.empty:
        validate_data_quality(df)
    else:
        print("Warning: No data to process after filtering")
    
    print("Data processing completed successfully!")
    return df

if __name__ == "__main__":
    DEFAULT_TDI_BP = 'data/TW_TDI_1.csv'
    df = explore_data(DEFAULT_TDI_BP)
    print(df.head(10))
