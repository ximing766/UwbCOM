# import numpy as np

# # 初始状态估计
# x = 0.0  # 初始位置
# E_est = 0.5  # 初始误差协方差

# # 过程噪声协方差
# Q = 0.01
# # 状态转移矩阵
# F = 1.0  # 假设位置不变
# # 观测矩阵
# H = 1.0 
# # 观测噪声协方差
# E_mea = 0.35


# # 生成1000个随机的0和1的测量值
# measurements = list(np.random.randint(0, 2, 1000))
# measurements.extend([0] * 1000)
# measurements.extend([1] * 10)

# for i, z in enumerate(measurements):
#     # 预测步骤
#     x = F * x
#     E_est = F * E_est * F + Q

#     y = z - H * x
#     S = H * E_est * H + E_mea

#     K = E_est * H / S  # 计算卡尔曼增益
#     x = x + K * y  # 更新状态估计
#     E_est = (1 - K * H) * E_est  # 更新误差协方差

#     # 分类
#     classification = 1 if x >= 0.5 else 0
#     print(f"Time step {i + 1}: Measure = {z}, Predict = {x:.5f}, E_est={E_est:.10f}, K = {K}, Classification = {classification}")

import numpy as np
# 初始状态估计
x = np.array([[0.0], [0.0]])  # 初始位置和速度
E_est = np.array([[0.5, 0.0], [0.0, 0.5]])  # 初始误差协方差

# 过程噪声协方差
Q = np.array([[0.01, 0.0], [0.0, 0.01]])


# 状态转移矩阵
F = np.array([[1.0, 1.0], [0.0, 1.0]])  # 假设位置和速度保持不变
# 观测矩阵
H = np.array([[1.0, 0.0]])
# 观测噪声协方差
E_mea = np.array([[0.35]])

# 生成1000个随机的0和1的测量值
measurements = list(np.random.randint(0, 2, 100))
measurements.extend([0] * 100)
measurements.extend([1] * 10)

for i, z in enumerate(measurements):
    z = np.array([[z]])  # 将测量值转换为矩阵形式

    # 预测步骤
    x = F @ x                    #常规状态下x的更新
    E_est = F @ E_est @ F.T + Q

    S = H @ E_est @ H.T + E_mea
    K = E_est @ H.T @ np.linalg.inv(S)  # 计算卡尔曼增益

    y = z - H @ x
    x = x + K @ y                       # 更新状态估计
    E_est = (np.eye(2) - K @ H) @ E_est  # 更新误差协方差

    # 分类
    classification = 1 if x[0, 0] >= 0.5 else 0
    print(f"Time step {i + 1}: Measure = {z[0, 0]}, Predict = {x[0, 0]:.5f}, E_est={E_est[0, 0]:.10f}, K = {K[0, 0]}, Classification = {classification}")
