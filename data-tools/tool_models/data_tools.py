import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import calendar

class LocationData:
    def __init__(self, csv_file):
        self.locations_df = pd.read_csv(csv_file)
        self._add_case_totals()
        self._tidy_data()
        self._set_all_totals(
            {'metro': 'Market-Metro', 'region': 'Region'})
        self.location_relations = self._get_relational_data()
        self.totals_reports_graphs = {}
        
    def _add_case_totals(self):
        self.locations_df['Total Cases Sold'] = self.locations_df['Total Grocery Cases Counted'] \
            + self.locations_df['Total Food Service Cases Counted']

    def _tidy_data(self):
        self.locations_df.dropna(subset=['Total Cases Sold'], inplace=True)
        self.locations_df = self.locations_df[self.locations_df['Total Cases Sold'] != 0]
        self.locations_df = self.locations_df.loc[:, ['Company + Location', 'Region', 'Market-Metro', 'Segment', 'Total Cases Sold']]

    def _set_all_totals(self, total_types):
        self.totals = {}
        for table_name, column_name in total_types.items():
            self.totals[table_name] = self._get_totals(column_name)

    def _get_totals(self, column_name):
        totals = self.locations_df.groupby(column_name).sum()
        totals = totals.sort_values('Total Cases Sold', ascending=False)
        return totals

    def _set_report_graph(self, table_name, threshold=50):
        sns.set()
        plt.figure()
        plt.xticks(rotation=60)
        table = self.totals[table_name]
        table = table[table['Total Cases Sold'] >= threshold]
        plot = sns.barplot(x=table.index.values, y='Total Cases Sold', data=table, ci=None)
        plot.set_title(f'All Time Total Case Sales per {table_name.title()}')
        plot.set_ylabel('Case Sales')
        plot.set_xlabel(f'{table_name.title()}')
        x_labels = table.index.values
        plot.set_xticklabels(x_labels)
        self.totals_reports_graphs[table_name] = plt

    def _get_relational_data(self):
        # return data that can be used to determine relationships between 
        # a location's name, region, and market-metro
        location_relations = self.locations_df.loc[:, ['Company + Location', 'Region', 'Market-Metro']]
        location_relations.rename(columns={'Company + Location': 'Locations'}, inplace=True)
        return location_relations

    @property
    def totals_tables_names(self):
        return self.totals.keys()

    def print_totals_reports(self):
        for table_name in self.totals_tables_names:
            print(self.totals[table_name])

    def show_totals_reports_graphs(self, use_table=None):
        #list input, even if single value. Default set to all totals tables.
        if use_table == None:
            use_table = self.totals_tables_names
        for name in use_table:
            if name not in self.totals_reports_graphs: 
                #generate and save to instance if not yet done
                self._set_report_graph(name)
            #show specified plot
            self.totals_reports_graphs[name].show()


class SalesData:
    def __init__(self, csv_file):
        self.sales_df = pd.read_csv(csv_file)
        self._tidy_data()
        self.sales_totals = self._get_sales_totals()
        
    def _tidy_data(self):
        self.sales_df.dropna(subset=['Units Sold'], inplace=True)
        self.sales_df[self.sales_df['Units Sold'] != 0]
        self.sales_df = self.sales_df.loc[:, ['Locations', 'Date', 'Product', 'Units Sold']]

    def _get_sales_totals(self):
        sales_totals = self.sales_df.groupby(['Locations', 'Date', 'Product']).sum()
        sales_totals = sales_totals.sort_values(['Units Sold'])
        return sales_totals
        

class LocationSales:
    def __init__(self, location_relations, sales_data):
        self.location_relations = location_relations
        self.sales_totals = sales_data
        self.location_sales = self._get_combined()

    def _get_combined(self):
        combined = pd.merge(self.location_relations, self.sales_totals)
        combined['Date'] = pd.to_datetime(combined['Date'])
        return combined

    def date_filter_sales(self, date_range):
        date_mask = (self.location_sales['Date'] > date_range[0]) & (self.location_sales['Date'] <= date_range[1])
        filtered_sales = self.location_sales.loc[date_mask]
        self.current_date_range = date_range
        return filtered_sales

    def aggregate_sales(self, location_sales, group_by=['Region', 'Product']):
        aggregate_functions = {'Units Sold': 'sum'}
        grouped_totals = location_sales.groupby(group_by, as_index=False)
        grouped_totals = grouped_totals.agg(aggregate_functions)
        grouped_totals = grouped_totals.sort_values('Units Sold', ascending=False)
        self.current_group_by = group_by
        return grouped_totals

    def get_date_filter_aggregated_sales(self, date_range, group_by):
        filtered_sales = self.date_filter_sales(date_range)
        aggregated_sales = self.aggregate_sales(
            filtered_sales, group_by=group_by)

        return aggregated_sales

    def date_filter_grouped_product_sales_plot(self, aggregated_sales):
        #display a plot of the sales with the current group by settings
        sns.set()
        plt.figure()
        plt.xticks(rotation=60)
        palette = sns.color_palette("rainbow_r", len(aggregated_sales[self.current_group_by[1]].unique()))
        plot = sns.barplot(x=self.current_group_by[0], y='Units Sold', hue=self.current_group_by[1], data=aggregated_sales, ci=None, palette=palette)
        plot.set_title(f'Unit Sales by {self.current_group_by[0]} and {self.current_group_by[1]} from {self.current_date_range[0]} to {self.current_date_range[1]}')
        plot.set_ylabel('Unit Sales')
        plot.set_xlabel(f'{self.current_group_by[0]} by {self.current_group_by[1]}')
        plt.legend(loc=1, fontsize='18', title=f'{self.current_group_by[1]} Types')
        plt.tight_layout()
        plt.show()


class SalesTimeSeries:
    def __init__(self, locations_csv, sales_csv, group_by, periods_by='month', years=[2019, 2020, 2021]):
        self.location_data = LocationData(locations_csv)
        self.sales_data = SalesData(sales_csv)
        self.group_by = group_by
        self.period_years = years
        self.period_duration = periods_by
        self.location_sales = LocationSales(self.location_data.location_relations, self.sales_data.sales_df)
        self._set_period_dict() #set self.periods_dict
        self._set_period_sales() #set self.period_sales
        self._combine_sales()

    def _set_period_dict(self):
        periods_dict = {}
        for year in self.period_years:
            if self.period_duration == 'month':
                for month in range(1, 13):
                    for month in range(1, 13):
                        _, month_end_day = calendar.monthrange(year, month)
                        key_name = f'month_{month}_{year}'
                        periods_dict[key_name] = {'start_date': f'{month}/01/{year}', 'end_date': f'{month}/{month_end_day}/{year}'}
            self.periods_dict = periods_dict

    def _set_period_sales(self):
        period_sales = {}
        dates_dict = self.periods_dict
        for period, dates in dates_dict.items():
            date_range = [dates['start_date'], dates['end_date']]
            #get data and graph of aggregated sales for group_by
            zone_sales = self.location_sales.get_date_filter_aggregated_sales(
                date_range, group_by=self.group_by)
            period_sales[f'{period}'] = zone_sales
        self.period_sales = period_sales

    def _combine_sales(self):
        for sales_period, sales_data in self.period_sales.items():
            sales_data['Period'] = sales_period
        self.period_sales = pd.concat(self.period_sales.values(), ignore_index=True)
    
    def show_lineplot(self):
        sns.set()
        plt.figure()
        plt.xticks(rotation=60)
        palette = sns.color_palette("rainbow_r", len(self.period_sales['Product'].unique()))
        plot = sns.lineplot(x='Period', y='Units Sold', hue='Product', style=self.group_by[0], data=self.period_sales, ci=None, palette=palette)
        plot.set_title(f'Monthly Unit Sales by {self.group_by[1]} and {self.group_by[0]}')
        plot.set_ylabel('Unit Sales')
        plot.set_xlabel(f'Time Period')
        plt.legend(loc=2, fontsize='8', title=f'{self.group_by[1]} and {self.group_by[0]}')
        plt.tight_layout()
        plt.show()
