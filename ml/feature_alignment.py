import numpy as np
from cicids_feature_map import FEATURE_COLUMNS

TOTAL_FEATURES = len(FEATURE_COLUMNS)


def build_feature_vector(flow_features):
    """
    Converts a live flow feature dictionary into an ordered
    numpy vector matching the model's training column order.
    """
    vector = np.zeros(TOTAL_FEATURES)

    for idx, feature_name in enumerate(FEATURE_COLUMNS):
        if feature_name in flow_features:
            vector[idx] = flow_features[feature_name]

    return vector.reshape(1, TOTAL_FEATURES)