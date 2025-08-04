from qm.simulate._simulator_samples import SimulatorSamples, SimulatorControllerSamples

from ._streams_manager import StreamsManager
from ._single_stream_fetchers import BaseSingleStreamFetcher, SingleStreamSingleResultFetcher, SingleStreamMultipleResultFetcher

# Keeping these names for backwards compatibility
StreamingResultFetcher = StreamsManager
SingleStreamingResultFetcher = SingleStreamSingleResultFetcher
MultipleStreamingResultFetcher = SingleStreamMultipleResultFetcher

__all__ = [
    "BaseSingleStreamFetcher",
    "StreamsManager",
    "StreamingResultFetcher",
    "SingleStreamingResultFetcher",
    "MultipleStreamingResultFetcher",
    "SingleStreamSingleResultFetcher",
    "SingleStreamMultipleResultFetcher",
    "SimulatorSamples",
    "SimulatorControllerSamples",
]
