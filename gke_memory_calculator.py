import argparse
from typing import Tuple

def gke_reserved_memory(total_memory_gib: float) -> float:
    reserved_memory = 0

    if total_memory_gib <= 1:
        reserved_memory = 0
    elif total_memory_gib <= 4:
        reserved_memory = 0.10 * total_memory_gib
    elif total_memory_gib <= 8:
        reserved_memory = 0.10 * 4 + 0.08 * (total_memory_gib - 4)
    elif total_memory_gib <= 16:
        reserved_memory = 0.10 * 4 + 0.08 * 4 + 0.04 * (total_memory_gib - 8)
    elif total_memory_gib <= 128:
        reserved_memory = 0.10 * 4 + 0.08 * 4 + 0.04 * 8 + 0.024 * (total_memory_gib - 16)
    else:
        reserved_memory = 0.10 * 4 + 0.08 * 4 + 0.04 * 8 + 0.024 * 112 + 0.008 * (total_memory_gib - 128)

    return reserved_memory

def standard_gke_reserved_memory(total_memory_gib: float) -> float:
    reserved_memory = 0

    if total_memory_gib <= 1:
        reserved_memory = 255 / 1024
    elif total_memory_gib <= 4:
        reserved_memory = 0.25 * total_memory_gib
    elif total_memory_gib <= 8:
        reserved_memory = 0.25 * 4 + 0.20 * (total_memory_gib - 4)
    elif total_memory_gib <= 16:
        reserved_memory = 0.25 * 4 + 0.20 * 4 + 0.10 * (total_memory_gib - 8)
    elif total_memory_gib <= 128:
        reserved_memory = 0.25 * 4 + 0.20 * 4 + 0.10 * 8 + 0.06 * (total_memory_gib - 16)
    else:
        reserved_memory = 0.25 * 4 + 0.20 * 4 + 0.10 * 8 + 0.06 * 112 + 0.02 * (total_memory_gib - 128)

    return reserved_memory + (100 / 1024)  # Add 100 MiB for Pod eviction

def parse_arguments() -> Tuple[float, bool]:
    parser = argparse.ArgumentParser(description='Calculate allocatable memory in a GKE node.')
    parser.add_argument('total_memory_gib', type=float, help='Total memory of the node in GiB')
    parser.add_argument('--streaming', action='store_true', help='Consider container streaming reservations')
    args = parser.parse_args()
    return args.total_memory_gib, args.streaming

def main():
    total_memory_gib, consider_streaming = parse_arguments()

    reserved_memory = standard_gke_reserved_memory(total_memory_gib)
    if consider_streaming:
        reserved_memory += gke_reserved_memory(total_memory_gib)

    allocatable_memory_gib = total_memory_gib - reserved_memory
    print(f"Allocatable memory: {allocatable_memory_gib} GiB")

if __name__ == '__main__':
    main()
