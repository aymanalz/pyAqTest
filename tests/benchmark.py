import pyAqTest
import time

ini_filename = r"C:\workspace\projects\pump_tests\benchmark\benchmark.ini"
batch = pyAqTest.Batch_Processing(config_obj=ini_filename)
time1 = time.time()
batch.run_batch()
batch.generate_html_report()
time2 = time.time()
print(f"Time taken: {time2 - time1} seconds")