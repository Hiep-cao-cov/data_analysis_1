import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

def plot_customer_demand(df, customer_name, customer_column, suppliers, 
                         year_column='year', demand_ylim=None,
                         title_fontsize=14, axis_label_fontsize=12, 
                         tick_fontsize=10, legend_fontsize=9, 
                         legend_title_fontsize=10, value_label_fontsize=None,
                         demand_label_fontsize=12):
    """
    Plot a combined chart with stacked bars for supplier volumes for all years (2022-2025).
    Overlay transparent bars (border only) for 'demand' column values for 2022-2024.
    For 2025, overlay a transparent 'demand' bar with 'demand: <value>' label.
    
    Parameters:
    df (pd.DataFrame): Dataframe containing the data with 'demand' column
    customer_name (str): Name of the customer to plot
    customer_column (str): Name of the column containing customer names
    suppliers (list): List of supplier column names for stacked bars
    year_column (str, optional): Name of the year column. Defaults to 'year'
    demand_ylim (tuple, optional): Y-axis limits for demand as (min, max)
    title_fontsize (int, optional): Font size for chart title. Defaults to 14
    axis_label_fontsize (int, optional): Font size for axis labels. Defaults to 12
    tick_fontsize (int, optional): Font size for axis tick labels. Defaults to 10
    legend_fontsize (int, optional): Font size for legend items. Defaults to 9
    legend_title_fontsize (int, optional): Font size for legend title. Defaults to 10
    value_label_fontsize (int, optional): Font size for value labels on bars. If None, auto-calculated
    demand_label_fontsize (int, optional): Font size for demand value labels. Defaults to 12
    """

    # Validate required columns exist, including hardcoded 'demand'
    required_columns = [customer_column, year_column, 'demand'] + suppliers
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Verify customer exists
    if customer_name not in df[customer_column].values:
        available_customers = sorted(df[customer_column].unique())
        raise ValueError(f"Customer '{customer_name}' not found in column '{customer_column}'. "
                        f"Available customers: {available_customers}")
    
    # Verify suppliers exist in dataframe
    missing_suppliers = [sup for sup in suppliers if sup not in df.columns]
    if missing_suppliers:
        raise ValueError(f"Supplier columns not found: {missing_suppliers}")
    
    # Filter dataframe for the specified customer
    customer_df = df[df[customer_column] == customer_name].copy()
    
    if customer_df.empty:
        raise ValueError(f"No data found for customer '{customer_name}' in column '{customer_column}'")
    
    # Sort by year to ensure proper bar alignment
    customer_df = customer_df.sort_values(year_column)
    
    # Generate colors for suppliers
    def generate_colors(n):
        """Generate n distinct colors"""
        if n <= 10:
            base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            return base_colors[:n]
        else:
            import matplotlib.cm as cm
            colormap = cm.get_cmap('tab20')
            return [colormap(i/n) for i in range(n)]
    
    supplier_colors = generate_colors(len(suppliers))
    
    # Get unique years
    years = sorted(customer_df[year_column].unique())
    n_years = len(years)
    
    if n_years == 0:
        raise ValueError(f"No data found for customer '{customer_name}'")
    
    # Set up bar positions
    bar_width = 0.6
    x = np.arange(n_years)
    
    # Create the plot
    fig_width = max(12, len(suppliers))
    fig, ax1 = plt.subplots(figsize=(fig_width, 9))
    
    # Plot stacked bars for supplier volumes for all years
    bottom = np.zeros(n_years)
    max_demand = 0
    
    for j, supplier in enumerate(suppliers):
        values = np.array([customer_df[customer_df[year_column] == year][supplier].iloc[0] 
                          if year in customer_df[year_column].values and not customer_df[customer_df[year_column] == year].empty
                          else 0 for year in years])
        
        bars = ax1.bar(x, values, bar_width, bottom=bottom, 
                      label=supplier.replace('_', ' ').title(), color=supplier_colors[j])
        
        # Add value labels on each stack (only if value > 0) with custom font size
        for i, (bar, value) in enumerate(zip(bars, values)):
            if value > 0:
                label_y = bottom[i] + value / 2
                year_data = customer_df[customer_df[year_column] == years[i]]
                total_height = year_data[suppliers].sum(axis=1).iloc[0] if not year_data.empty else 0
                show_label = value > total_height * 0.05
                
                if show_label:
                    # Use custom font size or auto-calculate
                    if value_label_fontsize is not None:
                        font_size = value_label_fontsize
                    else:
                        font_size = max(6, min(10, 80//len(suppliers)))
                    
                    ax1.text(bar.get_x() + bar.get_width()/2, label_y, 
                            f'{value:.0f}',
                            ha='center', va='center', 
                            fontsize=font_size,
                            fontweight='bold',
                            color='white' if value > total_height * 0.15 else 'black',
                            bbox=dict(boxstyle='round,pad=0.2', 
                                    facecolor='black' if value > total_height * 0.15 else 'white',
                                    alpha=0.7, edgecolor='none'))
        
        bottom += values
        max_demand = max(max_demand, bottom.max())
    
    # Add transparent demand bars for 2022-2024
    demand_values = np.array([customer_df[customer_df[year_column] == year]['demand'].iloc[0] 
                             if year in customer_df[year_column].values and not customer_df[customer_df[year_column] == year].empty
                             else 0 for year in years])
    
    for i, year in enumerate(years):
        if year in [2022, 2023, 2024]:
            demand_value = demand_values[i]
            if pd.notna(demand_value) and demand_value > 0:
                demand_bar = ax1.bar(x[i], demand_value, bar_width, 
                                    facecolor='none', edgecolor='blue', linewidth=0.3, 
                                    label='Demand (2022-2024)' if i == 0 else None)
                # Add value label above the bar with custom font size
                ax1.text(x[i], demand_value + (demand_value * 0.05), 
                        f'{demand_value:.0f}',
                        ha='center', va='bottom', fontsize=demand_label_fontsize, fontweight='bold',
                        color='blue')
                max_demand = max(max_demand, demand_value)
            else:
                print(f"Warning: Demand value for {year} is NaN or zero. No demand bar plotted.")
    
    # Plot demand bar for 2025 at the same position with transparent fill and border
    if 2025 in years:
        idx_2025 = years.index(2025)
        year_data = customer_df[customer_df[year_column] == 2025]
        if not year_data.empty:
            demand_value = year_data['demand'].iloc[0]
            if pd.notna(demand_value):
                demand_bar = ax1.bar(x[idx_2025], demand_value, bar_width, 
                                    facecolor='none', edgecolor='red', linewidth=2, 
                                    label='2025 Demand')
                # Existing value label above the bar with custom font size
                ax1.text(x[idx_2025], demand_value + (demand_value * 0.05), 
                        f'{demand_value:.0f}',
                        ha='center', va='bottom', fontsize=demand_label_fontsize, fontweight='bold',
                        color='red')
               
                max_demand = max(max_demand, demand_value)
            else:
                print("Warning: Demand value for 2025 is NaN. Demand bar will not be plotted.")
    else:
        print("Warning: Year 2025 not found. Demand bar will not be plotted.")
    
    # Customize primary y-axis (demand) with custom font sizes
    ax1.set_xlabel(year_column.title(), fontsize=axis_label_fontsize)
    ax1.set_ylabel('Demand', color='black', fontsize=axis_label_fontsize)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, rotation=45 if len(str(years[0])) > 4 else 0, fontsize=tick_fontsize)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=tick_fontsize)
    ax1.grid(True, alpha=0.3)
    
    # Adjust demand Y-axis
    if demand_ylim:
        ax1.set_ylim(demand_ylim[0], demand_ylim[1])
    else:
        max_demand = max_demand if max_demand > 0 else 100
        ax1.set_ylim(0, max_demand * 1.1)
        
        import math
        tick_interval = max(1, math.ceil(max_demand / 10))
        ax1.set_yticks(np.arange(0, max_demand * 1.1 + tick_interval, tick_interval))
    
    # Create legend with custom font sizes
    handles, labels = ax1.get_legend_handles_labels()
    ncols = min(6, max(2, len(handles) // 3))
    
    ax1.legend(handles, labels, 
              title='Legend', 
              loc='center right', 
              bbox_to_anchor=(1, 0.9),
              frameon=True, 
              fancybox=True, 
              shadow=True, 
              ncol=ncols, 
              fontsize=legend_fontsize,
              title_fontsize=legend_title_fontsize)
    
    # Title with custom font size
    plt.title(f'Demand Analysis for {customer_name} total demand (mt)', 
              fontsize=title_fontsize, fontweight='bold', pad=20)
    
    fig.subplots_adjust(bottom=0.18)
    #plt.show()
       
    
    
    # REMOVE THIS LINE: plt.show() 
    # Instead, return the figure object
    return fig

def plot_customer_demand_with_price(df, customer_name, customer_column, suppliers, 
                                   year_column='year', demand_ylim=None, price_ylim=None, 
                                   price_columns=None, price_colors=None,
                                   title_fontsize=14, axis_label_fontsize=12, 
                                   tick_fontsize=11, legend_fontsize=9, 
                                   legend_title_fontsize=10, value_label_fontsize=None,
                                   price_annotation_fontsize=9, annotation_spacing=20):
    """
    Plot a combined chart with stacked bars for supplier volumes for all years (2022-2025).
    Overlay transparent bars (border only) for 'demand' column values for 2022-2024.
    For 2025, overlay a transparent 'demand' bar with 'demand: <value>' label.
    Also plots multiple line charts for prices with enhanced clarity for close values.
    
    Parameters:
    df (pd.DataFrame): Dataframe containing the data with 'demand' column
    customer_name (str): Name of the customer to plot
    customer_column (str): Name of the column containing customer names
    suppliers (list): List of supplier column names for stacked bars
    year_column (str, optional): Name of the year column. Defaults to 'year'
    demand_ylim (tuple, optional): Y-axis limits for demand as (min, max)
    price_ylim (tuple, optional): Y-axis limits for price as (min, max)
    price_columns (list, optional): List of price column names to plot. If None, no price lines
    price_colors (list, optional): List of colors for price lines. If None, uses default colors
    title_fontsize (int, optional): Font size for chart title. Defaults to 14
    axis_label_fontsize (int, optional): Font size for axis labels. Defaults to 12
    tick_fontsize (int, optional): Font size for axis tick labels. Defaults to 11
    legend_fontsize (int, optional): Font size for legend items. Defaults to 9
    legend_title_fontsize (int, optional): Font size for legend title. Defaults to 10
    value_label_fontsize (int, optional): Font size for value labels on bars. If None, auto-calculated
    price_annotation_fontsize (int, optional): Font size for price annotations. Defaults to 9
    annotation_spacing (int, optional): Vertical spacing between price annotations. Defaults to 20
    """
    # Validate required columns exist, including hardcoded 'demand'
    required_columns = [customer_column, year_column, 'demand'] + suppliers
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Verify customer exists
    if customer_name not in df[customer_column].values:
        available_customers = sorted(df[customer_column].unique())
        raise ValueError(f"Customer '{customer_name}' not found in column '{customer_column}'. "
                        f"Available customers: {available_customers}")
    
    # Verify suppliers exist in dataframe
    missing_suppliers = [sup for sup in suppliers if sup not in df.columns]
    if missing_suppliers:
        raise ValueError(f"Supplier columns not found: {missing_suppliers}")
    
    # Filter dataframe for the specified customer
    customer_df = df[df[customer_column] == customer_name].copy()
    
    if customer_df.empty:
        raise ValueError(f"No data found for customer '{customer_name}' in column '{customer_column}'")
    
    # Sort by year to ensure proper line chart connection
    customer_df = customer_df.sort_values(year_column)
    
    # Validate price columns if provided
    if price_columns:
        missing_price_cols = [col for col in price_columns if col not in df.columns]
        if missing_price_cols:
            print(f"Warning: Price columns {missing_price_cols} not found in dataframe. Skipping these columns.")
            price_columns = [col for col in price_columns if col in df.columns]
        
        if not price_columns:
            print("Warning: No valid price columns found. Only demand chart will be displayed.")
            price_columns = None
    
    # Generate colors for suppliers
    def generate_colors(n):
        """Generate n distinct colors"""
        if n <= 10:
            base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            return base_colors[:n]
        else:
            import matplotlib.cm as cm
            colormap = cm.get_cmap('tab20')
            return [colormap(i/n) for i in range(n)]
    
    supplier_colors = generate_colors(len(suppliers))
    
    # Set default or custom colors for price lines
    if price_columns:
        if price_colors is None:
            price_line_colors = ['#FF0000', '#00FF00', '#008000', '#FF00FF', '#00FFFF', 
                                '#FFA500', '#800080', '#008000', '#FFC0CB', '#A52A2A']
        else:
            price_line_colors = price_colors * ((len(price_columns) // len(price_colors)) + 1)
        
        price_line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
        price_markers = ['o', 's', '^', 'D', 'v', 'p', 'h', '*', '+', 'x']
    
    # Get unique years
    years = sorted(customer_df[year_column].unique())
    n_years = len(years)
    
    if n_years == 0:
        raise ValueError(f"No data found for customer '{customer_name}'")
    
    # Set up bar positions
    bar_width = 0.6
    x = np.arange(n_years)
    
    # Create the plot with dual y-axes
    fig_width = max(12, len(suppliers) + (len(price_columns) if price_columns else 0))
    fig, ax1 = plt.subplots(figsize=(fig_width, 9))
    
    # Plot stacked bars for supplier volumes for all years
    bottom = np.zeros(n_years)
    max_demand = 0
    
    for j, supplier in enumerate(suppliers):
        values = np.array([customer_df[customer_df[year_column] == year][supplier].iloc[0] 
                          if year in customer_df[year_column].values and not customer_df[customer_df[year_column] == year].empty
                          else 0 for year in years])
        
        bars = ax1.bar(x, values, bar_width, bottom=bottom, 
                      label=supplier.replace('_', ' ').title(), color=supplier_colors[j])
        
        # Add value labels on each stack (only if value > 0)
        for i, (bar, value) in enumerate(zip(bars, values)):
            if value > 0:
                label_y = bottom[i] + value / 2
                year_data = customer_df[customer_df[year_column] == years[i]]
                total_height = year_data[suppliers].sum(axis=1).iloc[0] if not year_data.empty else 0
                show_label = value > total_height * 0.05
                
                if show_label:
                    # Use custom font size or auto-calculate
                    if value_label_fontsize is not None:
                        font_size = value_label_fontsize
                    else:
                        font_size = max(6, min(10, 80//len(suppliers)))
                    
                    ax1.text(bar.get_x() + bar.get_width()/2, label_y, 
                            f'{value:.0f}',
                            ha='center', va='center', 
                            fontsize=font_size,
                            fontweight='bold',
                            color='white' if value > total_height * 0.15 else 'black',
                            bbox=dict(boxstyle='round,pad=0.2', 
                                    facecolor='black' if value > total_height * 0.15 else 'white',
                                    alpha=0.7, edgecolor='none'))
        
        bottom += values
        max_demand = max(max_demand, bottom.max())
    
    # Add transparent demand bars for 2022-2024
    demand_values = np.array([customer_df[customer_df[year_column] == year]['demand'].iloc[0] 
                             if year in customer_df[year_column].values and not customer_df[customer_df[year_column] == year].empty
                             else 0 for year in years])
    
    for i, year in enumerate(years):
        if year in [2022, 2023, 2024]:
            demand_value = demand_values[i]
            if pd.notna(demand_value) and demand_value > 0:
                demand_bar = ax1.bar(x[i], demand_value, bar_width, 
                                    facecolor='none', edgecolor='blue', linewidth=0.3, 
                                    label='Demand (2022-2024)' if i == 0 else None)
                # Add value label above the bar
                ax1.text(x[i], demand_value + (demand_value * 0.05), 
                        f'{demand_value:.0f}',
                        ha='center', va='bottom', fontsize=axis_label_fontsize, fontweight='bold',
                        color='blue')
                max_demand = max(max_demand, demand_value)
            else:
                print(f"Warning: Demand value for {year} is NaN or zero. No demand bar plotted.")
    
    # Plot demand bar for 2025 at the same position with transparent fill and border
    if 2025 in years:
        idx_2025 = years.index(2025)
        year_data = customer_df[customer_df[year_column] == 2025]
        if not year_data.empty:
            demand_value = year_data['demand'].iloc[0]
            if pd.notna(demand_value):
                demand_bar = ax1.bar(x[idx_2025], demand_value, bar_width, 
                                    facecolor='none', edgecolor='red', linewidth=2, 
                                    label='2025 Demand')
                # Existing value label above the bar
                ax1.text(x[idx_2025], demand_value + (demand_value * 0.05), 
                        f'{demand_value:.0f}',
                        ha='center', va='bottom', fontsize=axis_label_fontsize, fontweight='bold',
                        color='red')
               
                max_demand = max(max_demand, demand_value)
            else:
                print("Warning: Demand value for 2025 is NaN. Demand bar will not be plotted.")
    else:
        print("Warning: Year 2025 not found. Demand bar will not be plotted.")
    
    # Customize primary y-axis (demand)
    ax1.set_xlabel(year_column.title(), fontsize=axis_label_fontsize)
    ax1.set_ylabel('Demand', color='black', fontsize=axis_label_fontsize)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, rotation=45 if len(str(years[0])) > 4 else 0, fontsize=tick_fontsize)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=tick_fontsize)
    ax1.grid(True, alpha=0.3)
    
    # Create secondary y-axis for prices with improved annotation spacing
    if price_columns:
        ax2 = ax1.twinx()
        all_price_values = []
        
        # Smart annotation positioning system
        def calculate_annotation_positions(price_data_by_year, spacing):
            """
            Calculate non-overlapping positions for price annotations
            """
            positions = {}
            for year_idx in range(len(years)):
                year_prices = []
                for col_idx, price_col in enumerate(price_columns):
                    if year_idx < len(price_data_by_year[col_idx]) and price_data_by_year[col_idx][year_idx] is not None:
                        year_prices.append((price_data_by_year[col_idx][year_idx], col_idx))
                
                # Sort by price value to minimize crossing lines
                year_prices.sort(key=lambda x: x[0])
                
                # Assign positions with proper spacing
                base_offset = 25
                for i, (price_val, col_idx) in enumerate(year_prices):
                    positions[(year_idx, col_idx)] = base_offset + (i * spacing)
            
            return positions
        
        # Collect all price data first
        price_data_by_column = []
        for idx, price_col in enumerate(price_columns):
            price_values = []
            for year in years:
                year_data = customer_df[customer_df[year_column] == year]
                if not year_data.empty and price_col in year_data.columns:
                    price_val = year_data[price_col].iloc[0]
                    if pd.notna(price_val):
                        price_values.append(price_val)
                    else:
                        price_values.append(None)
                else:
                    price_values.append(None)
            price_data_by_column.append(price_values)
        
        # Calculate optimal annotation positions
        annotation_positions = calculate_annotation_positions(price_data_by_column, annotation_spacing)
        
        # Plot price lines with improved annotations
        for idx, price_col in enumerate(price_columns):
            price_values = price_data_by_column[idx]
            
            valid_indices = [i for i, price in enumerate(price_values) if price is not None]
            valid_x = [x[i] for i in valid_indices]
            valid_prices = [price_values[i] for i in valid_indices]
            
            if valid_prices:
                all_price_values.extend(valid_prices)
                price_label = price_col.replace('_', ' ').title()
                line_color = price_line_colors[idx % len(price_line_colors)]
                
                ax2.plot(valid_x, valid_prices, 
                        color=line_color, 
                        marker=price_markers[idx % len(price_markers)], 
                        linewidth=3, 
                        markersize=10, 
                        label=price_label,
                        linestyle=price_line_styles[idx % len(price_line_styles)],
                        markerfacecolor='white', 
                        markeredgecolor=line_color, 
                        markeredgewidth=2)
                
                # Use calculated positions for annotations
                for i, price in zip(valid_indices, valid_prices):
                    y_offset = annotation_positions.get((i, idx), 25 + (idx * annotation_spacing))
                    
                    ax2.annotate(f'{price:.2f}',
                                (x[i], price),
                                textcoords="offset points",
                                xytext=(0, y_offset),
                                ha='center', va='bottom',
                                fontsize=price_annotation_fontsize, 
                                color=line_color, 
                                fontweight='bold',
                                bbox=dict(boxstyle='round,pad=0.3', 
                                        facecolor='white', 
                                        alpha=0.9, 
                                        edgecolor=line_color, 
                                        linewidth=1.5),
                                # Add arrow for better connection
                                arrowprops=dict(arrowstyle='->', 
                                              connectionstyle='arc3,rad=0',
                                              color=line_color, 
                                              alpha=0.7,
                                              linewidth=0))
        
        ax2.set_ylabel('Price', color='red', fontsize=axis_label_fontsize)
        ax2.tick_params(axis='y', labelcolor='red', labelsize=tick_fontsize)
        
        if price_ylim and all_price_values:
            ax2.set_ylim(price_ylim[0], price_ylim[1])
        elif all_price_values:
            min_price = min(all_price_values)
            max_price = max(all_price_values)
            price_range = max_price - min_price
            if price_range > 0:
                ax2.set_ylim(min_price - price_range * 0.2, max_price + price_range * 0.2)
            else:
                padding = abs(min_price) * 0.2 if min_price != 0 else 20
                ax2.set_ylim(min_price - padding, max_price + padding)
    
    # Adjust demand Y-axis
    if demand_ylim:
        ax1.set_ylim(demand_ylim[0], demand_ylim[1])
    else:
        max_demand = max_demand if max_demand > 0 else 100
        ax1.set_ylim(0, max_demand * 1.1)
        
        import math
        tick_interval = max(1, math.ceil(max_demand / 10))
        ax1.set_yticks(np.arange(0, max_demand * 1.1 + tick_interval, tick_interval))
    
    # Create combined legend inside chart area at top right
    handles1, labels1 = ax1.get_legend_handles_labels()
    if price_columns:
        handles2, labels2 = ax2.get_legend_handles_labels()
        all_handles, all_labels = handles1 + handles2, labels1 + labels2
    else:
        all_handles, all_labels = handles1, labels1
    
    # Calculate number of columns based on legend items
    total_items = len(all_handles)
    if total_items <= 4:
        ncols = 1
    elif total_items <= 8:
        ncols = 2
    else:
        ncols = 3
    
    # Position legend inside chart area at top right
    legend = ax1.legend(all_handles, all_labels, 
                       title='Legend', 
                       loc='upper right',
                       frameon=True, 
                       fancybox=True, 
                       shadow=True, 
                       fontsize=legend_fontsize,
                       title_fontsize=legend_title_fontsize,
                       ncol=ncols,
                       columnspacing=0.8,
                       handletextpad=0.5,
                       borderaxespad=0.5,
                       framealpha=0.95,
                       facecolor='white',
                       edgecolor='gray',
                       bbox_to_anchor=(0.98, 0.98))
    
    legend.get_frame().set_linewidth(1.2)
    
    plt.title(f'COV sale volumes & Pocket price to {customer_name}', 
              fontsize=title_fontsize, fontweight='bold', pad=20)
    
    #plt.tight_layout()
    #plt.show()
    
    
    #fig.subplots_adjust(bottom=0.18)
    return fig

# Usage examples:

# Example 1: Basic usage with default settings
# plot_customer_demand_with_price(df, 
#                                customer_name='ABC Company',
#                                customer_column='tdi_customer',
#                                suppliers=['covestro', 'wanhua', 'basf', 'mcns'])

# Example 2: With price columns and wider annotation spacing
# plot_customer_demand_with_price(df, 
#                                customer_name='ABC Company',
#                                customer_column='tdi_customer',
#                                suppliers=['covestro', 'wanhua', 'basf', 'mcns'],
#                                price_columns=['pp', 'covestro_price'],
#                                annotation_spacing=25)

# Example 3: Multiple price lines with custom font sizes and spacing
# plot_customer_demand_with_price(df, 
#                                customer_name='ABC Company',
#                                customer_column='tdi_customer',
#                                suppliers=['covestro', 'wanhua', 'basf'],
#                                price_columns=['pp', 'covestro_price', 'market_price'],
#                                title_fontsize=16,
#                                axis_label_fontsize=12,
#                                tick_fontsize=10,
#                                legend_fontsize=9,
#                                price_annotation_fontsize=8,
#                                annotation_spacing=30)

# Example 4: Compact display for many price lines
# plot_customer_demand_with_price(df, 
#                                customer_name='ABC Company',
#                                customer_column='tdi_customer',
#                                suppliers=['covestro', 'wanhua', 'basf'],
#                                price_columns=['pp', 'covestro_price', 'market_price', 'competitor_price'],
#                                title_fontsize=14,
#                                price_annotation_fontsize=7,
#                                annotation_spacing=35,
#                                demand_ylim=(0, 5000),
#                                price_ylim=(100, 300))

# Example 5: Large presentation format
# plot_customer_demand_with_price(df, 
#                                customer_name='ABC Company',
#                                customer_column='tdi_customer',
#                                suppliers=['covestro', 'wanhua', 'basf'],
#                                price_columns=['pp', 'covestro_price'],
#                                title_fontsize=20,
#                                axis_label_fontsize=16,
#                                tick_fontsize=14,
#                                legend_fontsize=12,
#                                legend_title_fontsize=14,
#                                value_label_fontsize=12,
#                                price_annotation_fontsize=12,
#                                annotation_spacing=25)
# 

def plot_customer_business_plan(dataframe, customer_name, show_percentages=False,
                                title_fontsize=16, axis_label_fontsize=13,
                                tick_fontsize=11, legend_fontsize=12,
                                value_label_fontsize=11):
    """
    Enhanced version with better text positioning. 
    By default shows VALUES, only shows percentages if explicitly requested.
    
    Parameters:
    dataframe (pd.DataFrame): DataFrame containing columns: year, customer, min, base, max
    customer_name (str): Name of the customer to filter and visualize
    show_percentages (bool): If True, shows percentages. If False (DEFAULT), shows actual values
    title_fontsize (int, optional): Font size for chart title. Defaults to 16
    axis_label_fontsize (int, optional): Font size for axis labels. Defaults to 13
    tick_fontsize (int, optional): Font size for axis tick labels. Defaults to 11
    legend_fontsize (int, optional): Font size for legend. Defaults to 12
    value_label_fontsize (int, optional): Font size for value labels on bars. Defaults to 11
    
    Returns:
    matplotlib figure object
    """
    
    # Filter data for the specific customer
    customer_data = dataframe[dataframe['customer'] == customer_name].copy()
    
    if customer_data.empty:
        print(f"No data found for customer: {customer_name}")
        return None
    
    # Sort by year
    customer_data = customer_data.sort_values('year')
    
    # Handle missing values (replace NaN with 0)
    customer_data = customer_data.fillna(0)
    
    # Extract years and values
    years = customer_data['year'].astype(str)
    min_values = customer_data['min']
    base_values = customer_data['base'] 
    max_values = customer_data['max']
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(15, 9))
    
    # Set the width of bars
    bar_width = 0.7
    
    # Create stacked bars
    bars1 = ax.bar(years, min_values, bar_width, label='Min', color='#009fe4', alpha=0.8, edgecolor='white', linewidth=1)
    bars2 = ax.bar(years, base_values, bar_width, bottom=min_values, label='Base', color='#00bb7e', alpha=0.8, edgecolor='white', linewidth=1)
    bars3 = ax.bar(years, max_values, bar_width, bottom=min_values + base_values, label='Max', color='#ff7f41', alpha=0.8, edgecolor='white', linewidth=1)
    
    # Add value labels inside each stack segment
    for i, year in enumerate(years):
        min_val = min_values.iloc[i]
        base_val = base_values.iloc[i]
        max_val = max_values.iloc[i]
        total = min_val + base_val + max_val
        
        # Minimum height threshold for showing text (to avoid cramped labels)
        min_height_for_text = max(total * 0.05, 50)  # 5% of total or minimum 50 units
        
        # Label for Min segment (bottom segment)
        if min_val > min_height_for_text:
            # FIXED: Check show_percentages parameter properly
            if show_percentages and total > 0:
                percentage = (min_val / total) * 100
                text = f'{percentage:.1f}%'
            else:
                text = f'{min_val:.0f}'  # SHOW ACTUAL VALUE
            
            ax.text(i, min_val/2, text,
                    ha='center', va='center', fontweight='bold', 
                    color='white', fontsize=value_label_fontsize, 
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.3))
        
        # Label for Base segment (middle segment)
        if base_val > min_height_for_text:
            # FIXED: Check show_percentages parameter properly
            if show_percentages and total > 0:
                percentage = (base_val / total) * 100
                text = f'{percentage:.1f}%'
            else:
                text = f'{base_val:.0f}'  # SHOW ACTUAL VALUE
                
            ax.text(i, min_val + base_val/2, text,
                    ha='center', va='center', fontweight='bold', 
                    color='white', fontsize=value_label_fontsize,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.3))
        
        # Label for Max segment (top segment)
        if max_val > min_height_for_text:
            # FIXED: Check show_percentages parameter properly
            if show_percentages and total > 0:
                percentage = (max_val / total) * 100
                text = f'{percentage:.1f}%'
            else:
                text = f'{max_val:.0f}'  # SHOW ACTUAL VALUE
                
            ax.text(i, min_val + base_val + max_val/2, text,
                    ha='center', va='center', fontweight='bold', 
                    color='white', fontsize=value_label_fontsize,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.3))
    
    # Customize the chart with custom font sizes
    ax.set_xlabel('Year', fontsize=axis_label_fontsize, fontweight='bold')
    ax.set_ylabel('Value', fontsize=axis_label_fontsize, fontweight='bold')
    ax.set_title(f'Business plan 2023-2027 of {customer_name}', fontsize=title_fontsize, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=legend_fontsize)
    
    # Improve layout with custom font sizes
    plt.xticks(rotation=0, fontsize=tick_fontsize)
    plt.yticks(fontsize=tick_fontsize)
    plt.tight_layout()
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add some padding to the top for total labels
    y_max = max([min_values.iloc[i] + base_values.iloc[i] + max_values.iloc[i] 
                for i in range(len(years)) if not pd.isna(min_values.iloc[i] + base_values.iloc[i] + max_values.iloc[i])])
    ax.set_ylim(0, y_max * 1.15)
    
    return fig

##########################################################################################################
def plot_customer_demand1(df, customer_name, customer_column, suppliers, 
                         year_column='year', demand_ylim=None,
                         title_fontsize=14, axis_label_fontsize=12, 
                         tick_fontsize=10, legend_fontsize=9, 
                         legend_title_fontsize=10, value_label_fontsize=None,
                         demand_label_fontsize=12):
    """
    Plot a combined chart with stacked bars for supplier volumes for all years (2022-2025).
    Overlay transparent bars (border only) for 'demand' column values for 2022-2024.
    For 2025, overlay a transparent 'demand' bar with 'demand: <value>' label.
    
    Parameters:
    df (pd.DataFrame): Dataframe containing the data with 'demand' column
    customer_name (str): Name of the customer to plot
    customer_column (str): Name of the column containing customer names
    suppliers (list): List of supplier column names for stacked bars
    year_column (str, optional): Name of the year column. Defaults to 'year'
    demand_ylim (tuple, optional): Y-axis limits for demand as (min, max)
    title_fontsize (int, optional): Font size for chart title. Defaults to 14
    axis_label_fontsize (int, optional): Font size for axis labels. Defaults to 12
    tick_fontsize (int, optional): Font size for axis tick labels. Defaults to 10
    legend_fontsize (int, optional): Font size for legend items. Defaults to 9
    legend_title_fontsize (int, optional): Font size for legend title. Defaults to 10
    value_label_fontsize (int, optional): Font size for value labels on bars. If None, auto-calculated
    demand_label_fontsize (int, optional): Font size for demand value labels. Defaults to 12
    """

    # Validate required columns exist, including hardcoded 'demand'
    required_columns = [customer_column, year_column, 'demand'] + suppliers
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Verify customer exists
    if customer_name not in df[customer_column].values:
        available_customers = sorted(df[customer_column].unique())
        raise ValueError(f"Customer '{customer_name}' not found in column '{customer_column}'. "
                        f"Available customers: {available_customers}")
    
    # Verify suppliers exist in dataframe
    missing_suppliers = [sup for sup in suppliers if sup not in df.columns]
    if missing_suppliers:
        raise ValueError(f"Supplier columns not found: {missing_suppliers}")
    
    # Filter dataframe for the specified customer
    customer_df = df[df[customer_column] == customer_name].copy()
    
    if customer_df.empty:
        raise ValueError(f"No data found for customer '{customer_name}' in column '{customer_column}'")
    
    # Sort by year to ensure proper bar alignment
    customer_df = customer_df.sort_values(year_column)
    
    # Generate colors for suppliers
    def generate_colors(n):
        """Generate n distinct colors"""
        if n <= 10:
            base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            return base_colors[:n]
        else:
            import matplotlib.cm as cm
            colormap = cm.get_cmap('tab20')
            return [colormap(i/n) for i in range(n)]
    
    supplier_colors = generate_colors(len(suppliers))
    
    # Get unique years
    years = sorted(customer_df[year_column].unique())
    n_years = len(years)
    
    if n_years == 0:
        raise ValueError(f"No data found for customer '{customer_name}'")
    
    # Set up bar positions
    bar_width = 0.6
    x = np.arange(n_years)
    
    # Create the plot
    fig_width = max(12, len(suppliers))
    fig, ax1 = plt.subplots(figsize=(fig_width, 9))
    
    # Plot stacked bars for supplier volumes for all years
    bottom = np.zeros(n_years)
    max_demand = 0
    
    for j, supplier in enumerate(suppliers):
        values = np.array([customer_df[customer_df[year_column] == year][supplier].iloc[0] 
                          if year in customer_df[year_column].values and not customer_df[customer_df[year_column] == year].empty
                          else 0 for year in years])
        
        bars = ax1.bar(x, values, bar_width, bottom=bottom, 
                      label=supplier.replace('_', ' ').title(), color=supplier_colors[j])
        
        # Add percentage labels on each stack (only if value > 0) with custom font size
        for i, (bar, value) in enumerate(zip(bars, values)):
            if value > 0:
                # Calculate total for this year (sum of current bottom + remaining suppliers)
                year_data = customer_df[customer_df[year_column] == years[i]]
                total_height = year_data[suppliers].sum(axis=1).iloc[0] if not year_data.empty else 0
                
                if total_height > 0:
                    percentage = (value / total_height) * 100
                    label_y = bottom[i] + value / 2
                    show_label = value > total_height * 0.05
                    
                    if show_label:
                        # Use custom font size or auto-calculate
                        if value_label_fontsize is not None:
                            font_size = value_label_fontsize
                        else:
                            font_size = max(6, min(10, 80//len(suppliers)))
                        
                        ax1.text(bar.get_x() + bar.get_width()/2, label_y, 
                                f'{percentage:.1f}%',
                                ha='center', va='center', 
                                fontsize=font_size,
                                fontweight='bold',
                                color='white' if value > total_height * 0.15 else 'black',
                                bbox=dict(boxstyle='round,pad=0.2', 
                                        facecolor='black' if value > total_height * 0.15 else 'white',
                                        alpha=0.7, edgecolor='none'))
        
        bottom += values
        max_demand = max(max_demand, bottom.max())
    
    # Add total volume labels on top of each stacked bar
    for i, year in enumerate(years):
        year_data = customer_df[customer_df[year_column] == year]
        if not year_data.empty:
            total_vol = year_data[suppliers].sum(axis=1).iloc[0]
            if total_vol > 0:
                ax1.text(x[i], total_vol + (total_vol * 0.05), 
                        f'{total_vol:.0f}',
                        ha='center', va='bottom', 
                        fontsize=demand_label_fontsize, 
                        fontweight='bold',
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.3', 
                                facecolor='lightgray',
                                alpha=0.8, edgecolor='black'))
    
    # Add transparent demand bars for 2022-2024
    demand_values = np.array([customer_df[customer_df[year_column] == year]['demand'].iloc[0] 
                             if year in customer_df[year_column].values and not customer_df[customer_df[year_column] == year].empty
                             else 0 for year in years])
    
    for i, year in enumerate(years):
        if year in [2022, 2023, 2024]:
            demand_value = demand_values[i]
            if pd.notna(demand_value) and demand_value > 0:
                demand_bar = ax1.bar(x[i], demand_value, bar_width, 
                                    facecolor='none', edgecolor='blue', linewidth=0.3, 
                                    label='Demand (2022-2024)' if i == 0 else None)
                # Add value label above the bar with custom font size
                """
                ax1.text(x[i], demand_value + (demand_value * 0.05), 
                        f'{demand_value:.0f}',
                        ha='center', va='bottom', fontsize=demand_label_fontsize, fontweight='bold',
                        color='blue')
                """
                max_demand = max(max_demand, demand_value)
            else:
                print(f"Warning: Demand value for {year} is NaN or zero. No demand bar plotted.")
    
    # Plot demand bar for 2025 at the same position with transparent fill and border
    if 2025 in years:
        idx_2025 = years.index(2025)
        year_data = customer_df[customer_df[year_column] == 2025]
        if not year_data.empty:
            demand_value = year_data['demand'].iloc[0]
            if pd.notna(demand_value):
                demand_bar = ax1.bar(x[idx_2025], demand_value, bar_width, 
                                    facecolor='none', edgecolor='red', linewidth=2, 
                                    label='2025 Demand')
                # Existing value label above the bar with custom font size
                ax1.text(x[idx_2025], demand_value + (demand_value * 0.05), 
                        f'{demand_value:.0f}',
                        ha='center', va='bottom', fontsize=demand_label_fontsize, fontweight='bold',
                        color='red')
               
                max_demand = max(max_demand, demand_value)
            else:
                print("Warning: Demand value for 2025 is NaN. Demand bar will not be plotted.")
    else:
        print("Warning: Year 2025 not found. Demand bar will not be plotted.")
    
    # Customize primary y-axis (demand) with custom font sizes
    ax1.set_xlabel(year_column.title(), fontsize=axis_label_fontsize)
    ax1.set_ylabel('Demand', color='black', fontsize=axis_label_fontsize)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, rotation=45 if len(str(years[0])) > 4 else 0, fontsize=tick_fontsize)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=tick_fontsize)
    ax1.grid(True, alpha=0.3)
    
    # Adjust demand Y-axis
    if demand_ylim:
        ax1.set_ylim(demand_ylim[0], demand_ylim[1])
    else:
        max_demand = max_demand if max_demand > 0 else 100
        ax1.set_ylim(0, max_demand * 1.1)
        
        import math
        tick_interval = max(1, math.ceil(max_demand / 10))
        ax1.set_yticks(np.arange(0, max_demand * 1.1 + tick_interval, tick_interval))
    
    # Create legend with custom font sizes
    handles, labels = ax1.get_legend_handles_labels()
    ncols = min(6, max(2, len(handles) // 3))
    
    ax1.legend(handles, labels, 
              title='Legend', 
              loc='center right', 
              bbox_to_anchor=(1, 0.9),
              frameon=True, 
              fancybox=True, 
              shadow=True, 
              ncol=ncols, 
              fontsize=legend_fontsize,
              title_fontsize=legend_title_fontsize)
    
    # Title with custom font size
    plt.title(f'Demand Analysis for {customer_name} total demand (mt)', 
              fontsize=title_fontsize, fontweight='bold', pad=20)
    
    fig.subplots_adjust(bottom=0.18)
    
    return fig