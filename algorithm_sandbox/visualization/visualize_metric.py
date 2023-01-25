import matplotlib.pyplot as plt


def visualize_metric(x, y_social, y_priority, y_weight, metric_name):
    plt.figure(figsize=(9, 5))
    plt.plot(x, y_social, label='Social Algorithm')
    plt.plot(x, y_priority, label='Priority Algorithm')
    plt.plot(x, y_weight, label='Weight Algorithm')
    plt.xlabel("Number of students")
    plt.ylabel(metric_name)
    plt.legend(loc=(1.04, 0.80))
    plt.subplots_adjust(right=0.75)
    plt.show()
