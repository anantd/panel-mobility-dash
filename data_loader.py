import pandas as pd

class AppleDataLoader():
    
    def __init__(self):
        apple = pd.read_csv('data/applemobilitytrends-2020-05-24.csv')
        
        # filtering to US only
        apple_us = apple[(apple.country == 'United States') | (apple.region == 'United States')]
        
        # date cols to melt for apple data
        cols_to_melt = apple_us.columns.str.startswith('2020')

        # pivoting dates from wide to long
        apple_clean = apple_us.melt(
            id_vars = ['geo_type', 'region', 'sub-region', 'country', 'transportation_type'], 
            value_vars = apple_us.columns[cols_to_melt],
            var_name = 'date', 
            value_name = 'relative_vol'
        )
        
        # full dataset
        self.all_data = apple_clean 
        
        # us-wide data
        us = pd.DataFrame(apple_clean[apple_clean.geo_type == 'country/region'])
        us['date'] = pd.to_datetime(us['date'])
        us = us.drop(['geo_type', 'region', 'sub-region', 'country'], axis = 1)
        self.us = us
        
        # state-wide data (driving volume + 7-day rolling average)
        states = pd.DataFrame(apple_clean[apple_clean.geo_type == 'sub-region'])
        states['date'] = pd.to_datetime(states['date'])
        temp = states.pivot_table(
            index = ['region', 'date'], 
            values = 'relative_vol', 
            columns = 'transportation_type').reset_index()

        x = temp.groupby('region')['driving'].rolling(7).mean().reset_index()
        temp['7_day'] = x['driving']
        temp.columns = ['state', 'date', 'driving', '7_day']
        self.states = temp
        
        # county data
        counties = pd.DataFrame(apple_clean[(apple_clean.geo_type == 'county') & 
                                            (apple_clean.transportation_type == 'driving')])
        counties['date'] = pd.to_datetime(counties['date'])
        temp = counties.pivot_table(
            index = ['sub-region', 'region', 'date'], 
            values = 'relative_vol', 
            columns = 'transportation_type').reset_index()

        x = temp.groupby(['sub-region', 'region'])['driving'].rolling(7).mean().reset_index()
        temp['7_day'] = x['driving']
        temp.columns = ['state', 'county', 'date', 'driving', '7_day']
        self.counties = temp
        
        # city data
        x = pd.DataFrame(apple_clean[apple_clean.geo_type == 'city'])
        x = x.drop(['geo_type'], axis = 1)
        x['date'] = pd.to_datetime(x['date'])
        x = x.pivot_table(
                    index = ['sub-region', 'region', 'date'], 
                    values = 'relative_vol', 
                    columns = 'transportation_type').reset_index()

        driving = x.groupby(['sub-region', 'region'])['driving', 'date'].rolling(7, on = 'date').mean().reset_index()
        walking = x.groupby(['sub-region', 'region'])['walking', 'date'].rolling(7, on = 'date').mean().reset_index()
        transit = x.groupby(['sub-region', 'region'])['transit', 'date'].rolling(7, on = 'date').mean().reset_index()
        x['7_day_driving'] = driving['driving']
        x['7_day_transit'] = walking['walking']
        x['7_day_walking'] = walking['walking']

        x.columns = ['state', 'city', 'date', 'driving', 'trasit', 'walking',
                    '7_day_driving', '7_day_walking', '7_day_transit']
        
        self.cities = x
    
    
    def get_country(self):
        """Returns US-wide time series dataset."""
        x = self.us.pivot_table(index = 'date', columns = 'transportation_type', values = 'relative_vol').reset_index()
        driving = x[['driving', 'date']].rolling(7, on = 'date').mean().reset_index()
        walking = x[['walking', 'date']].rolling(7, on = 'date').mean().reset_index()
        transit = x[['transit', 'date']].rolling(7, on = 'date').mean().reset_index()
        x['7_day_driving'] = driving['driving']
        x['7_day_transit'] = walking['walking']
        x['7_day_walking'] = walking['walking']
        return pd.DataFrame(x)
    
    def get_country_long(self):
        us = self.get_country()
        x = us.melt(id_vars = 'date',
             value_vars = ['7_day_driving', '7_day_transit', '7_day_walking'],
             value_name = '7_day_average')

        l = {'7_day_driving':'driving', '7_day_walking':'walking', '7_day_transit':'transit'}
        x['transportation_type'] = x['transportation_type'].apply(lambda x: l[x])
        return x
    
    def get_country_long_raw(self):
        us = self.get_country()
        x = us.melt(id_vars = 'date',
             value_vars = ['driving', 'transit', 'walking'],
             value_name = 'volume')
        return x
    
    def get_state(self, state):
        return pd.DataFrame(self.states[self.states['state'] == state])
    
    def get_county(self, state, county):
        res = pd.DataFrame(self.counties[(self.counties['state'] == state) &
                                          (self.counties['county'] == county)]) 
        res = res.drop(['state', 'county'], axis = 1)
        return res
    
    def get_cities(self):
        return pd.DataFrame(self.cities)
    
    def get_state_list(self):
        return sorted(self.states['state'].unique())
    
    def get_state_county_combinations(self):
        res = []
        for i in list(zip(self.counties.state, self.counties.county)):
            res.append(', '.join(i))
        return list(set(res))  

    
class GoogleDataLoader():
    
    def __init__(self):
        google = pd.read_csv('data/Global_Mobility_Report.csv', low_memory = False)
        
        # filtering to US only
        google_us = google[google.country_region_code == 'US']
        
        google_clean = google_us.drop('country_region_code', 1)
        google_clean.date = pd.to_datetime(google_clean.date)
        google_clean.columns = [
            'country_region',
            'sub_region_1',
            'sub_region_2', 
            'date',
            'retail_recreation',
            'grocery_pharmacy',
            'parks',
            'transit_stations',
            'workplaces',
            'residential'
        ]

        google_clean = google_clean.set_index('date')
        
        # full dataset
        self.all_data = google_clean

        # US-wide data
        us = google_clean[google_clean.sub_region_1.isna()]
        us = us.drop(['country_region', 'sub_region_1', 'sub_region_2'], axis = 1)
        self.us = us
        
        # state-wide data
        states = google_clean[google_clean.sub_region_2.isna() & (~google_clean.sub_region_1.isna())]
        states = states.drop(['country_region', 'sub_region_2'], axis = 1)
        
        # computing 7-day moving averages for each destination category
        x = states.reset_index()
        rr = x.groupby('sub_region_1')['retail_recreation', 'date'].rolling(7, on = 'date').mean().reset_index()
        gp = x.groupby('sub_region_1')['grocery_pharmacy', 'date'].rolling(7, on = 'date').mean().reset_index()
        parks = x.groupby('sub_region_1')['parks', 'date'].rolling(7, on = 'date').mean().reset_index()
        transit = x.groupby('sub_region_1')['transit_stations', 'date'].rolling(7, on = 'date').mean().reset_index()
        work = x.groupby('sub_region_1')['workplaces', 'date'].rolling(7, on = 'date').mean().reset_index()
        resi = x.groupby('sub_region_1')['residential', 'date'].rolling(7, on = 'date').mean().reset_index()
        x['retail_recreation_7_day']= rr['retail_recreation']
        x['grocery_pharmacy_7_day']= gp['grocery_pharmacy']
        x['parks_7_day']= parks['parks']
        x['transit_stations_7_day']= transit['transit_stations']
        x['workplaces_7_day']= work['workplaces']
        x['residential_7_day'] = resi['residential']
        self.states = x
        
        # county data
        counties = google_clean[~google_clean.sub_region_2.isna() & (~google_clean.sub_region_1.isna())]
        counties = counties.drop('country_region', axis = 1)
        self.counties = counties


    def get_country(self):
        """Returns US-wide time series dataset."""
        x = self.us.reset_index()
        rr = x[['retail_recreation', 'date']].rolling(7, on = 'date').mean().reset_index()
        gp = x[['grocery_pharmacy', 'date']].rolling(7, on = 'date').mean().reset_index()
        parks = x[['parks', 'date']].rolling(7, on = 'date').mean().reset_index()
        transit = x[['transit_stations', 'date']].rolling(7, on = 'date').mean().reset_index()
        work = x[['workplaces', 'date']].rolling(7, on = 'date').mean().reset_index()
        resi = x[['residential', 'date']].rolling(7, on = 'date').mean().reset_index()
        x['retail_recreation_7_day']= rr['retail_recreation']
        x['grocery_pharmacy_7_day']= gp['grocery_pharmacy']
        x['parks_7_day']= parks['parks']
        x['transit_stations_7_day']= transit['transit_stations']
        x['workplaces_7_day']= work['workplaces']
        x['residential_7_day'] = resi['residential']
        
        return pd.DataFrame(x)
    
    def get_country_long(self):
        x = self.get_country()
        v = x.columns[1:7]
        res = x.melt(
            id_vars = 'date',
            value_vars = v,
            var_name = 'destination_type',
            value_name = 'volume'
        )
        return res

        
    def get_state(self, state):
        """Returns time series data for given state."""
        res = pd.DataFrame(self.states[self.states.sub_region_1 == state])
        v = res.columns[2:8]
        res = res.melt(id_vars = ['sub_region_1','date'],
                         value_vars = v,
                         var_name = 'destination_type',
                         value_name = 'volume')
        return res

    def get_county(self, state, county):
        """Returns time series data for given state, county pair"""
        res = pd.DataFrame(self.counties[(self.counties.sub_region_1 == state) &
                                       (self.counties.sub_region_2 == county)])
        
        v = res.columns[2:8]
        res = res.reset_index().melt(id_vars = 'date',
                         value_vars = v,
                         var_name = 'destination_type',
                         value_name = 'volume')
        
        return res
    
    
class CaseDataLoader():
    
    def __init__(self):
        raw = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
        id_vars = raw.columns[1:11]
        value_cars = raw.columns[11:]
        temp = raw.melt(id_vars = id_vars, value_vars = value_cars, var_name = 'date', value_name = 'cases')
        temp['date'] = pd.to_datetime(temp['date'])
        temp = temp[temp.Country_Region == "US"]
        temp = temp.drop(['iso2', 'iso3', 'code3', 'FIPS', 'Lat', 'Long_', 'Combined_Key'], axis = 1)
        
        self.data = temp
        
        # state data
        self.states = temp.groupby(['Province_State', 'date'])['cases'].sum().reset_index()
        
    def get_country(self):
        us = self.data.groupby(['Country_Region', 'date'])['cases'].sum().reset_index()
        us['new_cases'] = us['cases'].rolling(window=2).apply(lambda x: x[1] - x[0], raw = True)
        return us

    def get_state(self, state):
        res = pd.DataFrame(self.states[self.states.Province_State == state])
        res['new_cases'] = res['cases'].rolling(window=2).apply(lambda x: x[1] - x[0], raw = True)
        return res
    
    def get_county(self, state, county):
        x = (county.split(' ')[:-1])
        c = ' '.join(x)
        
        res = pd.DataFrame(self.data[(self.data.Province_State == state) & (self.data.Admin2 == c)])
        res['new_cases'] = res['cases'].rolling(window=2).apply(lambda x: x[1] - x[0], raw = True)
        return res