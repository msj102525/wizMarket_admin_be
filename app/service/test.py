from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
import time

def get_sub_district_count(start, end):
    # 여기에 get_sub_district_count의 실제 구현을 넣습니다.
    # 현재는 단순히 sleep과 print로 대체합니다.
    print(f"Processing districts from {start} to {end}")
    time.sleep(10)  # 대체: 실제 작업 수행

def execute_task_in_thread(start, end):
    start_time = time.time()
    print(f"Execution started for range {start} to {end} at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_sub_district_count, start, end)]
        for future in futures:
            future.result()

    end_time = time.time()
    print(f"Execution finished for range {start} to {end} at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Total execution time for range {start} to {end}: {end_time - start_time} seconds")

def execute_parallel_tasks(ranges):
    start_time = time.time()
    print(f"Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    with Pool(processes=len(ranges)) as pool:
        pool.starmap(execute_task_in_thread, ranges)

    end_time = time.time()
    print(f"Execution finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"Total execution time: {end_time - start_time} seconds")

if __name__ == "__main__":
    ranges_5 = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25)]
    ranges_10 = [(0, 2.5), (2.5, 5), (5, 7.5), (7.5, 10), (10, 12.5), (12.5, 15), (15, 17.5), (17.5, 20), (20, 22.5), (22.5, 25)]

    print("Testing with 5 ranges:")
    execute_parallel_tasks(ranges_5)

    print("\nTesting with 10 ranges:")
    execute_parallel_tasks(ranges_10)
