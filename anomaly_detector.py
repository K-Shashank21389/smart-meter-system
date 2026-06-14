import numpy as np

def detect_anomaly(readings, current_reading):

    if len(readings) < 3:
        return False

    mean = np.mean(readings)
    std = np.std(readings)

    threshold = mean + (2 * std)

    return current_reading > threshold