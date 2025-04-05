import numpy as np


def calculate_reverberation_times(decay_curve: np.ndarray, sample_rate: int) -> dict[str, float]:
    """
    Calculates reverberation times (EDT, T20, T30) from an energy decay curve.

    Args:
        decay_curve: Energy decay curve (typically squared impulse response in dB)
        sample_rate: Sampling rate of the audio signal in Hz

    Returns:
        Tuple containing:
        - reverberation_times: Array of calculated times [EDT, T20, T30] in seconds
        - parameter_names: List of parameter names ['EDT', 'T20', 'T30']

    Reference:
        ISO 3382-1:2009 Acoustics - Measurement of room acoustic parameters
    """
    # Define analysis parameters
    analysis_ranges = {
        'EDT': (-1, -10),   # Early Decay Time (0 to -10 dB)
        'T20': (-5, -25),   # Traditional T20 (-5 to -25 dB)
        'T30': (-5, -35)    # Traditional T30 (-5 to -35 dB)
    }

    rt_results = {}
    time_axis = np.arange(len(decay_curve)) / sample_rate

    for rt_type, (lower_db, upper_db) in analysis_ranges.items():
        # Find analysis window indices
        try:
            start_idx = _find_last_above_threshold(decay_curve, lower_db)
            end_idx = _find_last_above_threshold(decay_curve, upper_db)
            
            if start_idx >= end_idx:
                raise ValueError(
                    f"Invalid range for {rt_type}: "
                    f"{lower_db} dB occurs after {upper_db} dB"
                )

            # Linear regression to estimate decay rate
            slope, _ = np.polyfit(
                time_axis[start_idx:end_idx],
                decay_curve[start_idx:end_idx],
                1
            )
            
            # Calculate RT (time for 60 dB decay)
            rt_results[rt_type] = -60 / slope

        except (IndexError, ValueError) as e:
            raise ValueError(
                f"Failed to calculate {rt_type}: {str(e)}. "
                "Check decay curve quality or analysis ranges."
            ) from e

    return rt_results

def _find_last_above_threshold(signal: np.ndarray, threshold_db: float) -> int:
    """Helper: Finds the last index where signal ≥ threshold."""
    above_threshold = np.where(signal >= threshold_db)[0]
    if not above_threshold.size:
        raise ValueError(f"No values found ≥ {threshold_db} dB")
    return above_threshold[-1]