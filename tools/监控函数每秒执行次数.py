import threading
import time
from functools import wraps

class FunctionCounter:
    def __init__(self):
        self.lock = threading.Lock()
        self.count = 0
        self.last_call_time = time.time()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                self.count += 1
            return func(*args, **kwargs)

        def report():
            while True:
                time.sleep(1)
                with self.lock:
                    current_time = time.time()
                    if current_time - self.last_call_time >= 1:
                        print(f"Function {func.__name__} has been called {self.count} times in the last second.")
                        self.count = 0
                        self.last_call_time = current_time

        threading.Thread(target=report, daemon=True).start()
        return wrapper

# 使用装饰器
counter = FunctionCounter()

@counter
def my_function():
    pass

# 测试函数
for _ in range(10000):
    my_function()
    time.sleep(0.01)  # 模拟函数调用间隔