

class Monitor:
    def __init__(self, hospital):
        self.hospital = hospital
        self.queue_lengths = {"preparation": [], "operation": [], "recovery": []}
        self.blocked_times = []

    def monitor_queues(self, interval=5):
        while True:
            self.hospital.queue_lengths["preparation"].append(len(self.hospital.preparation.queue))
            self.hospital.queue_lengths["operation"].append(len(self.hospital.operating_theater.queue))
            self.hospital.queue_lengths["recovery"].append(len(self.hospital.recovery.queue))
            yield self.hospital.env.timeout(interval)

    def calculate_blocking_probability(self):
        total_time = self.hospital.env.now
        blocked_time = sum(self.hospital.theater_blocked_times)
        return blocked_time / total_time if total_time > 0 else 0
