# Forming Project Teams

A web application that answers one question: **given a pool of developers, how many unique project teams can be formed?**

---

## What problem does this solve?

A manager or team leader may know how many developers are available and how many people are needed for one team, but still not know how many different teams are possible.

This project solves that by calculating the number of unique team combinations. It focuses on combinations, not arrangements, so the same group is counted once even if the order changes.

---

## How the idea works (plain English)

1. You enter the total number of developers.
2. You enter how many developers should be in each team.
3. The system checks that the values are valid.
4. The backend calculates how many unique teams can be formed.
5. The app also shows the binomial coefficient table so the result can be viewed in context.

---

## What the app does

1. Accepts the total number of developers.
2. Accepts the number of developers required per team.
3. Validates the inputs before running the calculation.
4. Calculates the total number of unique teams through the Python backend.
5. Shows the final answer on the page.
6. Displays the binomial coefficient table below the result.

---

## What the app does NOT do

- It does not assign real people to teams.
- It does not store developer profiles.
- It does not rank or recommend team choices.
- It only calculates how many valid team combinations are possible.

---

## Project structure

| Area     | Responsibility |
| -------- | -------------- |
| Frontend | Collects user input, sends the request, and displays the result and table |
| Backend  | Validates the values, calculates the combinations, and returns the response |
| Testing  | Checks the main logic and confirms the input rules work correctly |

---

## Input rules

- Both values must be whole numbers.
- Both values must be greater than zero.
- Developers per team cannot be larger than the total number of developers.
- Empty or invalid input is rejected.

---

## Tech stack

- **Backend:** Python with FastAPI
- **Frontend:** React with Vite
- **Logic:** Manual team-combination calculation
- **Output:** Result display plus binomial coefficient table

---

## Example

| Input            | Value |
| ---------------- | ----- |
| Total developers | 10    |
| Developers per team | 4 |
| Result           | 210 unique teams |
