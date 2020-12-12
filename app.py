import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pandas as pd
import numpy as np
import requests

def melter(df, value_vars, id_vars, value_name='value', var_name='variable'):
    return pd.melt(df, id_vars=id_vars, value_vars=value_vars, value_name=value_name, var_name=var_name)

response = requests.get('https://covid19-api.vost.pt/Requests/get_full_dataset')

df = pd.read_json(response.content)

df_dict = response.json()

# Beware the format! You Must specify the date format otherwise shit could happen!
df['data_dados'] = pd.to_datetime(df['data_dados'], format='%d-%m-%Y %H:%M')

cols_to_melt = ['confirmados_arsnorte', 'confirmados_arscentro', 'confirmados_arslvt', 'confirmados_arsalentejo', 'confirmados_arsalgarve', 'confirmados_acores', 'confirmados_madeira']

confirmados_regiao = melter(df, id_vars='data_dados', value_vars=cols_to_melt, value_name = 'confirmados_regiao', var_name='ars')

confirmados_age_f = melter(df, df.columns[22:40:2], 'data_dados')

confirmados_age_m = melter(df, df.columns[23:40:2], 'data_dados')

total_confirmed = list(df_dict['confirmados'].values())[-1]

total_deaths = list(df_dict['obitos'].values())[-1]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig_confirmados_regiao = px.line(confirmados_regiao, x='data_dados', y='confirmados_regiao', color='ars')

fig_confirmados_age_f = px.line(confirmados_age_f, x='data_dados', y='value', color='variable')

fig_confirmados_age_m = px.line(confirmados_age_m, x='data_dados', y='value', color='variable')

waterfall_fig = go.Figure(go.Waterfall(x=df['data_dados'], y=df['confirmados_novos']))

fig_confirmados_regiao.update_layout(xaxis=dict(title='Date'))

app.layout = html.Div([
    html.H1('Portugal COVID Tracker'),
    html.Div([
        html.Div('Total confirmed: %d' % total_confirmed),
        html.Div('Total deaths: %d' % total_deaths)
    ]),
    html.Div([
        dcc.Graph(id='line-graph', figure=fig_confirmados_regiao),
        html.Div([
            html.Div(dcc.Graph(id='female_confirmed', figure=fig_confirmados_age_f), style=dict(position='relative')),
            html.Div(dcc.Graph(id='male_confirmed', figure=fig_confirmados_age_m), style=dict(position='relative'))
        ],
        style=dict(display='flex')
        ),
        html.Div(dcc.Graph(id='waterfall', figure=waterfall_fig))
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)