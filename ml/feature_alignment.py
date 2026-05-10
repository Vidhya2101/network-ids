import numpy as np

# IMPORTANT:
# These must match the SAME order used during training.
# We start with the features we currently support.
FEATURE_COLUMNS = [
    "duration",
    "packet_count",
    "byte_count",
    "avg_packet_size",
    "packets_per_sec",
    "bytes_per_sec",
    "syn_flags",
    "ack_flags",
    "fin_flags"
]

TOTAL_FEATURES = 78


def build_feature_vector(flow_features):
    """
    Converts live flow statistics into a fixed 78-feature vector
    compatible with the trained CICIDS2017 CNN model.
    """

    vector = np.zeros(TOTAL_FEATURES)

    for idx, feature_name in enumerate(FEATURE_COLUMNS):

        if feature_name in flow_features:
            vector[idx] = flow_features[feature_name]

    return vector.reshape(1, TOTAL_FEATURES)