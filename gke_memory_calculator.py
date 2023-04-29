import argparse
from typing import Tuple


def gb_to_gib(gb: float) -> float:
    return gb * (1000 ** 3) / (1024 ** 3)


def container_streaming_reserved_memory(total_memory_gib: float, verbose: bool = False) -> float:
    reserved_memory = 0

    if total_memory_gib <= 1:
        reserved_memory = 0
        if verbose:
            print(
                "Machine has less than 1 GiB of memory, no additional memory reserved for container streaming")
    elif total_memory_gib <= 4:
        reserved_memory = 0.10 * total_memory_gib
        if verbose:
            print(
                f"Machine has {total_memory_gib} GiB of memory, reserving 10% of the first 4 GiB for container streaming")
    elif total_memory_gib <= 8:
        reserved_memory = 0.10 * 4 + 0.08 * (total_memory_gib - 4)
        if verbose:
            print(
                f"Machine has {total_memory_gib} GiB of memory, reserving 10% of the first 4 GiB and 8% of the next 4 GiB for container streaming")
    elif total_memory_gib <= 16:
        reserved_memory = 0.10 * 4 + 0.08 * 4 + 0.04 * (total_memory_gib - 8)
        if verbose:
            print(
                f"Machine has {total_memory_gib} GiB of memory, reserving 10% of the first 4 GiB, 8% of the next 4 GiB, and 4% of the next 8 GiB for container streaming")
    elif total_memory_gib <= 128:
        reserved_memory = 0.10 * 4 + 0.08 * 4 + \
            0.04 * 8 + 0.024 * (total_memory_gib - 16)
        if verbose:
            print(f"Machine has {total_memory_gib} GiB of memory, reserving 10% of the first 4 GiB, 8% of the next 4 GiB, 4% of the next 8 GiB, and 2.4% of the next 112 GiB for container streaming")
    else:
        reserved_memory = 0.10 * 4 + 0.08 * 4 + 0.04 * 8 + \
            0.024 * 112 + 0.008 * (total_memory_gib - 128)
        if verbose:
            print(f"Machine has {total_memory_gib} GiB of memory, reserving 10% of the first 4 GiB, 8% of the next 4 GiB, 4% of the next 8 GiB, 2.4% of the next 112 GiB, and 0.8% of any memory above 128 GiB for container streaming")

    return reserved_memory


def standard_gke_reserved_memory(total_memory_gib: float, verbose: bool = False) -> float:
    reserved_memory = 0

    if total_memory_gib <= 1:
        reserved_memory = 255 / 1024
        if verbose:
            print("Machine has less than 1 GiB of memory, reserving 255 MiB")
    elif total_memory_gib <= 4:
        reserved_memory = 0.25 * total_memory_gib
        if verbose:
            print(
                f"Machine has {total_memory_gib} GiB of memory, reserving 25% of the first 4 GiB")
    elif total_memory_gib <= 8:
        reserved_memory = 0.25 * 4 + 0.20 * (total_memory_gib - 4)
        if verbose:
            print(
                f"Machine has {total_memory_gib} GiB of memory, reserving 25% of the first 4 GiB and 20% of the next 4 GiB")
    elif total_memory_gib <= 16:
        reserved_memory = 0.25 * 4 + 0.20 * 4 + 0.10 * (total_memory_gib - 8)
        if verbose:
            print(
                f"Machine has {total_memory_gib} GiB of memory, reserving 25% of the first 4 GiB, 20% of the next 4 GiB, and 10% of the next 8 GiB")
    elif total_memory_gib <= 128:
        reserved_memory = 0.25 * 4 + 0.20 * 4 + \
            0.10 * 8 + 0.06 * (total_memory_gib - 16)
        if verbose:
            print(
                f"Machine has {total_memory_gib} GiB of memory, reserving 25% of the first 4 GiB, 20% of the next 4 GiB, 10% of the next 8 GiB, and 6% of the next 112 GiB")
    else:
        reserved_memory = 0.25 * 4 + 0.20 * 4 + 0.10 * 8 + \
            0.06 * 112 + 0.02 * (total_memory_gib - 128)
        if verbose:
            print(f"Machine has {total_memory_gib} GiB of memory, reserving 25% of the first 4 GiB, 20% of the next 4 GiB, 10% of the next 8 GiB, 6% of the next 112 GiB, and 2% of any memory above 128 GiB")

    reserved_memory += (100 / 1024)  # Add 100 MiB for Pod eviction

    if verbose:
        print("Reserving an additional 100 MiB for Pod eviction")

    return reserved_memory


def parse_arguments() -> Tuple[float, bool, str]:
    parser = argparse.ArgumentParser(
        description="Calculate allocatable memory in a GKE node")
    parser.add_argument("total_memory", type=float,
                        help="Total memory in GB or GiB")
    parser.add_argument("--unit", choices=["GB", "GiB"], default="GiB",
                        help="Unit of the total memory (default: GiB)")
    parser.add_argument("--streaming", action="store_true",
                        help="Consider container streaming reservations")

    args = parser.parse_args()

    return args.total_memory, args.streaming, args.unit


def main():
    total_memory, consider_streaming, unit = parse_arguments()
    if unit == "GB":
        total_memory = gb_to_gib(total_memory)

    std_reserved_memory = standard_gke_reserved_memory(
        total_memory, verbose=True)
    print(f"Standard GKE reserved memory: {std_reserved_memory:.4f} GiB")

    reserved_memory = std_reserved_memory
    if consider_streaming:
        streaming_reserved_memory = container_streaming_reserved_memory(
            total_memory, verbose=True)
        print(
            f"Container streaming reserved memory: {streaming_reserved_memory:.4f} GiB")
        reserved_memory += streaming_reserved_memory

    print(f"Total reserved memory: {reserved_memory:.4f} GiB")

    allocatable_memory_gib = total_memory - reserved_memory
    print(f"Allocatable memory: {allocatable_memory_gib:.4f} GiB")


if __name__ == "__main__":
    main()
