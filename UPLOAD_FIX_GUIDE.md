# Upload the DDD-upgraded Infor Birst project from Android

This bundle is a **complete flat-layout repository** for GitHub Pages. Keep `index.html`, `README.md`, the three source CSVs, Python script, outputs, SQL, Birst guide, and all chart images together in the repository root.

## Replace existing files
1. Download and extract `Infor_Birst_Inventory_DDD_Upgrade.zip`.
2. Open https://github.com/Vikas915577/Infor-Birst-Inventory-Analytics.
3. Choose **Add file → Upload files** and upload the *contents* of the extracted folder—not only the ZIP.
4. Replace same-named old files with these upgraded versions. Upload the new files `index.html`, `dashboard_data.json`, `DDD_USER_STORY_AND_ACCEPTANCE_CRITERIA.md`, and `RESEARCH_REFERENCES.md`.
5. Remove accidental `__pycache__` and `.pyc` files from the repo.
6. In **Settings → Pages**, set source to branch `main`, folder `/(root)`.
7. Wait for Pages deployment, then open https://vikas915577.github.io/Infor-Birst-Inventory-Analytics/. Refresh if needed.

## Local validation
```bash
python -m pip install -r requirements.txt
python analyze_inventory.py
python -m unittest test_inventory_data -v
```

The DDD website is a static case-study/preview of the decision workflow. It is not the real Birst application. Build and reconcile the three pages in your Birst account before describing a live Birst dashboard as complete.
