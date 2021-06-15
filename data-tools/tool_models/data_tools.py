import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class LocationData:
    def __init__(self, csv_file):
        self.locations_df = pd.read_csv(csv_file)
        self._add_case_totals()
        self._tidy_data()
        self._set_all_totals(
            {'metro': 'Market-Metro', 'region': 'Region'})
        self.region_data = self.get_region_data()
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

    def get_region_data(self):
        region_data = self.locations_df.loc[:, ['Company + Location', 'Region', 'Market-Metro']]
        region_data.rename(columns={'Company + Location': 'Locations'}, inplace=True)
        return region_data

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
