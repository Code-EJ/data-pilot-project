import signal
import threading


stopped = threading.Event()


def stop(*_: object) -> None:
    stopped.set()


signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)
stopped.wait()
