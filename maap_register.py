from maap.maap import MAAP
maap = MAAP()

# response = maap.getQueues()
response = maap.register_algorithm_from_yaml_file("s1_algorithm.yml")
print(response.text)
