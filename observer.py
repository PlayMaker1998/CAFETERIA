# observer.py
_subscribers = {}

def subscribe(event_name, fn):
    _subscribers.setdefault(event_name, []).append(fn)

def publish(event_name, data):
    for fn in _subscribers.get(event_name, []):
        fn(data)
