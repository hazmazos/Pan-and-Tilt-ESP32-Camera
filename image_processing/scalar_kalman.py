import numpy as np

scalar_measurements = [10, 13, 13, 17, 17, 21]

def scalar_kalman(estimate):
    vel = 2

    P = 9
    R = 3
    Q = 1

    for measurement in  scalar_measurements:

        P += Q
        print(f"Predicted P is {P}")
        K = P / (P + R)
        print(f"K is {K}")

        pred = estimate + vel
        estimate = pred + K * (measurement - pred)

        P = (1-K) * P


        print(f"estimate is: {estimate}\nmeasurement is: {measurement}\n")

scalar_kalman(10)