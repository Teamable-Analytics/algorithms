import matplotlib.pyplot as plt


def visualize_metric(x, y_weight, y_social, y_priority, y_random, metric_name):
    plt.figure(figsize=(9, 5))
    plt.plot(x, y_social, label='Social Algorithm')
    plt.plot(x, y_priority, label='Priority Algorithm')
    plt.plot(x, y_weight, label='Weight Algorithm')
    plt.plot(x, y_random, label='Random Algorithm')
    plt.xlabel("Number of students")
    plt.ylabel(metric_name)
    plt.title("Ideal Cluster of Friends and 1 Random Enemy per Students")
    plt.suptitle("Random initial order of teams")
    plt.legend(loc=(1.04, 0.80))
    plt.subplots_adjust(right=0.75)
    plt.show()


def visualize_p_metric(x, y_priorities, y_weight, metric_name):

    plt.figure(figsize=(9, 5))

    for i, y in enumerate(y_priorities):
        plt.plot(x, y, label=f'Priority {i}')
    plt.plot(x, y_weight, label='Weight Algorithm')

    plt.xlabel("Number of students")
    plt.ylabel(metric_name)
    plt.title("Diversity females with a min of 2")
    plt.suptitle("Increase MAX_SPREAD")
    plt.legend(loc=(1.04, 0.80))
    plt.subplots_adjust(right=0.75)
    plt.show()
