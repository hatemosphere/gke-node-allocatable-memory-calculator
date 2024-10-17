import argparse
from collections import namedtuple
from typing import List, Tuple

MemoryTier = namedtuple('MemoryTier', ['threshold', 'percentage', 'verbose'])


def gb_to_gib(gb: float) -> float:
    return gb * (1000 ** 3) / (1024 ** 3)


def calculate_reserved_memory(total_memory_gib: float, memory_tiers: List[MemoryTier], verbose: bool = False) -> float:
    reserved_memory = 0.0
    last_threshold = 0.0

    for tier in memory_tiers:
        if total_memory_gib > tier.threshold:
            reserved_memory += tier.percentage * \
                (tier.threshold - last_threshold)
            last_threshold = tier.threshold
        else:
            reserved_memory += tier.percentage * \
                (total_memory_gib - last_threshold)
            if verbose and tier.verbose:
                print(tier.verbose.format(total_memory_gib,
                      tier.percentage * 100, tier.percentage * 100))
            break
    return reserved_memory


def parse_arguments() -> Tuple[float, bool, str]:
    parser = argparse.ArgumentParser(
        description="Calculate allocatable memory in a GKE node")
    parser.add_argument("total_memory", type=float,
                        help="Total memory in GB or GiB")
    parser.add_argument(
        "--unit", choices=["GB", "GiB"], default="GiB", help="Unit of the total memory (default: GiB)")
    parser.add_argument("--streaming", action="store_true",
                        help="Consider container streaming reservations")

    args = parser.parse_args()

    return args.total_memory, args.streaming, args.unit


def main():
    total_memory, consider_streaming, unit = parse_arguments()
    if unit == "GB":
        total_memory = gb_to_gib(total_memory)

    memory_tiers_gke = [
        MemoryTier(
            1, 255/1024, "Machine has less than 1 GiB of memory, reserving 255 MiB"),
        MemoryTier(
            4, 0.25, "Machine has {:.2f} GiB of memory, reserving {}% of the first 4 GiB"),
        MemoryTier(
            8, 0.20, "Machine has {:.2f} GiB of memory, reserving {}% of the first 4 GiB and {}% of the next 4 GiB"),
        MemoryTier(
            16, 0.10, "Machine has {:.2f} GiB of memory, reserving {}% of the first 8 GiB and {}% of the next 8 GiB"),
        MemoryTier(
            128, 0.06, "Machine has {:.2f} GiB of memory, reserving {}% of the first 16 GiB and {}% of the next 112 GiB"),
        MemoryTier(float(
            'inf'), 0.02, "Machine has {:.2f} GiB of memory, reserving {}% of any memory above 128 GiB")
    ]

    memory_tiers_streaming = [
        MemoryTier(
            1, 0, "Machine has less than 1 GiB of memory, no additional memory reserved for container streaming"),
        MemoryTier(
            4, 0.01, "Machine has {:.2f} GiB of memory, reserving {}% of the first 4 GiB for container streaming"),
        MemoryTier(
            8, 0.08, "Machine has {:.2f} GiB of memory, reserving {}% of the first 4 GiB and {}% of the next 4 GiB for container streaming"),
        MemoryTier(
            16, 0.04, "Machine has {:.2f} GiB of memory, reserving {}% of the first 8 GiB and {}% of the next 8 GiB for container streaming"),
        MemoryTier(
            128, 0.024, "Machine has {:.2f} GiB of memory, reserving {}% of the first 16 GiB and {}% of the next 112 GiB for container streaming"),
        MemoryTier(float('inf'), 0.008,
                   "Machine has {:.2f} GiB of memory, reserving {}% of any memory above 128 GiB for container streaming")
    ]

    std_reserved_memory = calculate_reserved_memory(
        total_memory, memory_tiers_gke, verbose=True)
    print(f"Standard GKE reserved memory: {std_reserved_memory:.4f} GiB")

    reserved_memory = std_reserved_memory
    if consider_streaming:
        streaming_reserved_memory = calculate_reserved_memory(
            total_memory, memory_tiers_streaming, verbose=True)
        print(
            f"Container streaming reserved memory: {streaming_reserved_memory:.4f} GiB")
        reserved_memory += streaming_reserved_memory

    reserved_memory += (100 / 1024)  # Add 100 MiB for Pod eviction
    print("Reserving an additional 100 MiB for Pod eviction")

    print(f"Total reserved memory: {reserved_memory:.4f} GiB")
    allocatable_memory_gib = total_memory - reserved_memory
    print(f"Allocatable memory: {allocatable_memory_gib:.4f} GiB")


if __name__ == "__main__":
    main()
