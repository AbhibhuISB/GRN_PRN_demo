# Sid's Farm Demo - GRN/PRN QR Acknowledgement

This is a demo-only web app to present the paper-to-online order acknowledgement flow.

## What this demo covers

- Store manager flow with two options:
  - **GRN**: yesterday's order auto-populated; product-wise confirmation and editable quantities.
  - **PRN**: blank table with SKU dropdown, quantity, and image upload (camera-enabled input on mobile).
- Final confirmation generates a QR code.
- QR scan opens a role chooser (**CFA** or **Store Manager**).
- CFA can either:
  - Accept and complete the transaction, or
  - Dispute numbers so manager can edit and regenerate QR.
- Multiple manager sessions are independent (no login used).

## Run locally

1. Open terminal in this folder:
   ```powershell
   cd d:\ISB\ideas\sids-farm-demo
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Start app:
   ```powershell
   python app.py
   ```
4. Open:
   - Launcher: `http://127.0.0.1:5000`

## Demo tips

- Create multiple manager sessions from launcher for independent parallel testing.
- For audience scans, show generated QR on screen.
- On mobile, PRN image field uses `accept=image/*` + `capture=environment` to route to camera where supported.

## Notes

- Data is stored in-memory only (resets on restart).
- This intentionally avoids deployment, auth, and production hardening.

## Deploy on Render (simple path)

1. Push this folder to a GitHub repo.
2. In Render, click **New +** -> **Blueprint**.
3. Connect the repo and select this project root.
4. Render will detect [render.yaml](render.yaml) and create a free web service.
5. Wait for deploy, then open the generated Render URL.

### Render click-by-click (recommended)

1. Log in to Render dashboard.
2. Click **New +** (top-right).
3. Click **Blueprint**.
4. Connect GitHub account (if prompted).
5. Select repo: **GRN_PRN_demo**.
6. Keep branch as **main**.
7. Click **Apply** / **Create Blueprint Instance**.
8. Wait for build + deploy to complete.
9. Open service URL shown by Render.

Expected Render settings (auto-read from [render.yaml](render.yaml)):
- Type: Web Service
- Environment: Python
- Plan: Free
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

Alternative (without Blueprint):
- Create **Web Service** from repo.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

Free tier note:
- Render free plans are typically available but can change over time.
- Free services may sleep after inactivity and take a few seconds to wake.

If first deploy fails:
- Check **Logs** in Render service page.
- Confirm repo root contains [app.py](app.py), [requirements.txt](requirements.txt), and [render.yaml](render.yaml).
- Click **Manual Deploy** -> **Deploy latest commit** after fixing issues.
