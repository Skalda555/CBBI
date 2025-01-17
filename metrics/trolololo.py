from typing import List

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression

from utils import add_common_markers
from .base_metric import BaseMetric


class TrolololoMetric(BaseMetric):
    @property
    def name(self) -> str:
        return 'Trolololo'

    @property
    def description(self) -> str:
        return 'Bitcoin Trolololo Trend Line'

    def calculate(self, df: pd.DataFrame, ax: List[plt.Axes]) -> pd.Series:
        begin_date = pd.to_datetime('2012-01-01')

        df['TroloDaysSinceBegin'] = (df['Date'] - begin_date).dt.days

        df['TroloTopPrice'] = np.power(10, 2.900 * np.log(df['TroloDaysSinceBegin'] + 1400) - 19.463)  # Maximum Bubble Territory
        df['TroloTopPriceLog'] = np.log(df['TroloTopPrice'])
        df['TroloBottomPrice'] = np.power(10, 2.788 * np.log(df['TroloDaysSinceBegin'] + 1200) - 19.463)  # Basically a Fire Sale
        df['TroloBottomPriceLog'] = np.log(df['TroloBottomPrice'])

        df['TroloDifference'] = df['TroloTopPriceLog'] - df['TroloBottomPriceLog']
        df['TroloOvershootActual'] = df['PriceLog'] - df['TroloTopPriceLog']
        df['TroloUndershootActual'] = df['TroloBottomPriceLog'] - df['PriceLog']

        high_rows = df.loc[(df['PriceHigh'] == 1) & (df['Date'] >= begin_date)]
        high_x = high_rows.index.values.reshape(-1, 1)
        high_y = high_rows['TroloOvershootActual'].values.reshape(-1, 1)
        high_y[0] *= 0.6  # the first value seems too high

        low_rows = df.loc[(df['PriceLow'] == 1) & (df['Date'] >= begin_date)]
        low_x = low_rows.index.values.reshape(-1, 1)
        low_y = low_rows['TroloUndershootActual'].values.reshape(-1, 1)

        x = df.index.values.reshape(-1, 1)

        lin_model = LinearRegression()
        lin_model.fit(high_x, high_y)
        df['TroloOvershootModel'] = lin_model.predict(x)

        lin_model.fit(low_x, low_y)
        df['TroloUndershootModel'] = lin_model.predict(x)

        df['TroloIndex'] = (df['PriceLog'] - df['TroloBottomPriceLog'] + df['TroloUndershootModel']) / \
                           (df['TroloOvershootModel'] + df['TroloDifference'] + df['TroloUndershootModel'])

        ax[0].set_title(self.description)
        sns.lineplot(data=df, x='Date', y='TroloIndex', ax=ax[0])
        add_common_markers(df, ax[0])

        return df['TroloIndex']
