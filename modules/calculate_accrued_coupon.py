#Calculate the accrued coupon from a cashflow schedule
#vibecoding with CoPilot

from datetime import datetime
import polars as pl

def calculate_accrued_actact(df: pl.DataFrame, today: datetime = None) -> tuple[float, float]:
    """
    Calculate the accrued coupon for a bond using the actual/actual convention.
    pl.DataFrame contains ['date'] in chronological order
    Optional today: Specify a transaction date
    Returns: Accrued_amount and accrued_time (fraction of  a coupon)
    """
    if 'date' not in df.columns or 'cashflow' not in df.columns:
        raise ValueError("Input DataFrame must contain 'date' and 'cashflow' columns")
    if today is None:
        today = datetime.today()

    past = df.filter(pl.col("date") <= today)
    future = df.filter(pl.col("date") > today)

    if past.is_empty() or future.is_empty():
        raise ValueError("Cashflow DataFrame must contain dates both before and after 'Today'")

    last = past.select(pl.col("date").max()).item()
    next_ = future.select(pl.col("date").min()).item()
    if (next_ - last).days <1:
        raise ValueError("Invalid cashflow schedule: consecutive dates are identical")

    last_cashflow = df.filter(pl.col("date") == last).select("cashflow").item()

    fraction = (today-last).days/(next_-last).days
    accrued = last_cashflow*fraction

    print(f"Days since last cashflow: {(today-last).days} days")
    print(f"Days to next cashflow: {(next_-today).days} days")

    return round(accrued, 3), fraction
