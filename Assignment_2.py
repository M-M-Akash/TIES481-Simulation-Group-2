import simpy
import random
import json
import matplotlib.pyplot as plt


class HospitalSimulation:
    """
    Simulates patient flow through a hospital with preparation, operation, and recovery phases.

    Attributes:
        env (simpy.Environment): The simulation environment.
        interarrival_time (float): Mean interarrival time between patients.
        preparation (simpy.Resource): Resource representing preparation units.
        operating_theater (simpy.Resource): Resource representing operating theaters.
        recovery (simpy.Resource): Resource representing recovery units.
        prep_time (float): Mean preparation time per patient.
        op_time (float): Mean operation time per patient.
        recovery_time (float): Mean recovery time per patient.
        queue_lengths (dict): Tracks queue lengths over time.
        time_snapshots (list): Records time points for monitoring queue lengths.
        theater_busy_times (list): Stores durations of operating theater usage.
        theater_busy_start (float): Start time when the theater becomes busy.
    """
    
    def __init__(self, env, num_preparation, num_operating_theater, num_recovery, interarrival_time, prep_time, op_time, recovery_time):
        self.env = env
        self.interarrival_time = interarrival_time
        self.preparation = simpy.Resource(env, capacity=num_preparation)
        self.operating_theater = simpy.Resource(env, capacity=num_operating_theater)
        self.recovery = simpy.Resource(env, capacity=num_recovery)
        self.prep_time = prep_time
        self.op_time = op_time
        self.recovery_time = recovery_time
        self.queue_lengths = {"preparation": [], "operation": [], "recovery": []}
        self.time_snapshots = []
        self.theater_busy_times = []
        self.theater_busy_start = None

    def theater_busy(self):
        """Marks the operating theater as busy and starts tracking time."""
        if self.theater_busy_start is None:
            self.theater_busy_start = self.env.now

    def theater_idle(self):
        """Marks the operating theater as idle and stops tracking time."""
        if self.theater_busy_start is not None:
            busy_duration = self.env.now - self.theater_busy_start
            self.theater_busy_times.append(busy_duration)
            self.theater_busy_start = None

    def preparation_process(self, patient_id, prep_time):
        """Simulates the preparation phase for a patient."""
        with self.preparation.request() as request:
            yield request
            print(f"{self.env.now}: Patient {patient_id} enters preparation")
            yield self.env.timeout(prep_time)
            print(f"{self.env.now}: Patient {patient_id} leaves preparation")

    def operation_process(self, patient_id, op_time):
        """Simulates the operation phase for a patient."""
        with self.operating_theater.request() as request:
            yield request
            self.theater_busy()
            print(f"{self.env.now}: Patient {patient_id} enters operation")
            yield self.env.timeout(op_time)
            print(f"{self.env.now}: Patient {patient_id} leaves operation")
            self.theater_idle()

    def recovery_process(self, patient_id, recovery_time):
        """Simulates the recovery phase for a patient."""
        with self.recovery.request() as request:
            yield request
            print(f"{self.env.now}: Patient {patient_id} enters recovery")
            yield self.env.timeout(recovery_time)
            print(f"{self.env.now}: Patient {patient_id} leaves recovery")

    def patient_lifecycle(self, patient_id):
        """
        Defines the complete lifecycle of a patient, including preparation, operation, and recovery.
        """
        preparation_time = random.expovariate(1 / self.prep_time)
        operation_time = random.expovariate(1 / self.op_time)
        recovery_stage_time = random.expovariate(1 / self.recovery_time)

        print(f"{self.env.now}: Patient {patient_id} arrives")
        yield self.env.process(self.preparation_process(patient_id, preparation_time))
        yield self.env.process(self.operation_process(patient_id, operation_time))
        yield self.env.process(self.recovery_process(patient_id, recovery_stage_time))
        print(f"{self.env.now}: Patient {patient_id} discharged")

    def monitor_queues(self):
        """
        Monitors and records the lengths of the queues for preparation, operation, and recovery.
        """
        while True:
            self.time_snapshots.append(self.env.now)
            self.queue_lengths["preparation"].append(len(self.preparation.queue))
            self.queue_lengths["operation"].append(len(self.operating_theater.queue))
            self.queue_lengths["recovery"].append(len(self.recovery.queue))
            yield self.env.timeout(5)

    def generate_patients(self):
        """
        Generates patients arriving at the hospital at exponential interarrival times.
        """
        patient_id = 0
        while True:
            yield self.env.timeout(random.expovariate(1 / self.interarrival_time))
            self.env.process(self.patient_lifecycle(patient_id))
            patient_id += 1

    def theater_utilization(self):
        """
        Calculates the utilization rate of the operating theater.
        Returns:
            float: Utilization percentage of the operating theater.
        """
        theater_utilization = (sum(self.theater_busy_times) / self.env.now if self.env.now > 0 else 0)
        return theater_utilization


# Parameters

def load_json_config(file_path):
    """Loads configuration parameters from a JSON file."""
    with open(file_path, "r") as f:
        return json.load(f)


config = load_json_config("config.json")

SIMULATION_TIME = config['SIMULATION_TIME']
INTERARRIVAL_TIME = config['INTERARRIVAL_TIME']
PREPARATION_UNITS = config['PREPARATION_UNITS']
OPERATION_UNITS = config['OPERATION_UNITS']
RECOVERY_UNITS = config['RECOVERY_UNITS']
PREP_TIME = config['PREPARATION_TIME']
OP_TIME = config['OPERATION_TIME']
RECOVERY_TIME = config['RECOVERY_TIME']

# Simulation environment
env = simpy.Environment()
hospital = HospitalSimulation(
    env,
    num_preparation=PREPARATION_UNITS,
    num_operating_theater=OPERATION_UNITS,
    num_recovery=RECOVERY_UNITS,
    interarrival_time=INTERARRIVAL_TIME,
    prep_time=PREP_TIME,
    op_time=OP_TIME,
    recovery_time=RECOVERY_TIME,
)

# Start processes
env.process(hospital.generate_patients())
env.process(hospital.monitor_queues())

# Run simulation
env.run(until=SIMULATION_TIME)

# Display average queue lengths
print("\nAverage Queue Lengths:")
for phase, lengths in hospital.queue_lengths.items():
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    print(f"{phase.capitalize()}: {avg_length:.2f}")

print(f"Operating Theater Utilization: {hospital.theater_utilization():.2%}")

# Visualization
plt.figure(figsize=(10, 6))
plt.plot(hospital.time_snapshots, hospital.queue_lengths["preparation"], label="Preparation Queue")
plt.plot(hospital.time_snapshots, hospital.queue_lengths["operation"], label="Operation Queue")
plt.plot(hospital.time_snapshots, hospital.queue_lengths["recovery"], label="Recovery Queue")
plt.xlabel("Time")
plt.ylabel("Queue Length")
plt.title("Queue Lengths Over Time")
plt.legend()
plt.grid()
plt.show()

