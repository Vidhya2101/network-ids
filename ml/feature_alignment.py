import numpy as np

# =========================================================
# IMPORTANT:
# These features MUST match:
#
# 1. preprocess.py training columns
# 2. live flow feature order
# 3. CNN model input order
#
# =========================================================

FEATURE_COLUMNS = [

    # -----------------------------------------------------
    # Core Flow Features
    # -----------------------------------------------------

    "Flow Duration",

    "Total Fwd Packets",

    "Total Backward Packets",

    # -----------------------------------------------------
    # Packet Length Features
    # -----------------------------------------------------

    "Total Length of Fwd Packets",

    "Total Length of Bwd Packets",

    "Packet Length Mean",

    "Packet Length Std",

    "Packet Length Max",

    "Packet Length Min",

    # -----------------------------------------------------
    # Traffic Rate Features
    # -----------------------------------------------------

    "Flow Bytes/s",

    "Flow Packets/s",

    # -----------------------------------------------------
    # Inter Arrival Time Features
    # -----------------------------------------------------

    "Flow IAT Mean",

    "Flow IAT Std",

    "Flow IAT Max",

    "Flow IAT Min",

    # -----------------------------------------------------
    # TCP Flag Features
    # -----------------------------------------------------

    "SYN Flag Count",

    "ACK Flag Count",

    "FIN Flag Count",

    "RST Flag Count",

    "PSH Flag Count"
]

# =========================================================
# Total Supported Features
# =========================================================

TOTAL_FEATURES = len(FEATURE_COLUMNS)


# =========================================================
# Build Ordered Feature Vector
# =========================================================

def build_feature_vector(flow_features):

    """
    Converts live flow feature dictionary
    into ordered numpy vector for scaler/CNN.
    """

    vector = np.zeros(TOTAL_FEATURES)

    for idx, feature_name in enumerate(FEATURE_COLUMNS):

        if feature_name in flow_features:

            vector[idx] = flow_features[feature_name]

    return vector.reshape(1, TOTAL_FEATURES)