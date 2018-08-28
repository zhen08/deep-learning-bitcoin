import matplotlib
import copy

matplotlib.use('Agg')

def compute_returns(p):
    close_prices = p['price_close']
    close_prices_returns = 100 * ((close_prices.shift(-1) - close_prices) / close_prices).fillna(0.0)
    return close_prices_returns.shift(1).fillna(0)


def plot_p(df):
    import matplotlib.pyplot as plt
    import mpl_finance
    fig, ax = plt.subplots()
    df_nor = normalize(df)
    mpl_finance.candlestick2_ohlc(ax,
                      opens=df_nor['price_open'].values,
                      highs=df_nor['price_high'].values,
                      lows=df_nor['price_low'].values,
                      closes=df_nor['price_close'].values,
                      width=0.6,
                      colorup='g',
                      colordown='r',
                      alpha=1)
    plt.show()
    print('Done.')

def normalize(df):
    result = df.copy()
    max_value = df['price_high'].max()
    min_value = df['price_low'].min()
    for feature_name in df.columns:
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result

def draw_candle(df,ax):
    import mpl_finance
    ax.axis('off')
    df_nor = normalize(df)
    mpl_finance.candlestick2_ohlc(ax,
                      opens=df_nor['price_open'].values,
                      highs=df_nor['price_high'].values,
                      lows=df_nor['price_low'].values,
                      closes=df_nor['price_close'].values,
                      width=1.0,
                      colorup='g',
                      colordown='r',
                      alpha=1)


def save_to_file(df1, df2, df3, df4, filename):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(nrows=2, ncols=2)

    draw_candle(df1, ax[0,0])
    draw_candle(df2, ax[0,1])
    draw_candle(df3, ax[1,0])
    draw_candle(df4, ax[1,1])

    plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)


def mkdir_p(path):
    import os
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
