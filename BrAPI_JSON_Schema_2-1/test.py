import os
import sys

def find_files(path):
	result = []

	for root, dir, files in os.walk(path):
		for filename in files:
			result.append(os.path.join(root, filename))
		# print("root " + root)
		# print("dir:\n")
		# print(dir)
		# print("files:\n")
		# print(files)

	return result

for res in find_files(sys.argv[1]):
	print(res)