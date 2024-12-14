import simpy
import random
import numpy as np

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


# class HospitalSimulation:
#     def __init__(self, env, config, seed=None):
#         random.seed(seed)
#         self.env = env
#         self.config = config
#         self.preparation = simpy.PriorityResource(env, capacity=config["PREPARATION_UNITS"])
#         self.operating_theater = simpy.Resource(env, capacity=config["OPERATION_UNITS"])
#         self.recovery = simpy.Resource(env, capacity=config["RECOVERY_UNITS"])
#         self.queue_lengths = {"preparation": [], "operation": [], "recovery": []}
#         self.time_snapshots = []
#         self.theater_blocked_times = []
#         self.theater_busy_start = None

#     def preparation_process(self, patient_id, priority):
#         with self.preparation.request(priority=priority) as request:
#             yield request
#             yield self.env.timeout(random.expovariate(1 / self.config["PREPARATION_TIME"]))

#     def operation_process(self, patient_id):
#         with self.operating_theater.request() as request:
#             yield request
#             self.theater_busy_start = self.env.now
#             yield self.env.timeout(random.expovariate(1 / self.config["OPERATION_TIME"]))
#             if len(self.recovery.queue) >= self.config["RECOVERY_UNITS"]:
#                 self.theater_blocked_times.append(self.env.now - self.theater_busy_start)
#             self.theater_busy_start = None

#     def recovery_process(self, patient_id):
#         with self.recovery.request() as request:
#             yield request
#             yield self.env.timeout(random.expovariate(1 / self.config["RECOVERY_TIME"]))

#     def patient_lifecycle(self, patient_id, priority=1):
#         yield self.env.process(self.preparation_process(patient_id, priority))
#         yield self.env.process(self.operation_process(patient_id))
#         yield self.env.process(self.recovery_process(patient_id))

#     def generate_patients(self, warm_up):
#         patient_id = 0
#         while True:
#             if self.env.now >= warm_up:
#                 priority = 0 if random.random() < self.config["EMERGENCY_PROBABILITY"] else 1
#             else:
#                 priority = 1  # General patients during warm-up
#             yield self.env.timeout(random.expovariate(1 / self.config["INTERARRIVAL_TIME"]))
#             self.env.process(self.patient_lifecycle(patient_id, priority))
#             patient_id += 1
