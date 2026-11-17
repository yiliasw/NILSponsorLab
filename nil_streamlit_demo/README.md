# NIL Sponsor Manager — Streamlit + SQLite demonstration

This is a **standalone classroom prototype**, not the full NIL database used in class. It creates a small `BUSINESS` table with four columns and five fictional sample companies automatically on first run.

## Browser-only setup using GitHub Codespaces
1. Create a GitHub repository (private or public) and upload `app.py`, `requirements.txt`, and `README.md`.
2. From the repository, choose **Code → Codespaces → Create codespace**. Allow the environment to start.
3. In the Codespaces terminal, run `python -m pip install -r requirements.txt`.
4. Run `python -m streamlit run app.py --server.address 0.0.0.0`.
5. When Codespaces detects port **8501**, choose **Open in Browser** (or use the Ports tab). Keep port visibility **Private** unless you intend to share it.
6. Test Directory, Add Business, Edit, and Delete. Data lives in `nil_demo.db` in the Codespace. Avoid committing that generated file to GitHub.

## Optional public deployment
In Streamlit Community Cloud, choose **Create app**, select your GitHub repository, branch, and `app.py`, then deploy. Hosting requirements and account eligibility can change. The deployed app's local SQLite data is **not durable** across restarts/redeployments. This makes it suitable for a demonstration, not production recordkeeping.

## What to observe
- `sqlite3.connect()` opens a database file.
- `CREATE TABLE IF NOT EXISTS` defines the schema.
- `INSERT`, `UPDATE`, `DELETE` change records using **parameterized SQL**.
- `SELECT` feeds a Pandas DataFrame for the directory and chart.
- `with connect() as conn:` commits successful changes and rolls back if an exception occurs. (The context manager does not itself close the connection; this small demo is adequate for class use.)

## Limitations
- Uses fictional data only; no authentication or multi-user concurrency design.
- Simplified `BUSINESS` schema may differ from the existing NIL course database.
- For graded projects, assess the normalized database, joins, reports, and correctness—not just interface appearance.
