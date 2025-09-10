#!/usr/bin/env python3
from multiprocessing import Pool, cpu_count
import os
import array
import time

MAX_CPU_COUNT = 11


def to_int(x: bytes) -> int:
    # Parse sign
    if x[0] == 45:  # ASCII for "-"
        sign = -1
        idx = 1
    else:
        sign = 1
        idx = 0
    # Check the position of the decimal point
    if x[idx + 1] == 46:  # ASCII for "."
        # -#.# or #.#
        # 528 == ord("0") * 11
        result = sign * ((x[idx] * 10 + x[idx + 2]) - 528)
    else:
        # -##.# or ##.#
        # 5328 == ord("0") * 111
        result = sign * ((x[idx] * 100 + x[idx + 1] * 10 + x[idx + 3]) - 5328)

    return result


def process_chunk(args):
    filename, start, end = args
    stations = {}
    with open(filename, "rb") as f:
        f.seek(start)
        remaining = end - start

        if start != 0:
            discard = f.readline()
            remaining -= len(discard)

        while remaining > 0:
            line = f.readline()
            remaining -= len(line)
            sep_pos = line.rfind(b";")
            station = line[:sep_pos]
            value = to_int(line[sep_pos + 1: -1])
            try:
                stats = stations[station]
                if value < stats[0]:
                    stats[0] = value
                if value > stats[1]:
                    stats[1] = value
                stats[2] += value
                stats[3] += 1
            except KeyError:
                stations[station] = array.array(
                    "l", [value, value, value, 1]
                )
                # [0:min, 1:max, 2:sum, 3:count]
    return stations


def merge_results(results):
    merged = {}
    for result in results:
        for station, stats in result.items():
            existing = merged.get(station)
            if existing is None:
                merged[station] = array.array("l", stats)
            else:
                # [0:min, 1:max, 2:sum, 3:count]
                if stats[0] < existing[0]:
                    existing[0] = stats[0]
                if stats[1] > existing[1]:
                    existing[1] = stats[1]
                existing[2] += stats[2]
                existing[3] += stats[3]
    return merged


def main():
    filename = "data/measurements.txt"
    file_size = os.path.getsize(filename)
    num_processes = min(cpu_count(), MAX_CPU_COUNT)
    chunk_size = file_size // num_processes

    chunks = []
    for i in range(num_processes):
        start = i * chunk_size
        end = file_size if i == num_processes - 1 else (i + 1) * chunk_size
        chunks.append((filename, start, end))

    with Pool(num_processes) as pool:
        results = pool.map(process_chunk, chunks)

    merged = merge_results(results)

    results = []
    for station_bytes in sorted(merged.keys()):
        station = station_bytes.decode()
        stats = merged[station_bytes]
        avg = stats[2] / stats[3]
        results.append(
            "%s=%.1f/%.2f/%.1f" % (station, stats[0]*0.1, avg*0.1, stats[1]*0.1)
        )

    print("{" + ", ".join(results) + "}\n")
    print(f"Processed with {num_processes} CPU cores.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} s")
