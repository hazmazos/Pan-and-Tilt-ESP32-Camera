import numpy as np

measurements = np.array([12, 11, 13, 15, 14, 16])

x = np.array([10,2])
P = np.array([[4,1],[1,2]])

A = np.array([[1,1],[0,1]])
Q = np.zeros((2,2))

H = np.array([[1, 0]])
R = 4

for measurement in measurements:

    z = measurement

    x_pred = A @ x
    P_pred = A @ P @ A.T + Q

    y = z - H @ x_pred

    K = P_pred @ H.T @ np.linalg.inv(H @ P_pred @ H.T + R)

    x = x_pred + K @ y

    print(f"for measurement {measurement} the state vector is found to be {x} ")


    P = (np.identity(2) - K@H) @ P_pred




