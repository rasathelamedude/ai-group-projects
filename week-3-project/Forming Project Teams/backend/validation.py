"""Member 5: validation utilities."""


def parse_positive_integer(value: str, field_name: str) -> int:
    normalized_value = str(value).strip()

    if not normalized_value:
        raise ValueError(f"{field_name} is required.")

    if not normalized_value.isdigit():
        raise ValueError(f"{field_name} must be a whole number.")

    parsed_number = int(normalized_value)

    if parsed_number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return parsed_number


def validate_team_inputs(
    total_developers_value: str, team_size_value: str
) -> tuple[int, int]:
    total_developers = parse_positive_integer(
        total_developers_value, "Total developers"
    )
    team_size = parse_positive_integer(team_size_value, "Developers per team")

    if team_size > total_developers:
        raise ValueError(
            "Developers per team cannot be larger than the total developers."
        )

    return total_developers, team_size
