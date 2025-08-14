#Generate a date,payment cashflow schedule from today until maturity
#vibecoding with CoPilot

from datetime import datetime, timedelta
import polars as pl
import os

def generate_cashflow_schedule_gilts(maturity_date: datetime, coupon: float) -> pl.DataFrame:
    today = datetime.today()
    cutoff_date = today - timedelta(days=365)
    cashflow_dates = []

    #Gilts have semi-annual cashflows
    current = maturity_date
    step_days = [183,182]       #Alternating steps as 1 year is 365
    step_index = 0

    #Generate pseudo payment dates from final maturity in reverse
    while current >= cutoff_date:
            cashflow_dates.append(current)
            current -= timedelta(days=step_days[step_index])
            step_index = 1- step_index
    cashflow_dates.sort()       #Dates in chronological order

    #Generate payment amounts
    cashflows = [coupon/2]*len(cashflow_dates)
    if cashflows:
        cashflows[-1] += 100

    df = pl.DataFrame({
        'date':cashflow_dates,
        'cashflow':cashflows
    })

    #Save this down
    folder="Gilt_Schedules"
    filename = f"UKT-{coupon: .4f}-{maturity_date.strftime('%m%Y')}.json"
    filepath = os.path.join(folder, filename)

    if not os.path.exists(filepath):
        os.makedirs(folder, exist_ok=True)
        df.write_json(filepath)

    return df