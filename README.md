# gke-node-allocatable-memory-calculator

GKE Memory Calculator is a command-line utility to calculate allocatable memory in a Google Kubernetes Engine (GKE) node, taking into account standard GKE memory reservations and optional container streaming reservations.

Based on the following documentation pages:

- <https://cloud.google.com/kubernetes-engine/docs/concepts/plan-node-sizes#memory_and_cpu_reservations>
- <https://cloud.google.com/kubernetes-engine/docs/how-to/image-streaming#memory_reservation_for>

## Requirements

- Python 3.6 or higher

## Usage

To use the GKE Memory Calculator, run the `gke_memory_calculator.py` script with the total memory in GiB or in GB (`--units GB`) as the first argument. Take into account that VM creation UI in GCP gives you memory size in GB, whereas at the same time, Kubernetes Pod resources specification is in GiB, etc.

Optionally, include the `--streaming` flag to consider container streaming reservations.

### Example

Calculate allocatable memory with standard GKE reservations for a node with 150 GiB of total memory:

```bash
python gke_memory_calculator.py 150
```

Output:

```bash
Machine has 150.0 GiB of memory, reserving 25% of the first 4 GiB, 20% of the next 4 GiB, 10% of the next 8 GiB, 6% of the next 112 GiB, and 2% of any memory above 128 GiB
Reserving an additional 100 MiB for Pod eviction
Standard GKE reserved memory: 9.8577 GiB
Total reserved memory: 9.8577 GiB
Allocatable memory: 140.1423 GiB
```

Calculate allocatable memory with standard GKE reservations and container streaming reservations for a node with 150 GiB of total memory:

```bash
python gke_memory_calculator.py 150 --streaming
```

Output:

```bash
Machine has 150.0 GiB of memory, reserving 25% of the first 4 GiB, 20% of the next 4 GiB, 10% of the next 8 GiB, 6% of the next 112 GiB, and 2% of any memory above 128 GiB
Reserving an additional 100 MiB for Pod eviction
Standard GKE reserved memory: 9.8577 GiB
Machine has 150.0 GiB of memory, reserving 10% of the first 4 GiB, 8% of the next 4 GiB, 4% of the next 8 GiB, 2.4% of the next 112 GiB, and 0.8% of any memory above 128 GiB for container streaming
Container streaming reserved memory: 3.9040 GiB
Total reserved memory: 13.7617 GiB
Allocatable memory: 136.2383 GiB
```
