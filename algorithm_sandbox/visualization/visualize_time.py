import matplotlib.pyplot as plt


def visualize_time(x, y_social, y_priority, y_weight):
    plt.plot(x, y_social)
    plt.plot(x, y_priority)
    plt.plot(x, y_weight)
    plt.xlabel("Number of students")
    plt.ylabel("Execution time (s)")
    plt.show()
