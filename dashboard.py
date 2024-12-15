import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime
from dash import dash_table

# Criando alguns dados fictícios
df_base = pd.read_excel("base.xlsx")
df_base['ano_admissao'] = pd.to_datetime(df_base['data_admissao']).dt.year.astype('Int64')
df_base['ano_demissao'] = pd.to_datetime(df_base['data_demissao']).dt.year.astype('Int64')

df_analise_admissoes = df_base.groupby('ano_admissao').size().reset_index(name='qtd_admissoes')
df_analise_admissoes['qtd_admissoes_acumulado'] = df_analise_admissoes['qtd_admissoes'].cumsum()

df_analise_demissoes = df_base.groupby('ano_demissao').size().reset_index(name='qtd_demissoes')
df_analise_demissoes['qtd_demissoes_acumulado'] = df_analise_demissoes['qtd_demissoes'].cumsum()

ano_atual = datetime.now().year
ano_inicio = df_analise_admissoes['ano_admissao'].min()
df_analise_admissoes_demissoes = pd.DataFrame({'ano': range(ano_inicio, ano_atual + 1)})
df_analise_admissoes_demissoes = df_analise_admissoes_demissoes.merge(df_analise_admissoes, left_on='ano', right_on='ano_admissao', how='left')
df_analise_admissoes_demissoes = df_analise_admissoes_demissoes.merge(df_analise_demissoes, left_on='ano', right_on='ano_demissao', how='left')
df_analise_admissoes_demissoes['qtd_admissoes_ano_anterior'] = df_analise_admissoes_demissoes['qtd_admissoes'].shift(1, fill_value=0)
df_analise_admissoes_demissoes['qtd_admissoes_acumulado_ano_anterior'] = df_analise_admissoes_demissoes['qtd_admissoes_acumulado'].shift(1, fill_value=0)
df_analise_admissoes_demissoes['qtd_demissoes_ano_anterior'] = df_analise_admissoes_demissoes['qtd_demissoes'].shift(1, fill_value=0)
df_analise_admissoes_demissoes['qtd_demissoes_acumulado_ano_anterior'] = df_analise_admissoes_demissoes['qtd_demissoes_acumulado'].shift(1, fill_value=0)

df_base = df_base.loc[df_base['ano_admissao'] <= ano_atual]
df_base = df_base.loc[df_base['status'] == 'ativo']
df_analise_admissoes_demissoes = df_analise_admissoes_demissoes.loc[df_analise_admissoes_demissoes['ano'] <= ano_atual]
qtd_funcionarios_ativos = df_analise_admissoes_demissoes['qtd_admissoes'].sum() - df_analise_admissoes_demissoes['qtd_demissoes'].sum()
df_analise_admissoes_demissoes_ano_atual = df_analise_admissoes_demissoes.loc[df_analise_admissoes_demissoes['ano'] == ano_atual]
taxa_contratacoes_ano_anterior = df_analise_admissoes_demissoes_ano_atual['qtd_admissoes_acumulado_ano_anterior'].sum() / df_analise_admissoes_demissoes_ano_atual['qtd_admissoes_acumulado'].sum()
taxa_demissoes_ano_anterior = df_analise_admissoes_demissoes_ano_atual['qtd_demissoes_acumulado_ano_anterior'].sum() / df_analise_admissoes_demissoes_ano_atual['qtd_demissoes_acumulado'].sum()
taxa_contratacoes_ano_anterior = f'{taxa_contratacoes_ano_anterior:.2%}'
taxa_demissoes_ano_anterior = f'{taxa_demissoes_ano_anterior:.2%}'
turnover = ((df_analise_admissoes_demissoes_ano_atual['qtd_demissoes'].sum() + df_analise_admissoes_demissoes_ano_atual['qtd_admissoes'].sum()) / 2) / qtd_funcionarios_ativos
turnover = f'{turnover:.2%}'

df_analise_admissoes_demissoes['qtd_demissoes'] = -df_analise_admissoes_demissoes['qtd_demissoes']

# Criando o gráfico de barras empilhadas
fig_graph_bar = px.bar(df_analise_admissoes_demissoes, x='ano', y=['qtd_admissoes', 'qtd_demissoes'],
             labels={'value': 'Quantidade', 'variable': 'Indicador'},
             title='Contratações e Demissões por Ano',
             color_discrete_map={'qtd_admissoes': 'green', 'qtd_demissoes': 'red'})

# Ajustando o layout do gráfico
fig_graph_bar.update_layout(
    xaxis=dict(tickmode='linear', tick0=ano_inicio, dtick=1, title='', showgrid=False),
    yaxis=dict(title='', showgrid=False, visible=False),
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    font=dict(color='white'),
    margin=dict(l=40, r=40, t=40, b=40)  # Ajustando as margens para evitar corte
)

# Adicionando rótulos de dados nas barras
fig_graph_bar.update_traces(texttemplate='%{y}', textposition='outside', textfont_size=12)

df_analise_genero = df_base.groupby('genero').size().reset_index(name='qtd_genero')
fig_pie_chart = px.pie(df_analise_genero, names='genero', values='qtd_genero',
                       title='Distribuição de Gênero')

# Ajustando o layout do gráfico
fig_pie_chart.update_layout(
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    font=dict(color='white'),
    margin=dict(l=40, r=40, t=40, b=40)  # Ajustando as margens para evitar corte
)

table = dash_table.DataTable(
    id='table',
    columns=[
        {'name': 'Nome', 'id': 'nome'},
        {'name': 'Cargo', 'id': 'cargo'},
        {'name': 'Gênero', 'id': 'genero'},
        {'name': 'Setor', 'id': 'setor'},
        {'name': 'Data admissao', 'id': 'data_admissao'}
    ],
    data=df_base.to_dict('records'),
    page_size=10,  # Número de linhas por página
    page_action='native',  # Habilita a paginação nativa
    style_table={'overflowX': 'auto'},
    style_cell={
        'height': 'auto',
        'minWidth': '0px', 'maxWidth': '180px',
        'whiteSpace': 'normal'
    },
    style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'textAlign': 'center'  # Alinha o cabeçalho ao centro
    },
    style_data={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'textAlign': 'center'
    }
)

# Adicionando rótulos de dados no gráfico de pizza
fig_pie_chart.update_traces(textinfo='percent+label', textfont_size=12)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id="filtro_ano",
                    options=[{"label": ano, "value": ano} for ano in df_base["ano_admissao"].unique()],
                    placeholder="Ano",
                    multi=False,
                    value=2024
                ),
                width=1,
                style={'color': '#000000', 'padding': '10px'}
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Funcionários ativos", className="card-title"),
                            html.H6(id="qtd_funcionarios_ativos", className="card-subtitle"),
                        ]
                    ),
                    color="primary",
                    inverse=True,
                    style={'height': '100%'}
                ),
                width=3,
                style={'padding': '10px'}
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Crescimento contratações ano anterior", className="card-title"),
                            html.H6(id="taxa_contratacoes_ano_anterior", className="card-subtitle"),
                        ]
                    ),
                    color="primary",
                    inverse=True,
                    style={'height': '100%'}
                ),
                width=3,
                style={'padding': '10px'}
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Crescimento demissões ano anterior", className="card-title"),
                            html.H6(id="taxa_demissoes_ano_anterior", className="card-subtitle"),
                        ]
                    ),
                    color="primary",
                    inverse=True,
                    style={'height': '100%'}
                ),
                width=3,
                style={'padding': '10px'}
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Turnover", className="card-title"),
                            html.H6(id="turnover", className="card-subtitle"),
                        ]
                    ),
                    color="primary",
                    inverse=True,
                    style={'height': '100%'}
                ),
                width=2,
                style={'padding': '10px'}
            )
        ],
        style={'margin': '20px 0', 'display': 'flex'}
    ),
    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(figure=fig_graph_bar, id='fig_graph_bar'),
                width=6,
                style={'padding': '20px'}
            ),
            dbc.Col(
                dcc.Graph(figure=fig_pie_chart, id='fig_pie_chart'),
                width=6,
                style={'padding': '20px'}
            )
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                table,
                width=12,
                style={'padding': '20px'}
            )
        ]
    )
], style={'background-color': 'rgb(30, 30, 30)', 'padding': '20px'})

@app.callback(
    [
        Output("fig_graph_bar", "figure"),
        Output("fig_pie_chart", "figure"),
        Output("qtd_funcionarios_ativos", "children"),
        Output("taxa_contratacoes_ano_anterior", "children"),
        Output("taxa_demissoes_ano_anterior", "children"),
        Output("turnover", "children"),
        Output("table", "data"),
    ],
    [Input("filtro_ano", "value")]
)
def update_dashboard(ano):
    df_filtrado = pd.read_excel("base.xlsx")
    df_filtrado['ano_admissao'] = pd.to_datetime(df_filtrado['data_admissao']).dt.year.astype('Int64')
    df_filtrado['ano_demissao'] = pd.to_datetime(df_filtrado['data_demissao']).dt.year.astype('Int64')

    df_analise_admissoes = df_filtrado.groupby('ano_admissao').size().reset_index(name='qtd_admissoes')
    df_analise_admissoes['qtd_admissoes_acumulado'] = df_analise_admissoes['qtd_admissoes'].cumsum()

    df_analise_demissoes = df_filtrado.groupby('ano_demissao').size().reset_index(name='qtd_demissoes')
    df_analise_demissoes['qtd_demissoes_acumulado'] = df_analise_demissoes['qtd_demissoes'].cumsum()

    ano_inicio = df_analise_admissoes['ano_admissao'].min()
    df_analise_admissoes_demissoes = pd.DataFrame({'ano': range(ano_inicio, int(ano) + 1)})
    df_analise_admissoes_demissoes = df_analise_admissoes_demissoes.merge(df_analise_admissoes, left_on='ano', right_on='ano_admissao', how='left')
    df_analise_admissoes_demissoes = df_analise_admissoes_demissoes.merge(df_analise_demissoes, left_on='ano', right_on='ano_demissao', how='left')
    df_analise_admissoes_demissoes['qtd_admissoes_ano_anterior'] = df_analise_admissoes_demissoes['qtd_admissoes'].shift(1, fill_value=0)
    df_analise_admissoes_demissoes['qtd_admissoes_acumulado_ano_anterior'] = df_analise_admissoes_demissoes['qtd_admissoes_acumulado'].shift(1, fill_value=0)
    df_analise_admissoes_demissoes['qtd_demissoes_ano_anterior'] = df_analise_admissoes_demissoes['qtd_demissoes'].shift(1, fill_value=0)
    df_analise_admissoes_demissoes['qtd_demissoes_acumulado_ano_anterior'] = df_analise_admissoes_demissoes['qtd_demissoes_acumulado'].shift(1, fill_value=0)

    df_filtrado = df_filtrado.loc[df_filtrado['ano_admissao'] <= int(ano)]
    df_filtrado = df_filtrado.loc[df_filtrado['status'] == 'ativo']
    df_analise_admissoes_demissoes = df_analise_admissoes_demissoes.loc[df_analise_admissoes_demissoes['ano'] <= ano]

    # Calcular qtd de funcionários ativos
    qtd_funcionarios_ativos = df_analise_admissoes_demissoes['qtd_admissoes'].sum() - df_analise_admissoes_demissoes['qtd_demissoes'].sum()
    if qtd_funcionarios_ativos == 0:
        qtd_funcionarios_ativos = 0

    # Calcular taxa de contratações do ano anterior
    if df_analise_admissoes_demissoes_ano_atual['qtd_admissoes_acumulado'].sum() == 0:
        taxa_contratacoes_ano_anterior = 0
    else:
        taxa_contratacoes_ano_anterior = (
            df_analise_admissoes_demissoes_ano_atual['qtd_admissoes_acumulado_ano_anterior'].sum()
            / df_analise_admissoes_demissoes_ano_atual['qtd_admissoes_acumulado'].sum()
        )

    # Calcular taxa de demissões do ano anterior
    if df_analise_admissoes_demissoes_ano_atual['qtd_demissoes_acumulado'].sum() == 0:
        taxa_demissoes_ano_anterior = 0
    else:
        taxa_demissoes_ano_anterior = (
            df_analise_admissoes_demissoes_ano_atual['qtd_demissoes_acumulado_ano_anterior'].sum()
            / df_analise_admissoes_demissoes_ano_atual['qtd_demissoes_acumulado'].sum()
        )

    # Calcular turnover
    if qtd_funcionarios_ativos == 0:
        turnover = 0
    else:
        turnover = ((df_analise_admissoes_demissoes_ano_atual['qtd_demissoes'].sum() + df_analise_admissoes_demissoes_ano_atual['qtd_admissoes'].sum()) / 2) / qtd_funcionarios_ativos

    # Formatar para exibição como percentual
    taxa_contratacoes_ano_anterior = f'{taxa_contratacoes_ano_anterior:.2%}'
    taxa_demissoes_ano_anterior = f'{taxa_demissoes_ano_anterior:.2%}'
    turnover = f'{turnover:.2%}'

    # Inverter sinal da qtd_demissoes para o gráfico
    df_analise_admissoes_demissoes['qtd_demissoes'] = -df_analise_admissoes_demissoes['qtd_demissoes']

    # Atualizar os gráficos
    fig_graph_bar = px.bar(
        df_analise_admissoes_demissoes,
        x='ano',
        y=['qtd_admissoes', 'qtd_demissoes'],
        labels={'value': 'Quantidade', 'variable': 'Indicador'},
        title='Contratações e Demissões por Ano',
        color_discrete_map={'qtd_admissoes': 'green', 'qtd_demissoes': 'red'}
    )
    fig_graph_bar.update_layout(
        xaxis=dict(tickmode='linear', tick0=ano_inicio, dtick=1, title='', showgrid=False),
        yaxis=dict(title='', showgrid=False, visible=False),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    fig_graph_bar.update_traces(texttemplate='%{y}', textposition='outside', textfont_size=12)

    # Atualizar gráfico de gênero
    df_analise_genero = df_filtrado.groupby('genero').size().reset_index(name='qtd_genero')
    fig_pie_chart = px.pie(df_analise_genero, names='genero', values='qtd_genero', title='Distribuição de Gênero')
    fig_pie_chart.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    fig_pie_chart.update_traces(textinfo='percent+label', textfont_size=12)

    # Retornar os valores atualizados
    return (
        fig_graph_bar,
        fig_pie_chart,
        f"{qtd_funcionarios_ativos}",
        f"{taxa_contratacoes_ano_anterior}",
        f"{taxa_demissoes_ano_anterior}",
        f"{turnover}",
        df_filtrado.to_dict('records'),
    )

if __name__ == '__main__':
    app.run_server(debug=True)