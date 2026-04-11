"""Member 1: main logic for C(n, k)."""


def calculate_combination(total_developers: int, team_size: int) -> int:
    if total_developers < 0 or team_size < 0:
        raise ValueError("Values cannot be negative.")

    if team_size > total_developers:
        raise ValueError("Team size cannot be larger than the total developers.")

    smaller_side = min(team_size, total_developers - team_size)
    result = 1

    for step in range(1, smaller_side + 1):
        result = result * (total_developers - smaller_side + step) // step

    return result
