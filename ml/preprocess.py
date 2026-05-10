import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import numpy as np
import joblib

# Load dataset
df = pd.read_csv("data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv")

print("[*] Dataset Loaded")
print(df.shape)

# Clean column names
df.columns = df.columns.str.strip()

# Remove invalid rows
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)

print("[*] Cleaned Dataset Shape:", df.shape)

# Separate features and labels
#X = df.drop(columns=['Label'])
from cicids_feature_map import FEATURE_COLUMNS

X = df[FEATURE_COLUMNS]
y = df['Label']

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

joblib.dump(encoder, "models/label_encoder.pkl")

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

joblib.dump(scaler, "models/scaler.pkl")

# Balance dataset
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X_scaled, y_encoded)

print("[*] After SMOTE:", X_resampled.shape)

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled,
    y_resampled,
    test_size=0.2,
    random_state=42
)

# Save processed arrays
np.save("data/X_train.npy", X_train)
np.save("data/X_test.npy", X_test)
np.save("data/y_train.npy", y_train)
np.save("data/y_test.npy", y_test)

print("[*] Preprocessing Complete")