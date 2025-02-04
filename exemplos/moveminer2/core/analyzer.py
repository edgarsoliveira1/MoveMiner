from ..metrics.distance_calculation import (
    DistanceCalculator,
    EuclideanDistanceCalculation,
    HaversineDistanceCalculation,
)
from ..metrics.od_matrix_calculation import (
    ClusterODMatrixCalculation,
    ODMatrixCalculator,
)
from ..metrics.radius_gyration import (
    HaversineRadiusGyrationCalculation,
    RadiusGyrationCalculator,
)
from ..metrics.speed_calculation import SimpleSpeedCalculation, SpeedCalculator
from ..metrics.time_diff_calculation import (
    SimpleTimeDiffCalculation,
    TimeDiffCalculator,
)
from ..metrics.turning_angle_calculation import (
    HaversineTurningAngleCalculation,
    TurningAngleCalculator,
)
from ..patterns.cluster_detection import ClusterDetector, KMeansClusterDetection
from ..preprocessing.compression import StopCompression, TrajectoryCompressor
from ..preprocessing.outlier_detection import OutlierDetector, SpeedOutlierDetector
from ..preprocessing.segmentation import StopSegmentation, TrajectorySegmenter
from ..preprocessing.stop_detection import SpeedStopDetection, StopDetector
from ..visualization.plot_heatmap import HeatmapPlotter, HvHeatmapPlotStrategy
from ..visualization.plot_histogram import (
    HistogramPlotter,
    HvHistogramPlotStrategy,
    HvKDEPlotStrategy,
)
from ..visualization.plot_points import PointPlotStrategy, PointPlotter
from ..visualization.plot_polar import PolarPlotter, PyPlotPolarBarPlotStrategy


class Analyzer:
    class _MetricsFacade:
        def __init__(self, is_geo=True):
            self.distance_calculator = DistanceCalculator(
                HaversineDistanceCalculation()
            )
            if not is_geo:
                self.distance_calculator.set_strategy(EuclideanDistanceCalculation())
            self.timediff_calculator = TimeDiffCalculator(SimpleTimeDiffCalculation())
            self.turning_angle_calculator = TurningAngleCalculator(
                HaversineTurningAngleCalculation()
            )
            self.speed_calculator = SpeedCalculator(SimpleSpeedCalculation())
            self.radius_calculator = RadiusGyrationCalculator(
                HaversineRadiusGyrationCalculation()
            )
            self.od_matrix_calculator = ODMatrixCalculator(ClusterODMatrixCalculation())

        # Adicione métodos para calcular métricas específicas aqui

    class _PreprocessingFacade:
        def __init__(self):
            self.stop_detector = StopDetector(SpeedStopDetection())
            self.outlier_detector = OutlierDetector(SpeedOutlierDetector())
            self.cluster_detector = ClusterDetector(KMeansClusterDetection())
            self.compressor = TrajectoryCompressor(StopCompression())
            self.segmenter = TrajectorySegmenter(StopSegmentation())

    class _VisualizationFacade:
        def __init__(self):
            self.spatial_plotter = PointPlotter(PointPlotStrategy())
            self.hist_plotter = HistogramPlotter(HvHistogramPlotStrategy())
            self.kde_plotter = HistogramPlotter(HvKDEPlotStrategy())
            self.heatmap_plotter = HeatmapPlotter(HvHeatmapPlotStrategy())
            self.polar_plotter = PolarPlotter(PyPlotPolarBarPlotStrategy())

    def __init__(self, is_geo=True):
        self.metrics = self._MetricsFacade(is_geo)
        self.preprocessing = self._PreprocessingFacade()
        self.visualizer = self._VisualizationFacade()

    def spatial_plot(self, *args, **kwargs):
        return self.visualizer.spatial_plotter.plot(*args, **kwargs)

    def hist_plot(self, *args, **kwargs):
        return self.visualizer.hist_plotter.plot(*args, **kwargs)

    def kde_plot(self, *args, **kwargs):
        return self.visualizer.kde_plotter.plot(*args, **kwargs)

    def heatmap_plot(self, *args, **kwargs):
        return self.visualizer.heatmap_plotter.plot(*args, **kwargs)

    def polar_plot(self, *args, **kwargs):
        return self.visualizer.polar_plotter.plot(*args, **kwargs)
