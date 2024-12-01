import matplotlib.pyplot as plt


def plot_queues(time_snapshots, queue_lengths):
    plt.figure(figsize=(10, 6))
    plt.plot(time_snapshots, queue_lengths["preparation"], label="Preparation Queue")
    plt.plot(time_snapshots, queue_lengths["operation"], label="Operation Queue")
    plt.plot(time_snapshots, queue_lengths["recovery"], label="Recovery Queue")
    plt.xlabel("Time")
    plt.ylabel("Queue Length")
    plt.title("Queue Lengths Over Time")
    plt.legend()
    plt.grid()
    plt.show()
