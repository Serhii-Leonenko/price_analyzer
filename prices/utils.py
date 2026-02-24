from decimal import Decimal


def usd_to_cents(amount: Decimal) -> int:
    return int(amount * 100)


def cents_to_usd(amount: int) -> Decimal:
    return Decimal(amount) / 100
