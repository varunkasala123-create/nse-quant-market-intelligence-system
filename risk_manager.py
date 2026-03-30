def position_size(account_size, entry, stop):

    risk_per_trade = 0.01 * account_size   # 1% risk

    risk_per_share = abs(entry - stop)

    if risk_per_share == 0:
        return 0

    size = risk_per_trade / risk_per_share

    max_position = account_size * 0.2 / entry  # max 20% of capital

    size = min(size, max_position)

    return round(size,2)