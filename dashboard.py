#!/usr/bin/env python
# coding: utf-8

# In[1]:


from data_loader import AppleDataLoader, GoogleDataLoader, CaseDataLoader
from plots import *

a = AppleDataLoader()
g = GoogleDataLoader()
c = CaseDataLoader()
print("Data loaded.")

import panel as pn
pn.extension('vega')


states = a.get_state_list()
state_input = pn.widgets.AutocompleteInput(value = "Maryland",
                            options = states,
                            placeholder = "Maryland",
                            name = "Select a state")

@pn.depends(state_input.param.value)
def make_state_pane(state_input):
    return state_pane(
        a.get_state(state_input),
        g.get_state(state_input),
        c.get_state(state_input)
    )
    
state_county_combinations = a.get_state_county_combinations()
county_input = pn.widgets.AutocompleteInput(value = "Virginia, Fairfax County",
                            options = state_county_combinations,
                            placeholder = "Virginia, Fairfax County",
                            name = "Select a state, county (case sensitive)")

@pn.depends(county_input.param.value)
def make_county_pane(county_input):
    state, county = county_input.split(', ')
    #print(state)
    return state_pane(
        a.get_county(state, county),
        g.get_county(state, county),
        c.get_county(state, county)
    )


state_comp_1 = pn.widgets.AutocompleteInput(value = "Maryland",
                            options = states,
                            placeholder = "Maryland",
                            name = "Select first state")
state_comp_2 = pn.widgets.AutocompleteInput(value = "Washington",
                            options = states,
                            placeholder = "Washington",
                            name = "Select second state")

@pn.depends(state_comp_1.param.value, state_comp_2.param.value)
def make_comp(state_comp_1, state_comp_2):
    return state_comp(state_comp_1, state_comp_2, a, g, c)


state_comp_input = pn.Row(pn.layout.HSpacer(), state_comp_1, state_comp_2, pn.layout.HSpacer())
state_comparison = pn.Row(pn.layout.VSpacer(width = 10),
                          pn.Column(
                            pn.layout.HSpacer(height = 10),
                            state_comp_input,
                            pn.layout.HSpacer(height = 5),
                            pn.pane.Markdown("Brush over top left plot to zoom in on a date range."),
                            pn.layout.HSpacer(height = 5),
                            make_comp)
                         )

country_prompt = pn.pane.Markdown("Brush over top left plot to zoom in on a date range.")
country_plots = country_pane(a.get_country_long_raw(), g.get_country_long(), c.get_country())

country = pn.Row(pn.layout.VSpacer(width = 10), 
                 pn.Column(
                     pn.layout.HSpacer(height = 10),
                     country_prompt,
                     pn.layout.HSpacer(height = 10),
                     country_plots)
                )

state = pn.Row(pn.layout.VSpacer(width = 10),
               pn.Column(
                   pn.layout.HSpacer(height = 10),
                   state_input,
                   pn.layout.HSpacer(height = 10),
                   pn.pane.Markdown("Brush over top left plot to zoom in on a date range."),
                   pn.layout.HSpacer(height = 5),
                   make_state_pane
               )
              )

county = pn.Row(pn.layout.VSpacer(width = 10),
               pn.Column(
                   pn.layout.HSpacer(height = 10),
                   county_input,
                   pn.layout.HSpacer(height = 10),
                   pn.pane.Markdown("Brush over top left plot to zoom in on a date range."),
                   pn.layout.HSpacer(height = 5),
                   make_county_pane
               )
              )

about = pn.Row(pn.layout.VSpacer(width = 10),
               pn.Column(pn.layout.HSpacer(width = 10),
                         pn.pane.Markdown("##Datasets"),
                         pn.pane.Markdown(apple_link()),
                         pn.pane.Markdown(apple_description()),
                         pn.pane.Markdown(google_link()),
                         pn.pane.Markdown(google_description()),
                         pn.pane.Markdown(jhu_link()),
                         
                        width = 600)
              )

print("Components ready.")


# In[4]:


dash = pn.Tabs(
    ("About", about),
    ("Country", country),
    ("State", state),
    ("County", county),
    ("Compare states", state_comparison)
)
dash.servable("Mobility")


# In[ ]:





# In[ ]:




