from tool_models.data_tools import LocationData, LocationSales, SalesData, SalesTimeSeries
import calendar

def dual_zone_report(dates_dict):
    # graph region and market metro product sales for each date entry in 
    # dates_dict 
    location_data = LocationData('locations.csv')
    sales_data = SalesData('sales.csv')
    location_sales = LocationSales(location_data.location_relations, sales_data.sales_df)
    
    for period, dates in dates_dict.items():
        date_range = [dates['start_date'], dates['end_date']]
        
        #get data and graph of aggregated region product sales
        region_sales = location_sales.get_date_filter_aggregated_sales(
            date_range, group_by=['Region', 'Product'])
        location_sales.date_filter_grouped_product_sales_plot(region_sales)
        region_sales.to_csv(f'{period}region_sales.csv')
        
        #get data and graph of aggregated market-metro and product sales
        metro_sales = location_sales.get_date_filter_aggregated_sales(
            date_range, group_by=['Market-Metro', 'Product'])
        location_sales.date_filter_grouped_product_sales_plot(metro_sales)
        metro_sales.to_csv(f'{period}metro_sales.csv')

def region_sales_wide_series():
    group_by=['Region', 'Product']
    sts = SalesTimeSeries('locations.csv', 'sales.csv',  group_by)
    sts.show_lineplot()

if __name__ == '__main__':
    quarters = {
        '1q2021': {'start_date': '01/01/2021', 'end_date': '03/31/2021'}, 
        '2q2021': {'start_date': '04/01/2021', 'end_date': '06/30/2021'},
        }
    region_sales_wide_series()
    #print('running sales report')
    #dual_zone_report(quarters)