#Generate a date,payment cashflow schedule from today until maturity
#vibecoding with CoPilot

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import polars as pl
import os

def generate_cashflow_schedule_gilts(maturity_date: datetime, coupon: float) -> pl.DataFrame:
    today = datetime.today()
    cutoff_date = today - timedelta(days=365)
    cashflow_dates = []

    #Gilts have semi-annual cashflows
    current = maturity_date

    #Generate pseudo payment dates from final maturity in reverse order
    while current >= cutoff_date:
        cashflow_dates.append(current)

        #No fixed increment to the prior cashflow so calendar convention is most robust
        current -= relativedelta(months=6)
    cashflow_dates.sort()       #Dates in chronological order. Generally faster than building in order with prepends

    #Generate payment amounts
    if not cashflow_dates:
            return  ValueError('Unknown error building cashflow schedule')
    cashflows = [coupon/2]*len(cashflow_dates)          #All gilts are semi-annual
    cashflows[-1] += 100                                #Add principal

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