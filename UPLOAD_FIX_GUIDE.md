# Fix the existing GitHub Pages project (Android-friendly guide)

The current repository uploaded the files to the root folder. The previous README and test/script expected nested paths, which caused run commands to fail. This ZIP is deliberately flat: keep the files together in the repository root.

## Recommended clean repair
1. Download and extract `Infor_Birst_Inventory_Analytics_Fixed.zip` on your phone.
2. Open the extracted folder and check it contains `index.html`, `README.md`, the three CSVs, Python script, tests, SQL files, charts, and Birst guide.
3. Open the existing GitHub repo: https://github.com/Vikas915577/Infor-Birst-Inventory-Analytics
4. Use **Add file → Upload files**. Upload the contents of the extracted folder, not the ZIP itself and not an extra nested folder.
5. Where GitHub refuses a duplicate filename, edit/replace that file with the same-named file from the extracted bundle; remove the accidentally committed `test_inventory_data.cpython-313.pyc`.
6. Make sure `index.html` is at the root next to `README.md`. GitHub Pages needs a root `index.html` (or `index.md`) for a custom homepage.
7. In **Settings → Pages**, confirm the publishing source is branch `main`, folder `/ (root)`.
8. Wait for the Pages deployment to complete, then open https://vikas915577.github.io/Infor-Birst-Inventory-Analytics/. Refresh or try Incognito if the old page is cached.

## Validate the project locally
Run these from the extracted folder:

```bash
python -m pip install -r requirements.txt
python analyze_inventory.py
python -m unittest test_inventory_data -v
```

All sample data is synthetic. The page and guide do not claim that the Birst dashboard is already deployed.
