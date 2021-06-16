from tool_models.data_tools import LocationData, LocationSales, SalesData

def location_report():
    location_data = LocationData('locations.csv')
    sales_data = SalesData('sales.csv')
    location_sales = LocationSales(location_data.location_relations, sales_data.sales_df)
    quarters = {
        '1q2021': {'start_date': '01/01/2021', 'end_date': '03/31/2021'}, 
        '2q2021': {'start_date': '04/01/2021', 'end_date': '06/30/2021'},
        }
    region_comparison_dict = {}
    metro_comparison_dict = {}
    for quarter, dates in quarters.items():
        date_range = [dates['start_date'], dates['end_date']]
        
        #get data and graph of aggregated region product sales
        region_sales = location_sales.get_date_filter_aggregated_sales(
            date_range, group_by=['Region', 'Product'])
        location_sales.date_filter_grouped_product_sales_plot(region_sales)
        region_sales.to_csv(f'{quarter}region_sales.csv')
        region_comparison_dict['quarter'] = region_sales
        
        #get data and graph of aggregated market-metro and product sales
        metro_sales = location_sales.get_date_filter_aggregated_sales(
            date_range, group_by=['Market-Metro', 'Product'])
        location_sales.date_filter_grouped_product_sales_plot(metro_sales)
        metro_sales.to_csv(f'{quarter}metro_sales.csv')
        metro_comparison_dict['quarter'] = metro_sales





if __name__ == '__main__':
    print('running location report')
    location_report()