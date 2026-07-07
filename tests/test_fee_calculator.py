import bas_server.fee_calculator as fc


## Test All Caps
# Entry
def test_entry_tier_capped():
    assert fc.calculate_fee(900000) == 2000
    assert fc.calculate_fee(800000) == 2000
    assert fc.calculate_fee(799600) == 1999


# Mid
def test_mid_tier_capped():
    assert fc.calculate_fee(1800000) == 2500
    assert fc.calculate_fee(1500000) == 2500
    assert fc.calculate_fee(1249500) == 2499


# Upper
def test_upper_tier_capped():
    assert fc.calculate_fee(4000000) == 4000
    assert fc.calculate_fee(3200000) == 4000
    assert fc.calculate_fee(3199200) == 3999


# High
def test_high_tier_capped():
    assert fc.calculate_fee(9000000) == 6000
    assert fc.calculate_fee(7500000) == 6000
    assert fc.calculate_fee(7500000) == 6000


# Top
def test_top_tier_capped():
    assert fc.calculate_fee(99999999) == 20000
    assert fc.calculate_fee(33333333) == 20000
    assert fc.calculate_fee(33331666) == 19999


## Test All Tiers
# Free
def test_get_tier_free_bottom():
    assert fc.get_tier(1) is fc.free_tier


def test_get_tier_free_top():
    assert fc.get_tier(200000) is fc.free_tier


# Entry
def test_get_tier_entry_bottom():
    assert fc.get_tier(200001) is fc.entry_tier


def test_get_tier_entry_top():
    assert fc.get_tier(1000000) is fc.entry_tier


# Mid
def test_get_tier_mid_bottom():
    assert fc.get_tier(1000001) is fc.mid_tier


def test_get_tier_mid_top():
    assert fc.get_tier(2000000) is fc.mid_tier


# Upper
def test_get_tier_upper_bottom():
    assert fc.get_tier(2000001) is fc.upper_tier


def test_get_tier_upper_top():
    assert fc.get_tier(5000000) is fc.upper_tier


# High
def test_get_tier_high_bottom():
    assert fc.get_tier(5000001) is fc.high_tier


def test_get_tier_high_top():
    assert fc.get_tier(10000000) is fc.high_tier


# Top
def test_get_tier_top_bottom():
    assert fc.get_tier(10000001) is fc.top_tier


def test_get_tier_top_top():
    assert fc.get_tier(100000000) is fc.top_tier


# Test that we dont have any floats at any point
def test_never_a_float():

    raw = fc.compute_raw_fee(333000, fc.entry_tier)
    rounded = fc.round_fee(raw)
    capped = fc.apply_cap(rounded, fc.entry_tier)
    final = fc.calculate_fee(333000)

    assert not isinstance(raw, float)  # Decimal
    assert not isinstance(rounded, float)  # int
    assert not isinstance(capped, float)  # int
    assert not isinstance(final, float)  # int
