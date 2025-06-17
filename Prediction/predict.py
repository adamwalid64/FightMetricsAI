import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb

np.random.seed(42)
n_samples = 500

data = pd.DataFrame({
    "Height": np.random.normal(70, 3, n_samples),
    "Weight": np.random.normal(170, 15, n_samples),
    "Reach": np.random.normal(72, 4, n_samples),
    "SLpM": np.random.normal(3.5, 1, n_samples),
    "Str_Acc": np.random.uniform(30, 60, n_samples),
    "SApM": np.random.normal(3.0, 1, n_samples),
    "Str_Def": np.random.uniform(40, 70, n_samples),
    "TD_Avg": np.random.normal(2.0, 1, n_samples),
    "TD_Acc": np.random.uniform(30, 60, n_samples),
    "TD_Def": np.random.uniform(40, 80, n_samples),
    "Sub_Avg": np.random.normal(0.5, 0.3, n_samples),
    "Win_Category": np.random.randint(0, 2, n_samples)
})

X = data.drop("Win_Category", axis=1)
y = data["Win_Category"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"✅ Accuracy: {accuracy:.2f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))