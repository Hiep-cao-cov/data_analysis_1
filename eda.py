import pandas as pd
def explore_data(filename: str):
    """
    Explore the data in the given CSV file.
    
    Args:
        filename (str): The path to the CSV file.
    
    Returns:
        None
    """
    customer_mapping_tdi = {
        'HEADWAY ADVANCED MATERIALS INC':'HEADWAY ADVANCED MATERIALS',
        'Headway Advanced Materials Inc.':'HEADWAY ADVANCED MATERIALS',
        'KUN CHING KEY-INDUSTRY CO LTD':'KUN CHING',
        'KUN CHING INDUSTRIAL CO., LTD.':'KUN CHING',
        'CHEN CHI HSIANG INDUSTRY':'CHEN CHI HSIANG',
        'Chiao Fu Enterprise Co.Ltd':'CHIAO FU', 
        'Chiao Fu Enterprises Co., Ltd':'CHIAO FU',
        'JIANN FONG POLYURETHANE':'JIANN FONG',
        'TONG FONG TRADING CO LTD':'TONG FONG',
        'TONG FONG TRADING CO., LTD.':'TONG FONG',
        'Len Wa Enterprise Corp.':'LEN WA',
        'Tayfull Industrial Co.Ltd': 'TAYFULL',
        'Tayfull Industrial Co.Ltd': 'TAYFULL',        
    }
    df = pd.read_csv(filename)
    # Clean column names
    df = df.rename(mapper = str.strip,axis ='columns') 
    
    # Convert 'date' column to string and filter for valid date formats
    df['date'] = df['date'].astype(str)
    df = df[df['date'].str.match(r'^\d{2}\.\d{4}$', na=False)]
    df['date_1'] = pd.to_datetime(df['date'], format='%m.%Y')
    ########################################
    df['year'] = df['date_1'].dt.year
    df.sort_values(by='date_1', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    df['pp'] = pd.to_numeric(df['pp'], errors='coerce')
    df['margin'] = pd.to_numeric(df['margin'], errors='coerce')
    df['volume'] = df['volume'].str.replace(',', '.').astype(float)
    
    show_columns = ['year','date_1','ship_to_customer','shipto_code','material','material_code','volume','nasp','pp']
    
    
    new_df = df.loc[:,show_columns]
    new_df = new_df.dropna(subset=['nasp'])
    
    new_df.loc[:,'tdi_customer'] = new_df['ship_to_customer'].map(customer_mapping_tdi)
    tdi_df = new_df[new_df['ship_to_customer'].isin(customer_mapping_tdi.keys())].copy()
    
    #unique_tdi_customers_by_year = tdi_df.groupby('year')['tdi_customer'].unique()
    
    tdi_grouped = tdi_df.groupby(['year','tdi_customer']).agg({'pp': 'mean', 'volume': 'sum'}).reset_index() 
    tdi_grouped['pp'] = tdi_grouped['pp'].apply(lambda x: round(x, 2))
    tdi_competitor_list = ['mcns', 'wanhua', 'basf', 'hanwha', 'sabic','other']
    tdi_df = tdi_grouped.copy()
    
    for column in tdi_competitor_list:
        tdi_df[column] = 0.0

    tdi_df['demand'] =tdi_df['volume'] + tdi_df[tdi_competitor_list].sum(axis=1)
    tdi_df =tdi_df[['year','tdi_customer','pp','demand','volume','wanhua', 'basf', 'mcns', 'hanwha', 'sabic','other']]  

    
    show_columns = ['year','date_1','ship_to_customer','shipto_code','material','material_code','volume','nasp','pp'] 
    return tdi_df
if __name__ == "__main__":
    DEFAULT_TDI_BP = 'data/TW_TDI.csv'
    df = explore_data(DEFAULT_TDI_BP)
    print(df.head(10))