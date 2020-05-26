import altair as alt
import pandas as pd

def country_pane(apple_us, google_us, cases_us):
    brush = alt.selection_interval(encodings=['x'])

    p1 = alt.Chart(apple_us).mark_line(interpolate='monotone').encode(
        x = alt.X('date:T'),
        y = 'volume:Q',
        color = alt.Color('transportation_type:N', scale=alt.Scale(scheme="tableau20"),
                         legend = alt.Legend(title = "Transport/Destination Type",
                                            values = ['driving', 'walking', 'transit',
                                                     'parks', 'residential', 'workplaces',
                                                     'grocery_pharmacy', 'retail_recreation',
                                                     'transit_stations'])),
        tooltip = ['date', 'transportation_type', 'volume']
    ).add_selection(brush).properties(
        title = {'text': 'How are people getting around?',
                'subtitle': 'Source: Apple mobility data, request volumes indexed to Jan 13',
                'subtitleFontSize': 10,
                'fontSize': 16}
    )

    highlight = alt.selection(type='single', on='mouseover',
                                  fields=['destination_type'], nearest=True)

    p2 = alt.Chart(google_us).mark_line(interpolate='monotone').encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = 'volume:Q',
        color = 'destination_type:N'
    ).properties(
        title = {'text': 'Where are people going?',
                'subtitle': 'Source: Google mobility data, volume relative to median Jan traffic',
                'subtitleFontSize': 10,
                'fontSize': 16}
    )

    points = p2.mark_circle().encode(
            opacity=alt.value(0)
        ).add_selection(
            highlight
        )

    lines = p2.mark_line(interpolate='monotone').encode(
            size=alt.condition(~highlight, alt.value(1), alt.value(3))
        )
    
    c1 = alt.Chart(cases_us).mark_bar(color = 'lightgrey').encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = 'cases:Q'
        ).properties(title = 'Cumulative Cases')

    c2 = alt.Chart(cases_us).mark_bar(color = 'lightblue').encode(
            x = alt.X('date:T', scale = alt.Scale(domain = brush)),
            y = alt.Y('new_cases:Q', title = 'cases')
        ).properties(title = 'Daily New Cases')

    plot = alt.vconcat(
        (p1 | (points + lines)),
        (c1 | c2)
    )
    
    return plot

def state_pane(apple, google, cases):
    brush = alt.selection_interval(encodings=['x'])

    p1 = alt.Chart(apple).mark_line(interpolate='monotone').encode(
        x = alt.X('date:T'),
        y = alt.Y('7_day:Q', title = '7-day average'),
        color = alt.Color('transportation_type:N', scale=alt.Scale(scheme="tableau20"))
    ).add_selection(brush).properties(
        title = {'text': 'How are people getting around?',
                'subtitle': 'Source: Apple mobility data, request volumes indexed to Jan 13',
                'subtitleFontSize': 10,
                'fontSize': 16}
    )

    highlight = alt.selection(type='single', on='mouseover',
                                  fields=['destination_type'], nearest=True)

    p2 = alt.Chart(google).mark_line(interpolate='monotone').encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = 'volume:Q',
        color = alt.Color('destination_type:N',
                         legend = alt.Legend(title = "Destination Type",
                                            values = ['parks', 'residential', 'workplaces',
                                                     'grocery_pharmacy', 'retail_recreation',
                                                     'transit_stations']))
    ).properties(
        title = {'text': 'Where are people going?',
                'subtitle': 'Source: Google mobility data, volume relative to median Jan traffic',
                'subtitleFontSize': 10,
                'fontSize': 16}
    )

    points = p2.mark_circle().encode(
            opacity=alt.value(0)
        ).add_selection(
            highlight
        )

    lines = p2.mark_line(interpolate='monotone').encode(
            size=alt.condition(~highlight, alt.value(1), alt.value(3))
        )
    
    c1 = alt.Chart(cases).mark_bar(color = 'lightgrey').encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = 'cases:Q'
        ).properties(title = 'Cumulative Cases')
    
    m = cases['new_cases'].max()

    c2 = alt.Chart(cases).mark_bar(color = 'lightblue').encode(
            x = alt.X('date:T', scale = alt.Scale(domain = brush)),
            y = alt.Y('new_cases:Q', title = 'cases', scale = alt.Scale(domain = (0, m)))
        ).properties(title = 'Daily New Cases')

    plot = alt.vconcat(
        (p1 | (points + lines)),
        (c1 | c2)
    )
    
    return plot

def state_comp(a, b, apple, google, cases):
    s1, s2 = apple.get_state(a), apple.get_state(b)

    c1 = cases.get_state(a)
    c2 = cases.get_state(b)

    s = pd.concat([s1, s2])
    dat = pd.concat([c1, c2])
    m = dat['new_cases'].max() 
    mc = dat['cases'].max()
    
    brush = alt.selection_interval(encodings=['x'])

    driv = alt.Chart(s).mark_line().encode(
        x = 'date:T',
        y = alt.Y('7_day', title = 'request volume'),
        color = alt.Color('state', legend = alt.Legend(title = "State"), scale = alt.Scale(scheme='dark2'))
    ).add_selection(brush).properties(
        width = 300,
        title = {'text': 'Driving directions requests',
                'subtitle': 'Source: Apple, 7-day average'}

    )


    new = alt.Chart(dat).mark_bar(interpolate = 'monotone', opacity = 0.5).encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = alt.Y('new_cases', stack = None, title = 'cases', scale = alt.Scale(domain = (0, m))),
        color = 'Province_State',
        tooltip = ['Province_State', 'date', 'new_cases']
    ).properties(width = 300, title = {'text':'New Cases',
                          'subtitle': 'Source: JHU'})

    cum = alt.Chart(dat).mark_area(interpolate = 'monotone', opacity = 0.5).encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = alt.Y('cases', stack = None),
        color = 'Province_State'
    ).properties(width = 300, title = {'text':'Cumulative Cases',
                          'subtitle': 'Source: JHU'})

    
    # google mobility data comparisons
    g1 = google.get_state(a)
    g2 = google.get_state(b)
    goog = pd.concat([g1, g2])

    work = pd.DataFrame(goog[goog.destination_type == "workplaces"])
    grocery = pd.DataFrame(goog[goog.destination_type == "grocery_pharmacy"])
    park = pd.DataFrame(goog[goog.destination_type == "parks"])

    
    wk = alt.Chart(work).mark_line(interpolate = 'monotone', opacity = 0.7).encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = 'volume:Q',
        color = 'sub_region_1:N'
    ).properties(title = {'text':'Workplace traffic',
                          'subtitle': 'Source: Google mobility data'}, width = 300)

    gr = alt.Chart(grocery).mark_line(interpolate = 'monotone', opacity = 0.7).encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = 'volume:Q',
        color = 'sub_region_1:N'
    ).properties(title = {'text':'Grocery/pharmacy traffic',
                          'subtitle': 'Source: Google mobility data'}, width = 300)

    pk = alt.Chart(park).mark_line(interpolate = 'monotone', opacity = 0.7).encode(
        x = alt.X('date:T', scale = alt.Scale(domain = brush)),
        y = 'volume:Q',
        color = 'sub_region_1:N'
    ).properties(title = {'text':'Parks traffic',
                          'subtitle': 'Source: Google mobility data'}, width = 300)


    res = alt.vconcat((driv | new | cum), (wk | gr | pk))
    
    return res



def apple_link():
    return """Apple mobility data ([source](https://www.apple.com/covid19/mobility))"""

def apple_description():
    return """*This dataset contains relative volume of directions requests per country/region, sub-region or city compared to a baseline volume on January 13th, 2020. 
    We define our day as midnight-to-midnight, Pacific time. Cities are defined as the greater metropolitan area and their geographic boundaries remain constant across the data set. In many countries/regions, sub-regions, and cities, relative volume has increased since January 13th, consistent with normal, seasonal usage of Apple Maps. Day of week effects are important to normalize as you use this data.* """

def google_link():
    return """Google mobility data ([source](https://www.google.com/covid19/mobility/))"""

def google_description():
    return """*This dataset includes mobility trends for different categories of destinations (ex: grocery and pharmacy, workplaces). Changes for each day are compared to a baseline value for that day of the week. The baseline is the median value, for the corresponding day of the week, during the 5-week period Jan 3–Feb 6, 2020.*"""

def jhu_link():
    return """JHU COVID case data ([source](https://github.com/CSSEGISandData/COVID-19))"""