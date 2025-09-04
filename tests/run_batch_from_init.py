import pyAqTest

ini_filename = r"C:\workspace\projects\pump_tests\pyAqTest\tests\slug_test_config.ini"
batch = pyAqTest.Batch_Processing(config_obj=ini_filename)
batch.run_batch()
batch.generate_html_report()
