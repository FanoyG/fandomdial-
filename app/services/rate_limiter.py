import time

class RateLimiter:
    """
    Sliding window log rate limiter to prevent overflowing Gemini quota boundaries.
    Defaults to allowing a safe cap of 15 requests per minute.
    """
    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests_log = []

    def allow_request(self) -> bool:
        current_time = time.time()
        # Evict timestamps older than our active window threshold
        self.requests_log = [t for t in self.requests_log if current_time - t < self.window_seconds]
        
        if len(self.requests_log) >= self.max_requests:
            return False
            
        self.requests_log.append(current_time)
        return True
