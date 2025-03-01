import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# Load data
df = pd.read_csv("https://raw.githubusercontent.com/adeline-hub/light.danki/refs/heads/main/datasets/df_country_citrus_fao.csv")  
df_country_citrus_fao = pd.read_csv("https://raw.githubusercontent.com/adeline-hub/light.danki/refs/heads/main/datasets/df_country_citrus_fao.csv")  

# Aggregate data
df_dashboard = df[df['Year'] == 2023].groupby(['Item'], as_index=False)['Value'].sum()
df_grouped = df_country_citrus_fao.groupby(['Year', 'Item'], as_index=False)['Value'].sum()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([

    # Header with Icon & Title
    dbc.Row([
        dbc.Col(html.Img(src="https://github.com/adeline-hub/light.danki/blob/main/images/nbg11.png?raw=true", height="50px"), width="auto"),
        dbc.Col(html.H1("Citrus Production Dashboard: Where Citrus Grow?", className="text-primary"), width=8),
    ], className="my-2"),

    # Filters
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="item-filter", 
            options=[{'label': 'All', 'value': 'All'}] + [{'label': item, 'value': item} for item in df['Item'].unique()],
            value='All', clearable=False, multi=False), width=3),
        
        dbc.Col(dcc.Dropdown(
            id="year-filter", 
            options=[{'label': year, 'value': year} for year in df['Year'].unique()],
            value=df['Year'].max(), clearable=False), width=3),
    ], className="mb-3"),

    # First Row: Scatter Geo
    dbc.Row([
        dbc.Col(dcc.Graph(id="geo-scatter", style={"height": "700px"}), width=12),
    ]),

    # Second Row: Markdown & Line Chart
    dbc.Row([
        dbc.Col(dcc.Markdown("""
        ### Citrus Production Overview  
        Citrus species are perennial in growth habit. The most commonly cultivated species are:
        **Lime** (_Citrus aurantifolia_), **Sour Orange** (_Citrus aurantium_),
        **Pummelo** (_Citrus grandis_), **Lemon** (_Citrus limon_),
        **Citron** (_Citrus medica_), **Grapefruit** (_Citrus paradisi_),
        **Mandarin/Tangerine** (_Citrus reticulata_), **Sweet Orange** (_Citrus sinensis_).

        Present world citrus production is **98.7 million tons**, with:
        - **62% oranges**
        - **17% mandarins/tangerines**
        - **5% citrons**
        - **11% limes & lemons**
        - **5% grapefruit**
        _(Source: FAOSTAT, 2001)_
        """), width=4),
        dbc.Col(dcc.Graph(id="line-chart"), width=8),
    ]),

    # Third Row: Data Table & Scatter Plot (now with NO FILTER)
    dbc.Row([
        dbc.Col(dash_table.DataTable(id="citrus-table", style_table={'overflowX': 'auto'}), width=4),
        dbc.Col(dcc.Graph(figure=px.scatter(
            df_country_citrus_fao, x="Year", y="Value", color="Item", facet_col="continent",
            title="Citrus Production Trends by Continent (FAOSTAT)",labels={'continent': ''} 
        )), width=8),  # Static scatter plot with all data
    ]),

    # Footer
    dbc.Row([
        dbc.Col(html.P("© 2025 .danki", className="text-muted"), width=4),
        dbc.Col(html.A("📄 Documentation", href="https://docs.google.com/document/d/1f0x9qaZXy-wa4bKZs6au2fY-lXB6qcJnCIQtESa0maU/edit?usp=drive_link", target="_blank"), width=4),
        dbc.Col(dbc.Button("📥 Download Data", href="https://raw.githubusercontent.com/adeline-hub/light.danki/refs/heads/main/datasets/df_country_citrus_fao.csv", target="_blank"), width=4),
    ], className="mt-4 text-center"),

], fluid=True)

# Callbacks
@app.callback(
    Output("geo-scatter", "figure"),
    [Input("item-filter", "value"),
     Input("year-filter", "value")]
)
def update_geo_chart(selected_item, selected_year):
    filtered_df = df if selected_item == "All" else df[df["Item"] == selected_item]
    filtered_df = filtered_df[filtered_df["Year"] == selected_year]

    fig = px.scatter_geo(
        filtered_df, locations="iso_alpha_3", color="Item", hover_name="Area", size="Value",
        size_max=50, projection="eckert4", title="Distribution of Citrus Production (FAOSTAT)"
    )
    return fig

@app.callback(
    Output("line-chart", "figure"),
    [Input("item-filter", "value")]
)
def update_line_chart(selected_item):
    filtered_df = df_grouped if selected_item == "All" else df_grouped[df_grouped["Item"] == selected_item]
    
    fig = px.line(
        filtered_df, x="Year", y="Value", color="Item", markers=True,
        title="Citrus Production Trends Over Years (FAOSTAT)"
    )
    fig.update_traces(marker_line_width=0.5, opacity=0.6)
    return fig

@app.callback(
    [Output("citrus-table", "data"), Output("citrus-table", "columns")],
    [Input("year-filter", "value")]
)
def update_table(selected_year):
    df_summary = df[df["Year"] == selected_year].groupby("Item", as_index=False)["Value"].sum()
    
    # Rename columns
    df_summary = df_summary.rename(columns={"Item": "Citrus Type", "Value": "Production in Tons"})
    
    columns = [{"name": col, "id": col} for col in df_summary.columns]
    return df_summary.to_dict("records"), columns

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
    
server = app.server
