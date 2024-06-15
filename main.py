import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from haversine import haversine

df = pd.read_csv("nyc-taxi-trip-duration/train.csv")
df["haversine"] = df.apply(lambda x: haversine((x["pickup_latitude"], x["pickup_longitude"]), (x["dropoff_latitude"], x["dropoff_longitude"]), unit="km"), axis=1)
df["mean_speed"] = df["haversine"] / (df["trip_duration"] / (60 * 60))
df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
df["pickup_weekday"] = df["pickup_datetime"].dt.weekday
df["pickup_hour"] = df["pickup_datetime"].dt.hour

median_speed = df.groupby(["pickup_weekday", "pickup_hour"])["mean_speed"].median().reset_index()
pivot_table = median_speed.pivot_table(index="pickup_weekday", columns="pickup_hour", values="mean_speed")
weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
pivot_table.index = pivot_table.index.map(weekday_map)

app = dash.Dash(__name__)

app.layout = html.Div([html.H1("Median Speed by Weekday and Hour"), dcc.Graph(id="heatmap-graph"), html.P("Generated heatmap showing median speed")])


@app.callback(Output("heatmap-graph", "figure"), [Input("heatmap-graph", "id")])
def update_graph(graph_id):
    fig = px.imshow(pivot_table, text_auto=True, labels=dict(x="Hour", y="Weekday", color="Median Speed"), x=pivot_table.columns, y=pivot_table.index)
    fig.update_layout(title="Median Speed by Weekday and Hour", xaxis_title="Hour", yaxis_title="Weekday")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
  
