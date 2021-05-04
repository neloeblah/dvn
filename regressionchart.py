import re
import numpy as np
import pandas as pd
import plotly.express as px

from sklearn.linear_model import LassoCV

# Import data
df_new = pd.read_csv("happy/world-happiness-report-2021.csv")
df_hist = pd.read_csv("happy/world-happiness-report.csv")

# Add regional indicator to historical file
df_merged = pd.merge(df_hist, df_new[["Country name", "Regional indicator"]], how="left", on="Country name")


# Common columns from historical data
cols_hist = ["Country name", "year", "Life Ladder", "Log GDP per capita", "Social support", 
             "Healthy life expectancy at birth", "Freedom to make life choices", "Generosity", 
             "Perceptions of corruption", "Regional indicator"]

# Amend new data to match old format and merge
df_new["year"] = 2021
cols_new = ["Country name", "year", "Ladder score", "Logged GDP per capita", "Social support", 
            "Healthy life expectancy", "Freedom to make life choices", "Generosity", "Perceptions of corruption", 
            "Regional indicator"]

df_new_filtered = df_new[cols_new]
df_new_filtered.columns = cols_hist

df_final = pd.concat([df_merged[cols_hist], df_new_filtered])
df_final = df_final.reset_index(drop=True)


##### Regressions

years = df_final["year"].unique()
years = np.sort(years)[1:]  # remove 2005, not enough data

# Create dictionary where keys = years, values = feature importance
feature_importance = {}

x_cols = ["Log GDP per capita", "Social support", "Healthy life expectancy at birth", "Freedom to make life choices", 
                "Generosity", "Perceptions of corruption"]
for year in years:
    #filter year
    mask = df_final["year"] == year
    tmp_df = df_final.loc[mask].dropna()

    #split target-predictors
    y = tmp_df["Life Ladder"]
    X = tmp_df[x_cols]
    X = sm.add_constant(X) 

    #fit model
    reg = LassoCV()
    reg.fit(X, y)
    
    #extract coefficients
    coef = pd.Series(reg.coef_, index = X.columns)
    imp_coef = coef.sort_values()
    
    feature_importance[year] = imp_coef
    
    
# Convert to dataframe 
feat_df = pd.DataFrame(feature_importance)

# Remove constant and change to absolute (not concerned with direction, just size)
ranks = abs(feat_df.loc[feat_df.index != "const"])
ranks = pd.melt(ranks.reset_index(), id_vars="index", value_vars=years)

# Shorten names for plot
new_names = ["GDP", "Social Support", "Life Expectancy", "Freedom", "Generosity", "Corruption"]
labels = dict(zip(x_cols, new_names))
ranks["index"] = ranks["index"].map(labels)

# Color map 
colors = px.colors.qualitative.Set1[0:2] + px.colors.qualitative.Pastel1[2:4] +  px.colors.qualitative.Pastel1[6:8]
color_map = {}
for k,v in zip(labels.values(), colors):
    color_map[k] = v

# Chart
fig = go.Figure()

annotations = []
for i in ranks["index"].unique():
    # plot individual features
    tmp = ranks.loc[ranks["index"] == i]
    fig.add_trace(go.Scatter(x=tmp["variable"], y=tmp["value"], name=i, 
                             line=dict(color=color_map[i], width=size_map[i]))) 
    
    # attach label
    y = tmp.loc[tmp["variable"] == 2021, "value"]
    annotations.append(dict(xref='paper', x=0.95, y=y.values[0],
                                  xanchor='left', yanchor='middle',
                                  text='{}'.format(i),
                                  font=dict(family='Calibri Black',
                                            size=16, 
                                           color=color_map[i]),
                                  showarrow=False))

# add caption
annotations.append(dict(xref='paper', yref='paper', x=0.95, y=-0.2,
                        text="Feature Importance Scores calculated from Lasso Regression",
                        font=dict(family='Calibri',
                                            size=12, 
                                           color="black"),
                        showarrow=False))

# Formatting
fig.update_layout(height=600, width=950, yaxis_title="Importance Score", xaxis_title="Year", showlegend=False, plot_bgcolor="#FFFFFF", margin_b=90,
                  title={'text': "Prioritising Social Environment for Wellbeing", 
                         'x':0, 
                         'font': dict(size=20), 
                         'xanchor': 'left', 
                         'yanchor': 'top'}, 
                  annotations=annotations
                  )
fig.update_xaxes(showline=True, linewidth=1, linecolor="slategrey")
fig.show()
