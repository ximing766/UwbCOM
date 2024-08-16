import numpy as np

# def sliding_window_variance(data, window_size):
#     variances = []
#     for i in range(len(data) - window_size + 1):
#         window = data[i:i+window_size]
#         variance = np.var(window)
#         variances.append(variance)
#     return variances

# # 示例数据
# data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# window_size = 3

# result = sliding_window_variance(data, window_size)

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = np.var(data)
print(result)