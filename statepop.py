import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

data_path = r"US Population Estimates.csv" #https://www.fs.usda.gov/rds/archive/Catalog/RDS-2017-0017
pop_data1 = pd.read_csv(data_path, skiprows=[0],index_col='Year')

pop_data2 = pd.read_csv("https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/state/st-est00int-agesex.csv")
pop_data2 = pop_data2.loc[(pop_data2['AGE'] == 999) & (pop_data2['SEX'] == 0)] 
pop_data2 = pop_data2.drop(['REGION','DIVISION','STATE','SEX','AGE','ESTIMATESBASE2000','CENSUS2010POP'],axis=1)
pop_data2.rename(columns={"POPESTIMATE2000": 2000, 'POPESTIMATE2001': 2001, 'POPESTIMATE2002': 2002, 'POPESTIMATE2003': 2003, 'POPESTIMATE2004': 2004, 'POPESTIMATE2005': 2005, 'POPESTIMATE2006': 2006, 'POPESTIMATE2007': 2007, 'POPESTIMATE2008': 2008, 'POPESTIMATE2009': 2009, 'POPESTIMATE2010': 2010},inplace=True)
pop_data2.set_index('NAME',inplace=True)
pop_data2 = pop_data2.transpose().reset_index()
pop_data2.rename(columns={"index": 'Year', 'United States': 'Total'},inplace=True)
pop_data2.rename(index={'NAME': ''}, inplace=True)
pop_data2 = pop_data2.set_index('Year')

pop_data3 = pd.read_csv("http://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv")
pop_data3 = pop_data3.loc[:, pop_data3.columns.intersection(['NAME','POPESTIMATE2011','POPESTIMATE2012','POPESTIMATE2013','POPESTIMATE2014','POPESTIMATE2015','POPESTIMATE2016','POPESTIMATE2017','POPESTIMATE2018','POPESTIMATE2019'])]
pop_data3.rename(columns={'POPESTIMATE2011': 2011, 'POPESTIMATE2012': 2012, 'POPESTIMATE2013': 2013, 'POPESTIMATE2014': 2014, 'POPESTIMATE2015': 2015, 'POPESTIMATE2016': 2016, 'POPESTIMATE2017': 2017, 'POPESTIMATE2018': 2018, 'POPESTIMATE2019': 2019},inplace=True)
pop_data3.set_index('NAME',inplace=True)
pop_data3 = pop_data3.transpose().reset_index()
pop_data3.rename(columns={"index": 'Year', 'United States': 'Total'},inplace=True)
pop_data3 = pop_data3.drop(['Northeast Region','Midwest Region','South Region','West Region'],axis=1)
pop_data3.rename(index={'NAME': ''}, inplace=True)
pop_data3 = pop_data3.set_index('Year')

pop_data4 = pd.concat([pop_data1,pop_data2,pop_data3])
pop_data4 = pop_data4.stack().reset_index()
pop_data4.rename(columns={"level_1": "State", 0: "Population"},inplace=True)

us_state_abbrev = {
'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'}
pop_data4['state_code'] = pop_data4['State'].map(us_state_abbrev).fillna(pop_data4['State'])

df = pop_data4
df = df.groupby(['State', 'Year', 'state_code'])[['Population']].sum()
df.reset_index(inplace=True)

######

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
# App layout
app.layout = dbc.Container([
    
    dbc.Row(
        dbc.Col(html.Br(),
                width=12),
    ),
    
    dbc.Row([
        dbc.Col(html.H1("US State Population Dashboard", 
                className='text center text-primary mb-4'),
                width=9
               ),
        dbc.Col(html.P("Created by Tom Batroney Twitter: @TomBatroney", 
                className='text right text-primary mb-4'),
                width=3
                )
    ]),
    
    dbc.Row(
        dbc.Col(html.Br(),
                width=12),
    ),
    
    dbc.Row(
        dbc.Col(dcc.Slider(
                    id="slct_year",
                    min=1564,
                    max=2019,
                    step=1,
                    value=1564),
                width=12),
    ),
    
    dbc.Row(
        dbc.Col(id='output_container', 
                children=[],
                width=12),
    ),
    
    dbc.Row(
        dbc.Col(html.Br(),
                width=12),
    ),
    
    dbc.Row(
        dbc.Col(dcc.Graph(
                id='my_pop_map', figure={},
                ),width=12),
    ),
    
    dbc.Row(
        dbc.Col(html.Br(),
                width=12),
    ),
        
    dbc.Row(
        dbc.Col(dcc.Dropdown(
                id='my-dpdn', multi=True, value=['Pennsylvania','Total'],
                         options=[{'label':x, 'value':x}
                                  for x in sorted(df['State'].unique())],
                         ),width=12),
    ),
    
    dbc.Row(
        dbc.Col(html.Br(),
                width=12),
    ),
    
    dbc.Row(
        dbc.Col(dcc.Graph(
                id='line-fig', figure={},
                ), width=12),
    ),
    
    dbc.Row(
        dbc.Col(html.Br(),
                width=12),
    ),
    
    dbc.Row(
        dbc.Col(html.P("Data Sources:", 
                className='text left text-primary'),
                width=12
               ),
    ),
        
    dbc.Row(
        dbc.Col(html.P("1564 - 1999: https://www.fs.usda.gov/rds/archive/Catalog/RDS-2017-0017", 
                className='text left text-primary'),
                width=12
               ),
    ),
    
    dbc.Row(
        dbc.Col(html.P("2000 - 2010: https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/state/st-est00int-agesex.csv", 
                className='text left text-primary'),
                width=12
               ),
    ),
    
    dbc.Row(
        dbc.Col(html.P("2011 - 2019: http://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv", 
                className='text left text-primary'),
                width=12
               ),
    ),

])


# Connect the Plotly graphs with Dash Components

#interactive map
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_pop_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(year_slctd):

    container = "Year selected: {}".format(year_slctd)

    dff = df[df["Year"] == year_slctd]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='Population',
        hover_data=['State', 'Population'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'Population': 'State Population'},
        template='plotly_dark',
        range_color=(0, 15000000)
    )
    
    return container, fig

#line graph
@app.callback(
    Output('line-fig', 'figure'),
    Input('my-dpdn', 'value')
)
def update_graph(state_slctd):
    dff = df[df['State'].isin(state_slctd)]
    figln = px.line(dff, x='Year', y='Population', color='State')
    return figln

#####

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)







