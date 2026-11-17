# M&M RPro Analytics — Frontend

Plain HTML/CSS/JS frontend.

## Files
- `index.html` — Login page
- `dashboard.html` — Main dashboard
- `css/styles.css`
- `js/login.js`, `js/dashboard.js`, `js/chat.js`

## Deploy on Render
1. Push this `frontend` folder to GitHub (or the whole repo).
2. Create a new **Static Site** on Render.
3. Point it at the `frontend` directory (set Root Directory to `frontend` if needed).
4. Publish.

## Backend endpoints expected
- `POST /login` → `{ email, password }` → `{ token }`
- `GET /dashboard/summary` (Bearer token)
- `GET /dashboard/recommendations` (Bearer token)
- `POST /ask` (Bearer token) → `{ question }` → `{ answer }`

These endpoints still need to be added to the MMA Server backend.
