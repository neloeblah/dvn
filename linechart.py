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


##### Line chart - Australia vs USA

# Filter data
df_aus_us = df_final.loc[df_final["Country name"].isin(["Australia", "United States"])]
df_aus_us.sort_values(["Country name", "year"])

colors_dark = ["#4FD9A1", "#B22222"]
colors = ['rgba(79, 217, 161, 0.5)', 'rgba(178, 34, 34, 0.5)']

# Plot lines
fig = px.line(df_aus_us, x="year", y="Life Ladder", color="Country name", color_discrete_sequence=colors)

# Highlight COVID-19 year
fig.add_vrect(x0=2020, x1=2021, line_width=0, fillcolor="#78C9F1", annotation_text="COVID", 
              annotation_position="top left", opacity=0.2)

# Arrows 
fig.add_annotation(x=2021, y=7.15, ax=2020, ay=7.1, xref='x', yref='y', axref='x', ayref='y', 
                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor=colors_dark[0])
fig.add_annotation(x=2021, y=6.99, ax=2020, ay=7.06, xref='x', yref='y', axref='x', ayref='y', 
                   showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor=colors_dark[1])

# Country Labels
fig.add_annotation(x=2021.8, y= 7.20, text="Australia", showarrow=False, 
                   font=dict(family="Calibri Black", color=colors_dark[0], size=16))
fig.add_annotation(x=2022, y= 6.94, text="United States", showarrow=False, 
                   font=dict(family="Calibri Black", color=colors_dark[1], size=16))

# Formatting
fig.update_xaxes(range=[2005, 2022])
fig.update_layout(yaxis_title="Happiness Score", xaxis_title="Year", showlegend=False, plot_bgcolor="#FFFFFF", 
                  title={'text': "Different COVID-19 Responses",
                         'x':0,
                         'font': dict(size=20),
                         'xanchor': 'left',
                         'yanchor': 'top'})
fig.show()

