import simpy
import numpy as np
import json
from simulation import HospitalSimulation
from monitoring import Monitor
from analysis import calculate_point_estimates, calculate_confidence_intervals


def run_simulation(config, warm_up, duration, seed=None):
    env = simpy.Environment()
    hospital = HospitalSimulation(env, config, seed=seed)
    monitor = Monitor(hospital)
    env.process(hospital.generate_patients(warm_up))
    env.process(monitor.monitor_queues())
    env.run(until=duration)
    return monitor


def collect_samples(config, runs, warm_up, duration):
    queue_lengths = []
    blocking_probabilities = []

    for i in range(runs):
        monitor = run_simulation(config, warm_up, duration, seed=i)
        queue_lengths.append(np.mean(monitor.hospital.queue_lengths["preparation"]))
        blocking_probabilities.append(monitor.calculate_blocking_probability())

    return queue_lengths, blocking_probabilities


if __name__ == "__main__":
    # Load configurations
    with open("config.json", "r") as file:
        base_config = json.load(file)

    # Configurations for testing
    configurations = {
        "3p4r": {**base_config, "PREPARATION_UNITS": 3, "RECOVERY_UNITS": 4},
        "3p5r": {**base_config, "PREPARATION_UNITS": 3, "RECOVERY_UNITS": 5},
        "4p5r": {**base_config, "PREPARATION_UNITS": 4, "RECOVERY_UNITS": 5},
    }

    warm_up_time = 200
    simulation_time = 1200
    runs = 20

    results = {}
    for config_name, config in configurations.items():
        queue_lengths, blocking_probabilities = collect_samples(config, runs, warm_up_time, simulation_time)
        results[config_name] = {
            "queue_lengths": queue_lengths,
            "blocking_probabilities": blocking_probabilities,
        }

    # Analysis
    for config_name, data in results.items():
        print(f"\nResults for {config_name}:")
        mean_q, ci_q = calculate_point_estimates(data["queue_lengths"]), calculate_confidence_intervals(data["queue_lengths"])
        mean_bp, ci_bp = calculate_point_estimates(data["blocking_probabilities"]), calculate_confidence_intervals(data["blocking_probabilities"])
        print(f"Queue Lengths: Mean=({float(mean_q[0]):.2f}, {float(mean_q[1]):.2f}), "
      f"95% CI=({float(ci_q[0]):.2f}, {float(ci_q[1]):.2f})")
        print(f"Blocking Probabilities: Mean=({float(mean_bp[0]):.2f}, {float(mean_bp[1]):.2f}), "
      f"95% CI=({float(ci_bp[0]):.2f}, {float(ci_bp[1]):.2f})")
