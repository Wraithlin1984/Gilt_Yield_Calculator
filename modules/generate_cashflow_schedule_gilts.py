#Generate a date,payment cashflow schedule from today until maturity
#vibecoding with CoPilot
from calendar import weekday
from datetime import datetime, timedelta
import polars as pl
import os

def generate_cashflow_schedule_gilts(maturity_date: datetime, coupon: float) -> pl.DataFrame:
    today = datetime.today()
    cutoff_date = today - timedelta(days=365)
    cashflow_dates = []

    #Gilts have semi-annual cashflows
    current = maturity_date
    day = maturity_date.day
    month = maturity_date.month
    year = maturity_date.year

    #Generate pseudo payment dates from final maturity in reverse
    while current >= cutoff_date:
        #Bump weekends to the next Mondays
        ## This should check for public holidays, but that requires a calendar
        day_index = current.weekday()
        if day_index >4:
            current = current + timedelta(days=(7-day_index))

        cashflow_dates.append(current)

        #No fixed increment to the prior cashflow so calendar convention is most robust
        if (month-6)<0:
            year-= 1
        month = (month - 6) % 12
        current = datetime(year, month ,day)
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