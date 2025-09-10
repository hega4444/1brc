import duckdb
import time

def main():
    result = duckdb.query("""
        SELECT
            station,
            MIN(value) AS min_val,
            MAX(value) AS max_val,
            AVG(value) AS avg_val
        FROM read_csv(
            'data/measurements.txt',
            header=False,
            columns={'station': 'VARCHAR', 'value': 'DOUBLE'}
        )
        GROUP BY station
        ORDER BY station
    """).fetchall()

    results = []
    for station, mn, mx, avg in result:
        results.append(f"{station}={mn:.1f}/{avg:.2f}/{mx:.1f}")
    
    print("{" + ", ".join(results) + "}\n")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} s")
