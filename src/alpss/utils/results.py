from dataclasses import dataclass, field


@dataclass
class HELResult:
    """Result of Hugoniot Elastic Limit detection."""

    ok: bool
    strength_gpa: float
    uncertainty_gpa: float
    free_surface_velocity: float
    time_detection_ns: float
    consecutive_points: int
    segment_duration_ns: float
    strain_rate: float
    error_message: str | None
    # Internal data for plotting (gradient method)
    segment_start_idx: int | None
    segment_end_idx: int | None
    time_window: np.ndarray | None
    velocity_window: np.ndarray | None
    gradient_smooth: np.ndarray | None
    angles_deg: np.ndarray | None
    # Extra fields populated by the RDP + Linear Hybrid method
    method: str
    rise_slope: float  # [m/s per ns] slope of the rise segment
    plateau_slope: float  # [m/s per ns] slope of the plateau segment
    rdp_knee_time_ns: float  # time of the RDP knee point [ns]
    rdp_points: np.ndarray | None  # simplified vertices for visualisation
