#Calculate the yield on a fixed income instrument given the price and cashflow schedule
#vibecoding with CoPilot
import polars as pl
import numpy as np
from datetime import datetime

from polars.ml.utilities import frame_to_numpy
from polars.polars import ColumnNotFoundError

def calculate_yield_actact(
        df: pl.DataFrame,
        clean_price: float,
        accrued: float,
        fraction: float,
        coupon_freq: int =2,
        max_iterations: int =100,
        tolerance: float = 1e-4
)   -> float:

    """
    Calculate the yield on a fixed income security using act/act
    Parameters:
    - df:   Polars DataFrame with columns ['date','cashflow']
    - clean_price: Market price
    - accrued: Accrued interest
    - fraction: Fraction of period to next coupon
    - the fractional period of the first coupon
    - coupon_freq: Coupon frequency
    - max_iterations: Maximum number of iterations for convergence
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

    #calculate discount periods as periods (coupons)
    period = fraction
    np = df.shape[0]
    discount_periods = [fraction + i for i in range(np)]

    df = df.with_columns([
        pl.col('date').cast(pl.Datetime),
        pl.Series('discount_period', discount_periods)
     ])

    #Target present value
    target_pv = clean_price + accrued

    #Iterative solver (Newton-Rhapson fallback to bisection)
    def present_value(rate: float) -> float:
        return df.select (
            (pl.col('cashflow')/(1+rate/coupon_freq)**pl.col('discount_period')).sum()
        ).item()

    #Bracket search
    low, high = 0.0, 1.0
    for _ in range(max_iterations):
        mid = (low+high)/2
        pv = present_value(mid)
        if abs(pv-target_pv) < tolerance:
            return round (mid,5)
        if pv > target_pv:
            low = mid
        else:
            high = mid

    raise ValueError("Yield calculation did not converge within tolerance")

