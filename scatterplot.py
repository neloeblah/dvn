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


##### Scatter Plot
# Filter data
scatter_df = df_final.loc[df_final["year"].isin([2008, 2021])]
scatter_df["label"] = scatter_df["year"].astype(str)
colors = ["#DD5747", "#70A1E7"]

# Get trendlines per year
fig = px.scatter(scatter_df, x="Log GDP per capita", y="Life Ladder", color="label", facet_col="label", trendline="ols", 
                color_discrete_sequence=colors)
ols1, ols2 = fig.data[1], fig.data[3]


# Extract trendline formula and merge to main data
def ols_decomp(data):
    gradient = re.search("<br>Life Ladder = [0-9.]+", data["hovertemplate"]).group(0)
    gradient = float(gradient.replace("<br>Life Ladder = ", ""))

    constant = re.search("Log GDP per capita \+ -?[0-9.]+", data['hovertemplate']).group(0)
    constant = float(constant.replace("Log GDP per capita + ", ""))
    
    r2 = re.search("<br>R<sup>2</sup>=[0-9.]+<br>", data['hovertemplate']).group(0)
    r2 = r2.replace("<br>", "").replace("<sup>", "").replace("</sup>","")

    return(gradient, constant, r2)

grad1, const1, r2_1 = ols_decomp(ols1)
grad2, const2, r2_2 = ols_decomp(ols2)

scatter_df["ols"] = np.where(scatter_df["year"] == 2008, 
                             grad1 * scatter_df["Log GDP per capita"] + const1, 
                             grad2 * scatter_df["Log GDP per capita"] + const2)

# Re-do scatterplot with additional coloring
colors = ["#A8A9AA", "#DD5747", "#70A1E7", "#A8A9AA"]
conditions = [(scatter_df["year"] == 2008) & (scatter_df["Life Ladder"] < scatter_df["ols"]), 
              (scatter_df["year"] == 2008) & (scatter_df["Life Ladder"] >= scatter_df["ols"]), 
              (scatter_df["year"] == 2021) & (scatter_df["Life Ladder"] < scatter_df["ols"]), 
              (scatter_df["year"] == 2021) & (scatter_df["Life Ladder"] >= scatter_df["ols"])]
scatter_df["color_code"] = np.select(conditions, [0, 1, 2, 3])
scatter_df["color_code"] = scatter_df["color_code"].astype(str)


# Plot points
fig = px.scatter(scatter_df, x="Log GDP per capita", y="Life Ladder", color="color_code", facet_col="label", 
                color_discrete_sequence=colors)
# Plot trendlines
fig.add_trace(ols1, row=1, col=1) 
fig.add_trace(ols2, row=1, col=2) 


# Annotations
fig.for_each_annotation(lambda a: a.update(text=" "))
fig.add_annotation(xref="x domain", x=0.2, y=7, text="R2=" + "{:.2%}".format(float(r2_1.replace("R2=", ""))), 
                   showarrow=False, font=dict(family="Calibri Black", color=colors[1], size=14))
fig.add_annotation(xref="x domain", x=0.24, y=7.3, text="2008", showarrow=False, 
                   font=dict(family="Calibri Black", color=colors[1], size=14))
fig.add_annotation(xref="x2 domain", x=0.2, y=7, text="R2=" + "{:.2%}".format(float(r2_2.replace("R2=", ""))), 
                   showarrow=False, font=dict(family="Calibri Black", color=colors[2], size=14))
fig.add_annotation(xref="x2 domain", x=0.24, y=7.3, text="2021", showarrow=False, 
                   font=dict(family="Calibri Black", color=colors[2], size=14))
fig.add_annotation(xref="x2 domain", x=0.9, y=2.75, text="Larger deviations from the trend", showarrow=False, 
                   font=dict(family="Calibri Black", color=colors[2], size=14))
fig.add_annotation(xref="paper", x=0.5, yref="paper", y=-0.1, text="GDP per Captia", showarrow=False)
fig['layout']['xaxis']['title']['text']=''
fig['layout']['xaxis2']['title']['text']=''

# Formatting
fig.update_xaxes(showline=True, linewidth=1, linecolor="slategrey")
fig.update_layout(height=600, width=950, yaxis_title="Happiness Score", showlegend=False, plot_bgcolor="#FFFFFF",
                  title={'text': "Wellbeing is more than Wealth",
                         'x':0, 
                         'font': dict(size=20),
                         'xanchor': 'left',
                         'yanchor': 'top'})
fig.show()
