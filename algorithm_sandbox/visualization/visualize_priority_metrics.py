import matplotlib.pyplot as plt


def visualize_priority_metrics(x, priority_metrics):
    """

    Parameters
    ----------
    x: [x1, x2, ...]
    priority_metrics: [
        {'S_F': value, 'HT': value, ...},
        ...
    ]

    Returns
    -------

    """

    metrics = {}
    """
    Flat metrics:
        metrics = {
            'S_F': [value1, value2, ...]
            ...
        }
    """
    for metric in priority_metrics:
        for key, value in metric.items():
            if key not in metrics:
                metrics[key] = []
            metrics[key].append(value)

    for name, values in metrics.items():
        plt.plot(x, values, label=name)

    plt.xlabel("Number of students")
    plt.ylabel("Metric value (%)")
    plt.legend()
    plt.show()
