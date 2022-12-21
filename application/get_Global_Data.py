import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from application import db


def get_global_market():

    global_stocks_data = db["global_markets"].find({'index':'Nasdaq','Date':{"$gte": "2022-12-01"}}).sort([('Date', 1)])
    global_stocks_data =  pd.DataFrame(list(global_stocks_data))

    sid = "NASDAQ"

    # make sure everything is json serializable, plus use  ISO 8601 for dates
    trace = go.Candlestick(
        x=global_stocks_data['Date'].tolist(),
        open=global_stocks_data['Open'].tolist(),
        high=global_stocks_data['High'].tolist(),
        low=global_stocks_data['Low'].tolist(),
        close=global_stocks_data['Close'].tolist(),
        name="sid",
    )

    data = [trace]

    layout = {"title": sid,'xaxis': {'rangebreaks': [{'bounds': ['sat', 'mon']}], 'rangeslider': {'visible': False}}}
    fig = dict(data=data, layout=layout)

    return go.Figure(fig).to_dict()

if __name__ == '__main__':
    print(get_global_market())