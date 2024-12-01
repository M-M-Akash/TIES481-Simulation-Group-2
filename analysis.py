from scipy import stats
import numpy as np


def calculate_point_estimates(data):
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    return mean, std


def calculate_confidence_intervals(data, confidence=0.95):
    mean, std = calculate_point_estimates(data)
    n = len(data)
    margin = stats.t.ppf((1 + confidence) / 2, n - 1) * (std / np.sqrt(n))
    return mean - margin, mean + margin


