"""Member 2: build Pascal's Triangle / binomial coefficient table."""


def build_binomial_table(total_developers: int) -> list[list[int]]:
    table: list[list[int]] = []

    for row_index in range(total_developers + 1):
        if row_index == 0:
            table.append([1])
            continue

        previous_row = table[row_index - 1]
        current_row = [1]

        for column_index in range(1, row_index):
            current_row.append(previous_row[column_index - 1] + previous_row[column_index])

        current_row.append(1)
        table.append(current_row)

    return table
