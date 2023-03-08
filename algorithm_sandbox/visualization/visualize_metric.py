import matplotlib.pyplot as plt


def visualize_metric(x, y_weight, y_social, y_priority, y_random, metric_name):
    plt.figure(figsize=(9, 5))
    plt.plot(x, y_social, label='Social Algorithm')
    plt.plot(x, y_priority, label='Priority Algorithm')
    plt.plot(x, y_weight, label='Weight Algorithm')
    plt.plot(x, y_random, label='Random Algorithm')
    plt.xlabel("Number of students")
    plt.ylabel(metric_name)
    plt.title("Diversify")
    plt.suptitle("Diversify over 6 attribute")
    plt.legend(loc=(1.04, 0.80))
    plt.subplots_adjust(right=0.75)
    plt.show()
