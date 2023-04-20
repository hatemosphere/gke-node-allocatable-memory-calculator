# gke-node-allocatable-memory-calculator

GKE Memory Calculator is a command-line utility to calculate allocatable memory in a Google Kubernetes Engine (GKE) node, taking into account standard GKE memory reservations and optional container streaming reservations.

## Requirements

- Python 3.6 or higher

## Usage

To use the GKE Memory Calculator, run the `gke_memory_calculator.py` script with the total memory in GiB as the first argument. Optionally, include the `--streaming` flag to consider container streaming reservations.

### Example

Calculate allocatable memory with standard GKE reservations for a node with 150 GiB of total memory:

```bash
python gke_memory_calculator.py 150
```

Output:

```bash
Allocatable memory: 118.564 GiB
```

Calculate allocatable memory with standard GKE reservations and container streaming reservations for a node with 150 GiB of total memory:

```bash
python gke_memory_calculator.py 150 --streaming
```

Output:

```bash
Allocatable memory: 116.051328 GiB
```
