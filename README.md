# Loanwise — Loan Status Prediction

A minimal, ambient dark-themed Flask website for your loan status classification project. It loads the three supplied joblib files and uses the saved `StandardScaler` before calling your saved SVC classifier.

## Folder structure

```text
loan_status_website/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── models/
│   ├── loan_status_model.joblib
│   ├── scaler.joblib
│   └── feature_columns.joblib
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Run in VS Code (Windows)

1. Extract this ZIP.
2. Open the `loan_status_website` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run:
   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install the pinned packages:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start Flask:

   ```bash
   python app.py
   ```

7. Open the local address shown in the terminal, usually `http://127.0.0.1:5000`.

## Important model notes

- The saved feature order is checked at startup. The current expected columns are `Gender`, `Married`, `Dependents`, `Education`, `Self_Employed`, `ApplicantIncome`, `CoapplicantIncome`, `LoanAmount`, `Loan_Amount_Term`, `Credit_History`, and `Property_Area`.
- The categorical encodings follow the notebook: Female=0/Male=1; No=0/Yes=1 for Married and Self_Employed; Not Graduate=0/Graduate=1; Rural=0/Semiurban=1/Urban=2. Dependents `3+` becomes `4`.
- This app scales form inputs with the supplied scaler, then passes them to the saved SVC model. Do not scale a second time.
- The SVC was saved with scikit-learn 1.5.1. Use the pinned version in `requirements.txt`. Loading scikit-learn model files across versions can produce warnings or incompatibilities.
- The output interpretation assumes the target encoding is `1 = approved (Y)` and `0 = not approved (N)`. Confirm this against the code used to create `loan_cleaned.csv`; the visible notebook does not show how `Loan_Status` itself was encoded.
- This is a portfolio/learning demonstration, not a credit decision system. It is not a guarantee of loan approval and should not be used as the sole basis for real lending decisions.

## Before publishing online

This project loads trusted local model files. Do not accept uploaded `.joblib` files from website visitors. For a public deployment, turn off Flask debug mode and use a production WSGI server.
