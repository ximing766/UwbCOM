import numpy as np
import random
import matplotlib.pyplot as plt

class KalmanFilter:
    def __init__(self, std_acc, x_std_meas, y_std_meas):
        # 状态向量 [x, y]
        self.x = np.matrix([[0], [0]])
        
        # 过程噪声协方差
        self.Q = np.matrix([[std_acc**2, 0],
                            [0, std_acc**2]])
        
        # 测量误差协方差
        self.R = np.matrix([[x_std_meas**2, 0],
                            [0, y_std_meas**2]])
        
        # 状态转移矩阵
        self.F = np.matrix([[1, 0],
                            [0, 1]])
        
        # 观测矩阵
        self.H = np.matrix([[1, 0],
                            [0, 1]])
        # 估计误差协方差矩阵
        self.P = 10*np.eye(self.F.shape[1]) 
    
    def predict(self):
        # 状态预测
        self.x = self.F @ self.x

        # 误差协方差预测
        self.P = self.F @ self.P @ self.F.T + self.Q

        return self.x

    def update(self, z):
        # 计算卡尔曼增益
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        #print('K=',K[0][0])
        # 更新状态向量
        y = z - self.H @ self.x
        self.x = self.x + K @ y

        # 更新误差协方差矩阵
        I = np.eye(self.H.shape[1])
        self.P = (I - K @ self.H) @ self.P
        #print(f"更新后的误差协方差矩阵P: {self.P[0][0]}\n")

        return self.x

if __name__ == "__main__":
    # 示例使用
    std_acc = 1  # 过程噪声标准差
    x_std_meas = 5  # x测量噪声标准差
    y_std_meas = 5  # y测量噪声标准差

    kf = KalmanFilter(std_acc, x_std_meas, y_std_meas)

    # # 示例使用
    trajectory = []
    x = 0
    y = 0
    for _ in range(500):
        x += random.uniform(-1, 1.1)
        y += random.uniform(-1, 1)
        trajectory.append([x, y])

    measurements = []
    predictions = []

    for measurement in trajectory:
        z = np.matrix(measurement).T
        kf.predict()
        prediction = kf.update(z)
        measurements.append(measurement)
        predictions.append(prediction.T.tolist()[0])
        #print(f"measure: {measurement}, predict: {prediction.T.tolist()[0]}")

    # 转换为numpy数组以便绘图
    measurements = np.array(measurements)
    predictions = np.array(predictions)

    # 绘制测量值和预测值的曲线
    plt.figure(figsize=(10, 5))
    plt.plot(measurements[:, 0], measurements[:, 1], label='Measure', marker='o')
    plt.plot(predictions[:, 0], predictions[:, 1], label='Predict', marker='x')
    plt.xlabel('X ')
    plt.ylabel('Y ')
    plt.title('KF_Predict')
    plt.legend()
    plt.grid()
    plt.show()
