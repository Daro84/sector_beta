'''index_list = ['WIG_BANKI','WIG_BUDOW','WIG_CHEMIA','WIG_ENERG','WIG_GORNIC','WIG_INFO','WIG_LEKI','WIG_MEDIA',
              'WIG_MOTO','WIG_NRCHOM','WIG_ODZIEZ','WIG_PALIWA','WIG_SPOZYW','WIG_TELKOM']'''

index_list = ['WIG_BANKI','WIG_BUDOW','WIG_LEKI']

days_nb = 250
benchmark = 'WIG'

from flask import Flask, render_template
import pandas
import numpy as np

app = Flask(__name__)

@app.route('/')
def home():
    b_df = pandas.read_csv('https://stooq.pl/q/d/l/?s=' + benchmark + '&i=d')
    b_df = b_df[-days_nb:]
    date_start = b_df.iloc[0]['Data']
    date_end = b_df.iloc[-1]['Data']

    benchmark_returns = []
    for d in range(1, days_nb):
        benchmark_ret = b_df.iloc[d]['Zamkniecie'] / b_df.iloc[d - 1]['Zamkniecie']
        benchmark_returns.append(benchmark_ret)

    index_nb = 0
    data_summary = []

    for i in index_list:
        df = pandas.read_csv('https://stooq.pl/q/d/l/?s=' + i + '&i=d')
        df['Data'] = pandas.to_datetime(df['Data'])
        df = df[-days_nb:]
        first_value = df.iloc[0]['Zamkniecie']
        last_value = df.iloc[-1]['Zamkniecie']

        # compute daily returns for each ticker
        index_returns = []
        for d in range(1, days_nb):
            ticker_ret = df.iloc[d]['Zamkniecie'] / df.iloc[d - 1]['Zamkniecie']
            index_returns.append(ticker_ret)

        # compute rate of return, standard deviation, covariance and beta coefficient
        rate_return = round(100 * ((last_value / first_value) - 1), 2)
        sd = round((np.std(index_returns) * 100), 2)
        a = np.array([index_returns, benchmark_returns])
        cov = np.cov(a)[0][1]
        benchmark_var = (np.std(benchmark_returns)) ** 2
        beta = round(cov / benchmark_var, 2)

        # create list of dictionaries with data to render results template
        i_data = dict(index=i, last_value=last_value, rate_return=rate_return, sd=sd, beta=beta)
        data_summary.append(i_data)
        index_nb+=1

    return render_template('home.html',
                           data_summary=data_summary,
                           date_start=date_start,
                           date_end=date_end
                           )

if __name__ == '__main__':
    app.run(debug=True)