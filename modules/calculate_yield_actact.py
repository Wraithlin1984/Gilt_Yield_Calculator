#Calculate the yield on a fixed income instrument given the price and cashflow schedule
#vibecoding with CoPilot
import polars as pl
from datetime import datetime
from polars.exceptions import ColumnNotFoundError

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
    #Validate input
    required_cols = {"date", "cashflow"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    #Ensure "Date" is datetime
    df = df.with_columns(pl.col('date').cast(pl.Datetime))

    #Remove any cashflows in the past
    today = datetime.today()
    df_future = df.filter(pl.col('date') > today)
    if df_future.is_empty():
        raise ValueError("There are no dates in the future")

    #calculate discount periods as periods (coupons)
    np = df_future.shape[0]
    discount_periods = [fraction + i for i in range(np)]

    df_future = df_future.with_columns([
        pl.Series('discount_period', discount_periods)
     ])

    #Target present value
    target_pv = clean_price + accrued

    #Iterative solver (Newton-Rhapson fallback to bisection)
    def present_value(rate: float) -> float:
        try:
            return df_future.select (
                (pl.col('cashflow')/(1+rate/coupon_freq)**pl.col('discount_period')).sum()
            ).item()
        except ZeroDivisionError:
            raise ValueError("Invalid rate encountered during PV calculation")

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