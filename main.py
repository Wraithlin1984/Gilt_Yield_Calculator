#Let's make a calculator for gilt yields
#vibecoding with CoPilot

from datetime import datetime

from modules.generate_cashflow_schedule_gilts import generate_cashflow_schedule_gilts
from modules.calculate_accrued_coupon import calculate_accrued_actact
from modules.calculate_yield_actact import calculate_yield_actact

def validate_inputs(maturity_str: str, coupon_str: str, price_str: str) -> tuple[datetime, float, float]:
    #Validate and convert user inputs into typed values
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

    except ValueError as ve:
        raise ValueError(f"Input validation error: {ve}")
    except Exception as e:
        raise ValueError(f"Unexpected input error: {e}")

def compute_gilt_yield(
        maturity: datetime,
        coupon: float,
        price: float
) -> dict:
    ##Yield computation logic

    cashflows = generate_cashflow_schedule_gilts(maturity, coupon)
    accrued, fraction = calculate_accrued_actact(cashflows)
    yield_actact = calculate_yield_actact(
        cashflows, price, accrued, (1 - fraction),
        2, 1000, 1e-5
    )

    return {
        "yield": yield_actact,
        "accrued": accrued,
        "dirty_price": price+accrued
    }

def display_results(results: dict, price: float) -> None:
    print(f"Yield to maturity: {results['yield']*100: .3f}%")
    print(f"Accrued interest: £{results['accrued']: .3f} per £100")
    print(f"Dirty price: £{results['dirty_price']: .2f} = £{price: .2f} + £{results['accrued']: .2f}")

def main():
    maturity_str = input("Enter maturity date (dd/mm/yyyy): ")                     #Reinstate me
    coupon_str = input("Enter coupon rate (%): ")                                  #Reinstate me
    price_str = input("Enter clean price (% of par): ")                            #Reinstate me

    #TestValues for debugging
    #maturity_str = "31/01/2046"                                     #Debugging
    #coupon_str = "0.875"                                            #Debugging
    #price_str = "43.88"                                             #Debugging

    try:
        maturity, coupon, price = validate_inputs(maturity_str, coupon_str, price_str)
        results = compute_gilt_yield(maturity, coupon, price)
        display_results(results, price)
    except ValueError as err:
        print(f"\nError: {err}")


if __name__ == '__main__':
    main()
