import re
import numpy as np
import pandas as pd
import plotly.express as px

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

# Suicide Data
sr_file = "suicide_data.csv"
sr_df = pd.read_csv(sr_file)

# Fix formatting
column_names = sr_df.iloc[0]
sr_df = sr_df.iloc[1:]
sr_df.columns = column_names 
sr_df.set_index(["Country", "Sex"], inplace=True)
sr_df = sr_df.replace(" \[[0-9.-]+\]", "", regex=True).astype(float)
sr_df = sr_df.reset_index()

# Filter current data, totals only
sr_current = sr_df.loc[sr_df["Sex"] == "Both sexes", ["Country", "2019"]]

# Adjust for different country name formats
country_dict = {"Bolivia (Plurinational State of)": "Bolivia", "Czechia": "Czech Republic", "Democratic Republic of the Congo": "Congo (Kinshasa)", 
                "Congo": "Congo (Brazzaville)", "Iran (Islamic Republic of)": "Iran", "Côte d'Ivoire": "Ivory Coast", "Lao People's Democratic Republic": "Laos",
                "Republic of Moldova": "Moldova", "Russian Federation": "Russia", "Republic of Korea": "South Korea", "Syrian Arab Republic": "Syria",
                "United Kingdom of Great Britain and Northern Ireland": "United Kingdom", "United Republic of Tanzania": "Tanzania", 
                "United States of America": "United States", "Venezuela (Bolivarian Republic of)": "Venezuela", "Viet Nam": "Vietnam"}
sr_current["Country"] = sr_current["Country"].replace(country_dict)

# Get corresponding year from happiness data and merge
happy_df = df_final.loc[df_final["year"] == 2019, ["Country name", "Life Ladder", "Regional indicator", "Log GDP per capita"]]
happy_df.rename(columns={"Country name": "Country"}, inplace=True)

happy_sr = pd.merge(happy_df, sr_current, how="inner", on="Country")
happy_sr.rename(columns={"2019": "Suicide Rates"}, inplace=True)
happy_sr = happy_sr.loc[happy_sr["Country"] != "Lesotho"].dropna() # remove outlier
happy_sr["Log GDP per capita"] = np.exp(happy_sr["Log GDP per capita"])

# Color mapping
colors = px.colors.qualitative.Set1[0:2] + px.colors.qualitative.Pastel1[2:9] + px.colors.qualitative.Pastel2[0:2]
regions = happy_sr["Regional indicator"].unique()

color_map = {}
color_map["North America and ANZ"] = colors[0]
color_map["Western Europe"] = colors[1]

for color, region in zip(colors[2:], regions[~np.isin(regions, ["Western Europe", "North America and ANZ"])]):
    color_map[region] = color

# Plot
fig = px.scatter(happy_sr, x="Life Ladder", y="Suicide Rates", color="Regional indicator", size="Log GDP per capita",
                color_discrete_map=color_map)

# Annotations
annotations = []

# subtitle
annotations.append(dict(xref='paper', yref='paper', x=-0.10, y=1.03, text="Sized by GDP", font=dict(size=12, color="black"), showarrow=False)) 
    
# highlight Australia
x = happy_sr.loc[happy_sr["Country"] == "Australia", "Life Ladder"].values[0]
y = happy_sr.loc[happy_sr["Country"] == "Australia", "Suicide Rates"].values[0]
annotations.append(dict(x=x, y=y, ax=x+30, ay=y+50, text="Australia", font=dict(color="white"), 
                        showarrow=True, arrowwidth=2, arrowhead=2, bgcolor=colors[0], opacity=0.8))

# description
annotations.append(dict(xref='paper', yref='paper', x=0.05, y=0.82, text="Wealthy, happy countries are positively correlated across",
                        font=dict(color="black"), showarrow=False))
annotations.append(dict(xref='paper', yref='paper', x=0.07, y=0.79, text="<b>Western Europe", font=dict(color=colors[1]), showarrow=False))
annotations.append(dict(xref='paper', yref='paper', x=0.21, y=0.79, text="&", font=dict(color="black"), showarrow=False))
annotations.append(dict(xref='paper', yref='paper', x=0.225, y=0.79, text="<b>North America and ANZ", font=dict(color=colors[0]), showarrow=False))

# Formatting
fig.update_layout(height=600, width=950, xaxis_title="Happiness Score", showlegend=False, annotations=annotations, plot_bgcolor="#FFFFFF", 
                  title={
                        'text': "Suicide Prediction is Complex",
                        'x':0,
                        'font': dict(size=20),
                        'xanchor': 'left',
                        'yanchor': 'top'})
fig.update_xaxes(showline=True, linewidth=1, linecolor="slategrey")
fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="#EAF2F2")

fig.show()
