from pathlib import Path

import numpy as np
import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from plotly.subplots import make_subplots

# ---------------------------------------------------------
# 1. Leitura do CSV para um DataFrame
# ---------------------------------------------------------
PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_PROJETO / "ecommerce_estatistica.csv"

df = pd.read_csv(CAMINHO_CSV)

# Converte as colunas usadas nas análises para números.
for coluna in ["Nota", "N_Avaliações", "Desconto", "Preço"]:
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

# Converte as faixas de quantidade vendida em valores aproximados,
# seguindo o mapeamento utilizado no notebook de análise.
mapa_vendas = {
    "+100": 100,
    "+1000": 1000,
    "+10mil": 10000,
    "+50mil": 50000,
    "+100mil": 100000,
    "+500mil": 500000,
    "+1milhão": 1000000,
}
df["Vendas_Aproximadas"] = (
    df["Qtd_Vendidos"].astype(str).str.strip().map(mapa_vendas)
)

# ---------------------------------------------------------
# 2. Indicadores gerais
# ---------------------------------------------------------
preco_medio = df["Preço"].mean()
nota_media = df["Nota"].mean()
desconto_medio = df["Desconto"].mean()
total_produtos = len(df)

def formatar_numero(valor, casas=2):
    if pd.isna(valor):
        return "—"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def cartao_indicador(titulo, valor):
    return html.Div(
        [
            html.P(titulo, className="kpi-titulo"),
            html.H2(valor, className="kpi-valor"),
        ],
        className="kpi-card",
    )

# ---------------------------------------------------------
# 3. Gráficos equivalentes aos do notebook
# ---------------------------------------------------------

# Histograma: distribuição dos preços.
fig_hist = px.histogram(
    df, x="Preço", nbins=20, marginal="rug",
    title="Distribuição dos Preços dos Produtos",
    labels={"Preço": "Preço (R$)", "count": "Quantidade de produtos"},
    color_discrete_sequence=["#3977d5"],
)
fig_hist.update_layout(yaxis_title="Quantidade de produtos")

# Dispersão: preço x nota.
fig_disp = px.scatter(
    df, x="Preço", y="Nota", opacity=0.7,
    title="Relação entre Preço e Nota dos Produtos",
    labels={"Preço": "Preço (R$)", "Nota": "Nota média"},
    hover_data=["Título", "Marca"],
    color_discrete_sequence=["#13a89e"],
)

# Heatmap: correlação entre variáveis numéricas.
colunas_correlacao = [
    "Nota", "N_Avaliações", "Desconto", "Preço", "Vendas_Aproximadas"
]
matriz_correlacao = df[colunas_correlacao].corr()
fig_heat = go.Figure(
    data=go.Heatmap(
        z=matriz_correlacao.values,
        x=matriz_correlacao.columns,
        y=matriz_correlacao.index,
        zmin=-1, zmax=1, colorscale="RdBu",
        reversescale=True, text=np.round(matriz_correlacao.values, 2),
        texttemplate="%{text:.2f}", colorbar_title="Correlação",
    )
)
fig_heat.update_layout(title="Mapa de Calor - Correlação entre Variáveis")

# Barras: 10 marcas com mais produtos.
top_marcas = df["Marca"].value_counts().head(10).sort_values()
fig_barras = px.bar(
    x=top_marcas.values, y=top_marcas.index, orientation="h",
    title="Top 10 Marcas com Mais Produtos na Base",
    labels={"x": "Quantidade de produtos", "y": "Marca"},
    color_discrete_sequence=["#24966d"],
)

# Pizza: distribuição por gênero.
generos = df["Gênero"].fillna("Não informado").value_counts()
fig_pizza = px.pie(
    names=generos.index, values=generos.values, hole=0.25,
    title="Distribuição dos Produtos por Gênero",
)

# Densidade: estimativa KDE, equivalente ao kdeplot do notebook.
precos_validos = df["Preço"].dropna()
fig_densidade = go.Figure()
if len(precos_validos) > 1 and precos_validos.nunique() > 1:
    eixo_x = np.linspace(precos_validos.min(), precos_validos.max(), 250)
    estimador = gaussian_kde(precos_validos)
    eixo_y = estimador(eixo_x)
    fig_densidade.add_trace(go.Scatter(
        x=eixo_x, y=eixo_y, mode="lines",
        fill="tozeroy", name="Densidade",
        line={"color": "#8a55bd", "width": 3}
    ))
    fig_densidade.update_layout(
        title="Densidade da Distribuição dos Preços",
        xaxis_title="Preço (R$)", yaxis_title="Densidade"
    )
else:
    fig_densidade.add_annotation(
        text="Dados insuficientes para calcular a densidade.",
        x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False
    )
    fig_densidade.update_layout(title="Densidade da Distribuição dos Preços")

# Regressão: nota em relação ao logaritmo do número de avaliações.
dados_reg = df[["N_Avaliações", "Nota"]].dropna().copy()
dados_reg = dados_reg[dados_reg["N_Avaliações"] >= 0]
dados_reg["Log_Avaliações"] = np.log1p(dados_reg["N_Avaliações"])
fig_reg = px.scatter(
    dados_reg, x="Log_Avaliações", y="Nota", opacity=0.5,
    title="Regressão: Nota em Relação ao Número de Avaliações",
    labels={
        "Log_Avaliações": "Logaritmo do número de avaliações (log1p)",
        "Nota": "Nota média",
    },
    color_discrete_sequence=["#3977d5"],
)
if len(dados_reg) >= 2 and dados_reg["Log_Avaliações"].nunique() > 1:
    coef = np.polyfit(dados_reg["Log_Avaliações"], dados_reg["Nota"], 1)
    x_linha = np.linspace(dados_reg["Log_Avaliações"].min(),
                          dados_reg["Log_Avaliações"].max(), 100)
    y_linha = np.polyval(coef, x_linha)
    fig_reg.add_trace(go.Scatter(
        x=x_linha, y=y_linha, mode="lines",
        name="Linha de tendência", line={"color": "red", "width": 3}
    ))

# Aparência consistente e responsiva.
graficos = [fig_hist, fig_disp, fig_heat, fig_barras, fig_pizza, fig_densidade, fig_reg]
for figura in graficos:
    figura.update_layout(
        template="plotly_white",
        font={"family": "Arial, sans-serif", "color": "#263445"},
        title={"x": 0.03, "xanchor": "left"},
        margin={"l": 45, "r": 25, "t": 75, "b": 45},
        height=420,
    )

# ---------------------------------------------------------
# 4. Aplicação Dash
# ---------------------------------------------------------
app = Dash(__name__)
server = app.server
app.title = "Dashboard | Análise de E-commerce"

app.layout = html.Div(
    [
        html.Header(
            [
                html.Div("PAINEL DE DADOS", className="eyebrow"),
                html.H1("Análise Estatística de E-commerce"),
                html.P(
                    "Explore os indicadores e gráficos da base de produtos "
                    "em uma única tela."
                ),
            ],
            className="topo",
        ),
        html.Main(
            [
                html.Section(
                    [
                        cartao_indicador("Produtos analisados", formatar_numero(total_produtos, 0)),
                        cartao_indicador("Preço médio", f"R$ {formatar_numero(preco_medio)}"),
                        cartao_indicador("Nota média", formatar_numero(nota_media)),
                        cartao_indicador("Desconto médio", f"{formatar_numero(desconto_medio)}%"),
                    ],
                    className="kpi-grid",
                ),
                html.Div(
                    [
                        html.Div(
                            [html.H3("Distribuição dos preços"), dcc.Graph(figure=fig_hist, config={"displayModeBar": True})],
                            className="grafico-card",
                        ),
                        html.Div(
                            [html.H3("Preço e avaliação"), dcc.Graph(figure=fig_disp, config={"displayModeBar": True})],
                            className="grafico-card",
                        ),
                        html.Div(
                            [html.H3("Correlação entre variáveis"), dcc.Graph(figure=fig_heat, config={"displayModeBar": True})],
                            className="grafico-card",
                        ),
                        html.Div(
                            [html.H3("Marcas mais presentes"), dcc.Graph(figure=fig_barras, config={"displayModeBar": True})],
                            className="grafico-card",
                        ),
                        html.Div(
                            [html.H3("Produtos por gênero"), dcc.Graph(figure=fig_pizza, config={"displayModeBar": True})],
                            className="grafico-card",
                        ),
                        html.Div(
                            [html.H3("Densidade dos preços"), dcc.Graph(figure=fig_densidade, config={"displayModeBar": True})],
                            className="grafico-card",
                        ),
                        html.Div(
                            [html.H3("Tendência: avaliações e nota"), dcc.Graph(figure=fig_reg, config={"displayModeBar": True})],
                            className="grafico-card grafico-largo",
                        ),
                    ],
                    className="graficos-grid",
                ),
                html.Footer(
                    "Projeto acadêmico • Dados carregados de ecommerce_estatistica.csv",
                    className="rodape",
                ),
            ],
            className="conteudo",
        ),
    ]
)

if __name__ == "__main__":
    # Acesse http://127.0.0.1:8050 no navegador.
    app.run(debug=True)
