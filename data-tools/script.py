from tool_models.data_tools import LocationData

def location_report():
    location_data = LocationData('locations.csv')
    location_data.print_totals_reports()
    print(location_data.get_region_data())
    location_data.show_totals_reports_graphs()

if __name__ == '__main__':
    print('running location report')
    location_report()