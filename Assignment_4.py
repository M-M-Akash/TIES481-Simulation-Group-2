import simpy
import numpy as np
import random
from monitoring import Monitor
import itertools
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression



class HospitalSimulation:
    def __init__(self, env, num_prep, num_recovery, interarrival_dist, prep_time_dist, recovery_time_dist, seed=None):
        random.seed(seed)
        self.env = env
        self.preparation = simpy.PriorityResource(env, num_prep)
        self.operating_theater = simpy.Resource(env, 1)
        self.recovery = simpy.Resource(env, num_recovery)
        self.queue_lengths = {"preparation": [], "operation": [], "recovery": []}
        self.interarrival_dist = interarrival_dist
        self.prep_time_dist = prep_time_dist
        self.recovery_time_dist = recovery_time_dist
        self.time_snapshots = []
        self.theater_blocked_times = []
        self.theater_busy_start = None

    def preparation_process(self, patient_id, priority):
        with self.preparation.request(priority=priority) as request:
            yield request
            yield self.env.timeout(next(self.prep_time_dist))

    def operation_process(self, patient_id):
        with self.operating_theater.request() as request:
            yield request
            self.theater_busy_start = self.env.now
            yield self.env.timeout(np.random.exponential(20))
            if len(self.recovery.queue) >= 1:
                self.theater_blocked_times.append(self.env.now - self.theater_busy_start)
            self.theater_busy_start = None

    def recovery_process(self, patient_id):
        with self.recovery.request() as request:
            yield request
            yield self.env.timeout(next(self.recovery_time_dist))

    def patient_lifecycle(self, patient_id, priority=1):
        yield self.env.process(self.preparation_process(patient_id, priority))
        yield self.env.process(self.operation_process(patient_id))
        yield self.env.process(self.recovery_process(patient_id))

    def generate_patients(self, warm_up):
        patient_id = 0
        while True:
            if self.env.now >= warm_up:
                priority = 0 if random.random() < 0.2 else 1
            else:
                priority = 1  # General patients during warm-up
            yield self.env.timeout(next(self.interarrival_dist))
            self.env.process(self.patient_lifecycle(patient_id, priority))
            patient_id += 1

# Run experiments
warm_up_time = 200
# Generators for distributions
def exponential_dist(mean):
    while True:
        yield np.random.exponential(mean)

def uniform_dist(low, high):
    while True:
        yield np.random.uniform(low, high)



def run_simulation(config, warm_up, duration, seed=None):
    env = simpy.Environment()
    hospital = HospitalSimulation(env, **config, seed=seed)
    monitor = Monitor(hospital)
    env.process(hospital.generate_patients(warm_up))
    env.process(monitor.monitor_queues())
    env.run(until=duration)
    return monitor




def run_independent_simulations(warm_up_time, duration, num_runs=10):
    all_samples = []

    selected_config = {
        "num_prep": 4,
        "num_recovery": 4,
        "interarrival_dist": exponential_dist(25),
        "prep_time_dist": exponential_dist(40),
        "recovery_time_dist": exponential_dist(40)
    }

    for run in range(num_runs):
        
        # Run simulation
        monitor = run_simulation(selected_config, warm_up_time, duration)
        
        # Take samples at evenly spaced intervals after warm-up
        length = np.mean(monitor.hospital.queue_lengths["preparation"])
        
        # Store the samples for this run
        all_samples.append(length)
    
    return all_samples

def calculate_serial_correlation(data, lag=1):
    if len(data) <= lag:
        raise ValueError("Data length must be greater than the lag.")
    
    # Create the lagged array
    original = data[:-lag]
    lagged = data[lag:]
    
    # Compute Pearson correlation
    correlation, _ = pearsonr(original, lagged)
    return correlation



results = run_independent_simulations(warm_up_time, duration=1000)
serial_corr = calculate_serial_correlation(results, lag=1)
print("Serial Correlation (lag=1):", serial_corr)





configs = [
    {"num_prep": p, "num_recovery": r, "interarrival_dist": i, "prep_time_dist": pt, "recovery_time_dist": rt}
    for p, r, i, pt, rt in itertools.product(
        [4, 5],  # Preparation units
        [4, 5],  # Recovery units
        [exponential_dist(25), exponential_dist(22.5), uniform_dist(20, 30), uniform_dist(20, 25)],  # Interarrival times
        [exponential_dist(40), uniform_dist(30, 50)],  # Preparation times
        [exponential_dist(40), uniform_dist(30, 50)],  # Recovery times
    )
]



queue_lengths = []

for j, config in enumerate(configs):
    
    monitor = run_simulation(config, warm_up_time, duration=1000)
    queue_lengths.append(np.mean(monitor.hospital.queue_lengths["preparation"]))



X = np.array([[cfg["num_prep"], cfg["num_recovery"], next(cfg["interarrival_dist"]), next(cfg["prep_time_dist"]), next(cfg["recovery_time_dist"])] for cfg in configs])
y = queue_lengths
model = LinearRegression().fit(X, y)

print("Regression coefficients:", model.coef_)
print("Regression intercept:", model.intercept_)