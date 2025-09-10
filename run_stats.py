#!/usr/bin/env python3
import subprocess
import time


def run_pypy():
    print("🐍 Running PyPy implementation...")
    start = time.time()
    result = subprocess.run(
        ["pypy3", "test_pypy.py"], capture_output=True, text=True
    )
    end = time.time()
    print(f"🐍 \033[92mPyPy execution time: {end - start:.2f} s\033[0m\n")
    return result.stdout.strip(), result.returncode


def run_duckdb():
    print("🦆 Running DuckDB implementation...")
    start = time.time()
    result = subprocess.run(
        ["uv", "run", "python", "test_duckdb.py"], capture_output=True, text=True
    )
    end = time.time()
    print(f"🦆 \033[92mDuckDB execution time: {end - start:.2f} s\033[0m")
    return result.stdout.strip(), result.returncode


def compare_results(pypy_output, duckdb_output):
    print("\n=== COMPARISON ===")

    # Extract just the results line (first line with {})
    pypy_result = pypy_output.split("\n")[0] if pypy_output else ""
    duckdb_result = duckdb_output.split("\n")[0] if duckdb_output else ""

    if pypy_result == duckdb_result:
        print("✅ Results match!")
    else:
        print("❌ Results differ!")
        print(f"PyPy:   {pypy_result}")
        print(f"DuckDB: {duckdb_result}")


def main():
    print("=== 1BRC Performance Comparison ===\n")

    pypy_output, pypy_code = run_pypy()
    if pypy_code != 0:
        print(f"PyPy failed with code {pypy_code}")
        return

    duckdb_output, duckdb_code = run_duckdb()
    if duckdb_code != 0:
        print(f"DuckDB failed with code {duckdb_code}")
        return

    compare_results(pypy_output, duckdb_output)


if __name__ == "__main__":
    main()
