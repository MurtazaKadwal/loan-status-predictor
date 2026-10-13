from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

app = Flask(__name__)

# The model artifacts were saved with scikit-learn 1.5.1.
# Install the pinned versions in requirements.txt to avoid version mismatches.
model = joblib.load(MODEL_DIR / "loan_status_model.joblib")
scaler = joblib.load(MODEL_DIR / "scaler.joblib")
feature_columns = list(joblib.load(MODEL_DIR / "feature_columns.joblib"))

# Keep these mappings consistent with the notebook's Cell 7.
ENCODINGS = {
    "Gender": {"Female": 0, "Male": 1},
    "Married": {"No": 0, "Yes": 1},
    "Education": {"Not Graduate": 0, "Graduate": 1},
    "Self_Employed": {"No": 0, "Yes": 1},
    "Property_Area": {"Rural": 0, "Semiurban": 1, "Urban": 2},
}

EXPECTED_FEATURES = [
    "Gender", "Married", "Dependents", "Education", "Self_Employed",
    "ApplicantIncome", "CoapplicantIncome", "LoanAmount",
    "Loan_Amount_Term", "Credit_History", "Property_Area"
]

if feature_columns != EXPECTED_FEATURES:
    raise RuntimeError(
        "Feature columns in feature_columns.joblib do not match the website's "
        f"expected order. Loaded: {feature_columns}"
    )

def parse_form(form):
    """Convert human-readable form choices to the exact numeric encoding."""
    gender = form.get("Gender", "")
    married = form.get("Married", "")
    dependents_raw = form.get("Dependents", "")
    education = form.get("Education", "")
    self_employed = form.get("Self_Employed", "")
    property_area = form.get("Property_Area", "")

    required_choices = {
        "Gender": (gender, ENCODINGS["Gender"]),
        "Married": (married, ENCODINGS["Married"]),
        "Education": (education, ENCODINGS["Education"]),
        "Self_Employed": (self_employed, ENCODINGS["Self_Employed"]),
        "Property_Area": (property_area, ENCODINGS["Property_Area"]),
    }
    for field, (value, mapping) in required_choices.items():
        if value not in mapping:
            raise ValueError(f"Please select a valid value for {field.replace('_', ' ')}.")

    if dependents_raw not in {"0", "1", "2", "3+"}:
        raise ValueError("Please select a valid number of dependents.")

    try:
        applicant_income = float(form.get("ApplicantIncome", ""))
        coapplicant_income = float(form.get("CoapplicantIncome", ""))
        loan_amount = float(form.get("LoanAmount", ""))
        loan_term = float(form.get("Loan_Amount_Term", ""))
        credit_history = int(form.get("Credit_History", ""))
    except (TypeError, ValueError):
        raise ValueError("Enter valid numeric values for income, loan amount, and loan term.")

    numeric_values = {
        "Applicant income": applicant_income,
        "Co-applicant income": coapplicant_income,
        "Loan amount": loan_amount,
        "Loan term": loan_term,
    }
    for label, value in numeric_values.items():
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{label} must be a valid non-negative number.")

    if credit_history not in (0, 1):
        raise ValueError("Credit history must be 0 (No) or 1 (Yes).")
    if loan_term <= 0:
        raise ValueError("Loan term must be greater than zero.")

    # The notebook replaces "3+" with 4 before model training.
    dependents = 4 if dependents_raw == "3+" else int(dependents_raw)

    row = {
        "Gender": ENCODINGS["Gender"][gender],
        "Married": ENCODINGS["Married"][married],
        "Dependents": dependents,
        "Education": ENCODINGS["Education"][education],
        "Self_Employed": ENCODINGS["Self_Employed"][self_employed],
        "ApplicantIncome": applicant_income,
        "CoapplicantIncome": coapplicant_income,
        "LoanAmount": loan_amount,
        "Loan_Amount_Term": loan_term,
        "Credit_History": credit_history,
        "Property_Area": ENCODINGS["Property_Area"][property_area],
    }
    return pd.DataFrame([row], columns=feature_columns)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    submitted = {}

    if request.method == "POST":
        submitted = request.form.to_dict()
        try:
            input_df = parse_form(request.form)
            scaled_input = scaler.transform(input_df)
            prediction = model.predict(scaled_input)[0]

            # In the common cleaned loan dataset convention: 1 = Y/approved, 0 = N/not approved.
            # Confirm this mapping against the original target encoding used to create loan_cleaned.csv.
            approved = str(prediction).strip().lower() in {"1", "1.0", "y", "yes", "approved", "true"}
            result = {
                "approved": approved,
                "label": "Likely eligible" if approved else "Not likely eligible",
                "detail": (
                    "The model predicts the loan status as approved for the information provided."
                    if approved else
                    "The model predicts the loan status as not approved for the information provided."
                ),
            }
        except ValueError as exc:
            error = str(exc)
        except Exception:
            app.logger.exception("Prediction failed")
            error = "Something went wrong while generating the prediction. Check your model files and inputs."

    return render_template("index.html", result=result, error=error, submitted=submitted)

if __name__ == "__main__":
    app.run(debug=True)
