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

Alternative (without Blueprint):
- Create **Web Service** from repo.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

Free tier note:
- Render free plans are typically available but can change over time.
- Free services may sleep after inactivity and take a few seconds to wake.
