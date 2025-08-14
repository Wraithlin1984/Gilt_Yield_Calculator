#Calculate the yield on a fixed income instrument given the price and cashflow schedule
#vibecoding with CoPilot
from dbm import error
from operator import itemgetter
from pydoc import resolve

import polars as pl
from datetime import datetime
from typing import Union

from polars.polars import ColumnNotFoundError


def calculate_yield_actact(
        df: pl.DataFrame,
        clean_price: float,
        accrued: float,
        coupon_freq: int =2,
        max_iterations: int =100,
        tolerance: float = 1e-4
)   -> float:

    """
    Calculate the yield on a fixed income security using act/act
    Parameters:
    - df:   Polars DataFrame with colums ['date','cashflow']
    - clean_price: Market price
    - accrued: Accrued interest
    - coupon_freq: Coupon frequency
    - max_iteractions: Maximum number of iterations for convergence
    - tolerance: Tolerance for convergence

    Returns:
    - discount_date: Yield to maturity (float, 4 dp)

    """

    today = datetime.today()

    #remove any cashflows in the past
    try:
        df = df.filter(pl.col('date') >= today)
    except ColumnNotFoundError:
        raise ValueError("There is no 'date' column")

    if df.is_empty():
        raise ValueError("There are no dates in the future")

    #calculate discount period (years)
    df = df.with_columns([
        pl.col('date').cast(pl.Datetime),
        ((pl.col('date')- pl.lit(today)).dt.total_days()/365.25).alias('discount_period')
     ])
    print(df)

    #Target present value
    target_pv = clean_price + accrued

    #Iterative solver (Newton-Rhapson fallback to bisection)
    def present_value(rate: float) -> float:
        return df.select (
            (pl.col('cashflow')/(1+rate)**pl.col('discount_period')).sum()
        ).item()

    #Bracket search
    low, high = 0.0, 0.2
    for _ in range(max_iterations):
        mid = (low+high)/2
        pv = present_value(mid)
        if abs(pv-target_pv) < tolerance:
            return round (mid,4)
        if pv > target_pv:
            low = mid
        else:
            high = mid

    raise ValueError("Yield calculation did not converge within tolerance")

