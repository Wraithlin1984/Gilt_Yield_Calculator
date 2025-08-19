#Generate a date, payment cashflow schedule for a specified gilt from one year ago until maturity
#vibecoding with CoPilot

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import polars as pl
import os

def generate_cashflow_schedule_gilts(maturity_date: datetime, coupon: float) -> pl.DataFrame:
    today = datetime.today()
    cutoff_date = today - timedelta(days=365)          #Ensure we capture the last paid coupon
    cashflow_dates = []

    #Generate payment dates from final maturity in reverse order
    current = maturity_date
    while current >= cutoff_date:
        cashflow_dates.append(current)
        current -= relativedelta(months=6)              #All gilts are semi-annual
    cashflow_dates.sort()       #Dates in chronological order. Generally faster than building in order with prepends

    #Generate payment amounts
    if not cashflow_dates:
            raise ValueError('Unknown error building cashflow schedule')
    cashflows = [coupon/2]*len(cashflow_dates)          #All gilts are semi-annual
    cashflows[-1] += 100                                #Add principal to final cashflow

    df = pl.DataFrame({
        'date':cashflow_dates,
        'cashflow':cashflows
    })

    #Save this down
    folder="Gilt_Schedules"
    filename = f"UKT-{coupon:.4f}-{maturity_date.strftime('%m%Y')}.json"
    filepath = os.path.join(folder, filename)

    os.makedirs(folder, exist_ok=True)
    if not os.path.exists(filepath):
        df.write_json(filepath)

    return df