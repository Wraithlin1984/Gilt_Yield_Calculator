#calculate the accrued coupon from a cashflow schedule
#vibecoding with CoPilot

from datetime import datetime
import polars as pl

def calculate_accrued_actact(df: pl.DataFrame, today: datetime = None) -> float:
    if today is None:
        today = datetime.today()

    dates = df['date'].to_list()
    past = [d for d in dates if d < today]
    future = [d for d in dates if d > today]

    if not past  or not future:
        raise ValueError("Cashflow Datafroma must contain a 'date' column with at least one date in the past and one in the future")

    last = max(past)
    next_ = min(future)
    last_cashflow = df.filter(pl.col("date") == last)["cashflow"][0]

    fraction = (today-last).days/(next_-last).days
    accrued = last_cashflow*fraction

    print(f"Days since last cashflow: {(today-last).days} days")
    print(f"Days to next cashflow: {(next_-today).days} days")

    return round(accrued, 3)
