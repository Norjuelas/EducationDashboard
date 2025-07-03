import dash
from dash import Dash, html, dcc, Input, Output
import dash_cytoscape as cyto
import pandas as pd
import dash_bootstrap_components as dbc
import random

# Generar datos de prueba
years = [2023, 2024]
months = {
    2023: [1, 2, 3],
    2024: [1, 2]
}

categories = [
    {"id": "tech", "label": "Tecnología", "base_color": "#FF6B6B"},
    {"id": "finance", "label": "Finanzas", "base_color": "#4ECDC4"},
    {"id": "health", "label": "Salud", "base_color": "#45B7D1"},
    {"id": "energy", "label": "Energía", "base_color": "#96CEB4"},
    {"id": "education", "label": "Educación", "base_color": "#FFEEAD"}
]

test_data = []
node_ids = set()

for year in years:
    for month in months[year]:
        for _ in range(8):  # 8 nodos por mes
            category = random.choice(categories)
            node_id = f"{category['id']}_{year}_{month}_{random.randint(1000,9999)}"
            
            while node_id in node_ids:
                node_id = f"{category['id']}_{year}_{month}_{random.randint(1000,9999)}"
            
            node_ids.add(node_id)
            
            test_data.append({
                "año": year,
                "mes": month,
                "id_nodo": node_id,
                "label": f"{category['label']}\n{random.randint(1,100)}%",
                "tamaño_porcentaje": random.uniform(0.5, 5.0),
                "x": random.randint(50, 950),
                "y": random.randint(50, 550),
                "color": category['base_color']
            })

df = pd.DataFrame(test_data)
df['size'] = df['tamaño_porcentaje'] * 15  # Factor de escala visual

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Estilos Cytoscape
nodes_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'width': 'data(size)',
            'height': 'data(size)',
            'background-color': 'data(color)',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '20px',
            'text-outline-color': '#000',
            'text-outline-width': '2px',
            'opacity': 0.85,
            'border-color': 'rgba(255,255,255,0.8)',
            'border-width': '2px',
            'transition': 'all 0.3s ease',
            'text-wrap': 'wrap',
            'text-max-width': 'data(size)'
        }
    },
    {
        'selector': ':selected',
        'style': {
            'background-color': '#FFF',
            'border-color': '#FF0000',
            'border-width': '4px',
            'opacity': 1
        }
    },
    {
        'selector': ':hover',
        'style': {
            'opacity': 1,
            'z-index': 9999,
            'width': 'data(size)',
            'height': 'data(size)'
        }
    }
]


app.layout = dbc.Container([
    dbc.Row([
        # Left Column with Dropdowns and Text
        dbc.Col([
            # Year Dropdown
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[{'label': str(y), 'value': y} for y in df['año'].unique()],
                        value=df['año'].max(),
                        clearable=False,
                        placeholder='Select Year'
                    )
                ], width=12)
            ], style={'marginBottom': '10px'}),

            # Month Dropdown
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='month-dropdown',
                        options=[{'label': str(m), 'value': m} for m in df['mes'].unique()],
                        value=df['mes'].max(),
                        clearable=False,
                        placeholder='Select Month'
                    )
                ], width=12)
            ], style={'marginBottom': '20px'}),

            # Descriptive Text
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Descripción del Proyecto", style={'color': '#000'}),
                        html.P("Este es un análisis detallado de los datos correspondientes al año y mes seleccionados. "
                               "Utilice los menús desplegables para explorar diferentes períodos y obtener insights "
                               "sobre la información representada en el gráfico de burbujas.", style={'color': '#000'})
                    ], style={
                        'backgroundColor': '#98FF98',  # Color menta
                        'padding': '15px',
                        'borderRadius': '5px'
                    })
                ], width=12)
            ])
        ], width=4),

        # Right Column with Cytoscape and Chat
        dbc.Col([
            # Cytoscape Bubble Chart
            cyto.Cytoscape(
                id='bubble-chart',
                layout={'name': 'preset'},
                style={'width': '100%', 'height': '70vh', 'background': '#1a1a1a'},
                stylesheet=nodes_stylesheet
            ),
            
            # Chat Container
            dbc.Row([
                dbc.Col([
                    html.H4("Chat de Análisis", className="text-center", style={'marginTop': '15px'}),
                    dbc.Card([
                        dbc.CardBody([
                            # Chat Messages Area
                            html.Div(id='chat-messages', style={
                                'height': '200px', 
                                'overflowY': 'auto', 
                                'backgroundColor': '#f8f9fa', 
                                'padding': '10px',
                                'borderRadius': '5px'
                            }),
                            
                            # Chat Input
                            dbc.Row([
                                dbc.Col([
                                    dcc.Input(
                                        id='chat-input', 
                                        type='text', 
                                        placeholder='Escriba su mensaje...',
                                        style={'width': '100%'}
                                    )
                                ], width=10),
                                dbc.Col([
                                    dbc.Button('Enviar', id='send-chat', color='primary')
                                ], width=2)
                            ])
                        ])
                    ])
                ])
            ])
        ], width=8)
    ])
], fluid=True)

@app.callback(
    Output('bubble-chart', 'elements'),
    [Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_bubbles(selected_year, selected_month):
    filtered_df = df[(df['año'] == selected_year) & (df['mes'] == selected_month)]

    elements = []
    for _, row in filtered_df.iterrows():
        elements.append({
            'data': {
                'id': row['id_nodo'],
                'label': row['label'],
                'size': row['size'],
                'color': row['color'],
                'background_color': row['color'], #ejemplo
                'border_color': '#FFF', #ejemplo
                'font_size': '20px', #ejemplo
                'colors': '#000000 #FFFFFF #000000 #FFFFFF #000000 #FFFFFF #000000 #FFFFFF #000000 #FFFFFF' #ejemplo de edge
            },
            'position': {'x': row['x'], 'y': row['y']},
            'classes': 'bubble-node'
        })

    return elements

# Callback para actualizar opciones de meses según año seleccionado
@app.callback(
    Output('month-dropdown', 'options'),
    Input('year-dropdown', 'value')
)
def update_month_dropdown(selected_year):
    filtered_months = df[df['año'] == selected_year]['mes'].unique()
    return [{'label': str(m), 'value': m} for m in sorted(filtered_months)]

if __name__ == '__main__':
    app.run(debug=True)