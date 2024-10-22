#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void kalman_filter_classify(int measurement) {
    static double x = 0.0; // 初始位置
    static double E_est = 0.5; // 初始误差协方差
    const double Q = 0.003; // 过程噪声协方差
    const double E_mea = 0.35; // 观测噪声协方差
    // 状态转移矩阵
    const double F = 1.0; // 假设位置不变
    // 观测矩阵
    const double H = 1.0;

    // 预测步骤
    x = F * x;
    E_est = F * E_est * F + Q;

    double y = measurement - H * x;
    double S = H * E_est * H + E_mea;

    double K = E_est * H / S; // 计算卡尔曼增益
    x = x + K * y; // 更新状态估计
    E_est = (1 - K * H) * E_est; // 更新误差协方差

    // 分类
    int classification = x >= 0.5 ? 1 : 0;
    printf("Measure = %d, Predict = %.5f, E_est = %.10f, K = %.5f, Classification = %d\n", 
           measurement, x, E_est, K, classification);
}

int main() {
    srand(time(0)); // 初始化随机数生成器

    int measurements[2010];
    for (int i = 0; i < 1000; i++) {
        measurements[i] = rand() % 2;
    }
    for (int i = 1000; i < 2000; i++) {
        measurements[i] = 1;
    }
    for (int i = 2000; i < 2010; i++) {
        measurements[i] = 0;
    }

    for (int i = 0; i < 2010; i++) {
        kalman_filter_classify(measurements[i]);
    }

    return 0;
}