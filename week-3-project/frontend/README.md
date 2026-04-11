# React Frontend

This folder contains the React frontend for the assignment.

The project is not frontend-only.

- React handles the GUI
- Python `FastAPI` handles the calculation logic, validation, and table generation
- the binomial coefficient table is rendered on the same page under the result

## Member ownership in the React side

- **Member 3:** `src/members/member3/TeamForm.jsx`
- **Member 4:** `src/members/member4/BinomialPopup.jsx`

`BinomialPopup.jsx` keeps its old file name, but it now renders the table inside the same page instead of opening a popup window.

## Best learning order

1. `src/main.jsx`
2. `src/App.jsx`
3. your member file
4. `src/styles.css`

## If you are Member 3

Study these files first:

- `src/members/member3/TeamForm.jsx`
- `src/App.jsx`
- `src/styles.css`

Your job is:

- number inputs
- submit button
- result section on the same page
- sending the request to the Python backend

## If you are Member 4

Study these files first:

- `src/members/member4/BinomialPopup.jsx`
- `src/App.jsx`
- `src/styles.css`

Your job is:

- render the binomial coefficient table under the result
- highlight the final answer cell
- keep the table scrollable and readable

## Run

Start the Python backend first from the root `week4` folder:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

Then start React:

```bash
npm install
npm run dev
```

## Backend URL

The frontend no longer uses one fixed backend address.

- by default it uses the current browser hostname with port `8000`
- you can override it with `VITE_API_BASE_URL`

Example `react-team-app/.env`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```
