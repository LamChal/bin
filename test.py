import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
import io

URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
resp = requests.get(URL)
text = io.BytesIO(resp.content)
df = pd.read_csv(text)
print('Data downloaded and read into a dataframe!')


app = dash.Dash(__name__)
app.title = "Automobile Sales & Economy Dashboard"
year_list = [i for i in range(1980, 2024, 1)]

app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard", style={'textAlign': 'center',
                                                             'color': '#503D36',
                                                             'font-size': '24px'}),
    dcc.Dropdown(id='dropdown-statistics', 
                   options=[
                           {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                           {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
                           ],
                  placeholder='Select a report type',
                  style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'margin':'auto', 'text-align-last': 'center'}
                  ),
    dcc.Dropdown(id='select-year', 
                   options=[{'label': i, 'value': i} for i in year_list],
                  placeholder='Select-year',
                  style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'margin':'auto', 'text-align-last': 'center'}
                  ),

    html.Div(id= 'output-container', className= 'chart-grid', style={'display': 'flex'}),
],className='justify-content-center')

@app.callback(
    Output(component_id='select-year', component_property= 'disabled'),
    Input(component_id='dropdown-statistics', component_property= 'value')
)

def update_input_container(value):
    if value =='Yearly Statistics': 
        return False
    else: 
        return True

@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), 
     Input(component_id='select-year', component_property='value')]
     )

def update_output_container(value, year):
    if value == 'Recession Period Statistics':

        recession_data = df[df['Recession'] == 1]
        yearly_rec=recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()

        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                x='Year',
                y='Automobile_Sales',
                title="Automobile sales over Recession Period"))

        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()                 
        R_chart2  = dcc.Graph(
            figure=px.bar(average_sales,
            x='Vehicle_Type',
            y='Automobile_Sales',
            title="Vehicles sold by vehicle type"))


        exp_rec= recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
                figure=px.pie(exp_rec,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title=" Pie chart for total expenditure share by vehicle type during recessions"
            )
        )


        unemp_data= recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemp_data,
        x='unemployment_rate',
        y='Automobile_Sales',
        color='Vehicle_Type',
        labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
        title='Effect of Unemployment Rate on Vehicle Type and Sales'))


        return [
            html.Div(className='chart-row', children=[
                html.Div(children=R_chart1),
                html.Div(children=R_chart2)
    ], style={'display': 'flex', 'flex-wrap': 'wrap'}),

            html.Div(className='chart-row', children=[
                html.Div(children=R_chart3),
                html.Div(children=R_chart4)
    ], style={'display': 'flex', 'flex-wrap': 'wrap'})
]
    

    elif year and value== 'Yearly Statistics' :
        yearly_data = df[df['Year'] == year]

        yas= df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(yas,
                           x='Year',
                           y='Automobile_Sales',
                           title="Average Yearly Automobile Sales"))
            

        mas = df.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(mas,
                           x='Month',
                           y='Automobile_Sales',
                           title="Total Monthly Automobile Sales"))

        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title=f"Average Vehicles Sold by Vehicle Type in {year}"))

        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                          values='Advertising_Expenditure',
                          names='Vehicle_Type',
                          title="Total Ad Expenditure per Vehicle Type"))

        return [
            html.Div(className='chart-row', children=[
                html.Div(children=Y_chart1),
                html.Div(children=Y_chart2)
    ], style={'display': 'flex', 'flex-wrap': 'wrap'}),

            html.Div(className='chart-row', children=[
                html.Div(children=Y_chart3),
                html.Div(children=Y_chart4)
    ], style={'display': 'flex', 'flex-wrap': 'wrap'})
]
    
    else:
        return [html.Div("")]

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
