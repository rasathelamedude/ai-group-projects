# Team Formation Calculator

A desktop app that answers one question: **given a pool of developers, how many unique project teams can be formed?**

---

## What problem does this solve?

A manager has, say, 10 developers. She needs a team of 4. She wants to know how many _different_ team combinations are possible — not arrangements or rankings, just unique groups of people.

The answer is a single number calculated using a formula called the **Binomial Coefficient**, written as C(n, k) — where n is the total number of developers and k is the team size.

---

## How the math works (plain English)

1. You count how many ordered ways you can pick k people from n people. For 4 from 10, that is 10 × 9 × 8 × 7 = 5040.
2. But order does not matter for a team. The same 4 people can be arranged in 4 × 3 × 2 × 1 = 24 different orders — all of which represent the exact same team.
3. So you divide: 5040 ÷ 24 = **210 unique teams**.

The formula that captures this is:

```
C(n, k) = n! / (k! × (n - k)!)
```

Where `!` means factorial — multiply every whole number from 1 up to that number. So `4! = 1 × 2 × 3 × 4 = 24`.

---

## What the app does

1. You enter **n** (total developers) and **k** (team size) in two number fields.
2. You click **Calculate**.
3. The app shows you the answer — how many unique teams are possible.
4. A second window opens showing the full **Binomial Coefficient table** (Pascal's Triangle), which is a grid of all C(n, k) values up to your n. Your specific answer is highlighted in a different color so you can see exactly where it sits.

---

## What the app does NOT do

- It does not assign people to teams.
- It does not know who the developers are.
- It just counts how many possibilities exist.

---

## Project structure

| Member   | Responsibility                                               |
| -------- | ------------------------------------------------------------ |
| Member 1 | Core C(n, k) calculation — the math, no libraries            |
| Member 2 | Generate the full binomial table (Pascal's Triangle)         |
| Member 3 | Main window — the two inputs and the submit button           |
| Member 4 | Popup window — renders the table with the answer highlighted |
| Member 5 | Input validation, testing, and merging everything together   |

---

## Input rules

- Both n and k must be positive whole numbers.
- k cannot be larger than n (you cannot pick more people than exist).
- Neither field can be empty or zero.

---

## Tech stack

- **Language:** Python
- **GUI:** Tkinter
- **Libraries:** None for the math logic — implemented from scratch

---

## Example

| Input                | Value                |
| -------------------- | -------------------- |
| Total developers (n) | 10                   |
| Team size (k)        | 4                    |
| **Result**           | **210 unique teams** |
