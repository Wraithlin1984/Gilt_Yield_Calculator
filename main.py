#Let's make a calculator for gilt yields
#vibecoding with CoPilot

from datetime import datetime

from modules.generate_cashflow_schedule_gilts import generate_cashflow_schedule_gilts
from modules.calculate_accrued_coupon import calculate_accrued_actact


def validate_inputs(maturity_str: str, coupon_str: str, price_str: str):
    try:
        maturity = datetime.strptime(maturity_str, '%d/%m/%Y')
        if maturity < datetime.today():
            raise ValueError("Maturity date must be in the future")

        coupon = float(coupon_str)
        if coupon < 0:
            raise ValueError("Coupon must be non-negative")

        price = float(price_str)
        if price < 0:
            raise ValueError("Price must be non-negative")

        return maturity, coupon, price

    except Exception as e:
        raise ValueError(f"Invalid input: {e}")

def main():
    #maturity_str = input("Enter maturity date (dd/mm/yyyy): ")                     #Reinstate me
    #coupon_str = input("Enter coupon rate (%): ")                                  #Reinstate me
    #price_str = input("Enter clean price (% of par): ")                            #Reinstate me

    try:
        #maturity, coupon, price = validate_inputs(maturity_str, coupon_str, price_str) #Reinstate me
        maturity, coupon, price = validate_inputs("31/01/2046", "0.875", "45.11")           #Debugging/
    except ValueError as err:
        print(err)
        return

    ##Debugging
    cashflows = generate_cashflow_schedule_gilts(maturity,coupon)
    print(cashflows)                                               #Debugging
    accrued = calculate_accrued_actact(cashflows)
    print(accrued)

if __name__ == '__main__':
    main()
