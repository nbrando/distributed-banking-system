from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass

@dataclass
class FeeTier:
    bound: int
    rate: Decimal
    cap: int

top_tier = FeeTier(10000000, Decimal("0.0006"), 20000)
high_tier = FeeTier(5000000, Decimal("0.0008"), 6000)
upper_tier = FeeTier(2000000, Decimal("0.00125"), 4000)
mid_tier = FeeTier(1000000, Decimal("0.0020"), 2500)
entry_tier = FeeTier(200000, Decimal("0.0025"), 2000)
free_tier = FeeTier(0, Decimal("0"), 0)


def get_tier(amount_cents):

    if amount_cents > top_tier.bound:
        return top_tier

    if amount_cents > high_tier.bound:
        return high_tier

    if amount_cents > upper_tier.bound:
        return upper_tier

    if amount_cents > mid_tier.bound:
        return mid_tier

    if amount_cents > entry_tier.bound:
        return entry_tier
    
    return free_tier


def compute_raw_fee(amount_cents, tier):
    return Decimal(amount_cents) * tier.rate


def round_fee(raw_fee):
    return int(raw_fee.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def apply_cap(fee, tier):
    return min(fee, tier.cap)


def calculate_fee(amount_cents):

    # Get tier
    tier = get_tier(amount_cents)

    # 1. Calculate fee    
    raw_fee = compute_raw_fee(amount_cents, tier)
    
    # 2. Round using single global rounding policy
    rounded_fee = round_fee(raw_fee)

    # 3. Apply per-transfer cap
    final_fee = apply_cap(rounded_fee, tier)

    return final_fee
    