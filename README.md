# TIES481-Simulation-Group-2


## Hospital Simulation Project

This project simulates patient flow through a hospital system with three stages:
1. Preparation
2. Operation
3. Recovery

The simulation tracks patient flow, queue lengths, and the utilization of resources (e.g., operating theaters).

## Features
- Simulates exponential arrival and service times for patients.
- Tracks queue lengths and utilization over time.
- Outputs visualizations for queue dynamics.

## Requirements
- Python 3.8+
- Install dependencies using the provided `requirements.txt` file.

Install the dependencies with:
```bash
pip install -r requirements.txt
```

## Configuration
The simulation parameters are stored in a `config.json` file:
```json
{
    "SIMULATION_TIME": 1000,
    "INTERARRIVAL_TIME": 25,
    "PREPARATION_UNITS": 3,
    "OPERATION_UNITS": 1,
    "RECOVERY_UNITS": 3,
    "PREPARATION_TIME": 40,
    "OPERATION_TIME": 20,
    "RECOVERY_TIME": 40
}
```

## Usage
Run the simulation:
```bash
python Assignment_2.py

python Assignment_3.py

python Assignment_4.py
```

## Output
- Console logs for patient lifecycle.
- Average queue lengths and operating theater utilization.
- A plot of queue lengths over time.

