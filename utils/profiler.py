import cProfile
import io
import pstats

profiler = None  # Global variable to hold the profiler instance

def start_profiling():
    global profiler
    profiler = cProfile.Profile()
    profiler.enable(subcalls=True, builtins=False)
    if not profiler:
        profiler = cProfile.Profile()
        profiler.enable()
        return "Profiling started."
    else:
        return "Profiler is already running."

def stop_profiling():
    global profiler
    if profiler:
        profiler.disable()
        profiler = None
        return "Profiling stopped."
    else:
        return "Profiler is not running."

def get_stats():
    global profiler
    if profiler:
        profiler.disable()
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats()
        profiler.enable()  # Re-enable profiling after capturing stats
        return s.getvalue()
    else:
        return "Profiler is not running."
