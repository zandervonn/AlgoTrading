import os

def merge_subfolders_into_text(folder_path, output_file="merged_content.txt"):
	"""
	Merges the contents of all .cs files in subfolders within a given folder into a single text file,
	separating content from each subfolder with a clear header.

	Args:
		folder_path (str): The path to the main folder containing subfolders.
		output_file (str): The name of the output text file (default: merged_content.txt).
	"""
	print(f"Starting to merge files from {folder_path} into {output_file}...")

	file_count = 0

	with open(output_file, "w") as outfile:
		for root, dirs, files in os.walk(folder_path):
			for file in files:
				print(file)
				if file.endswith('.py'):
					file_path = os.path.join(root, file)
					print(f"Processing file: {file_path}")
					try:
						with open(file_path, "r") as infile:
							outfile.write(f"______________________________________{file}____________________________\n")
							outfile.write(infile.read())
							outfile.write("\n")  # Add an extra newline for spacing
						file_count += 1
					except UnicodeDecodeError:
						print(f"Error decoding file: {file_path}. Skipping...")

	print(f"Finished merging {file_count} files into {output_file}")

# Example usage
folder_path = r"C:\Users\Zander\IdeaProjects\algoTrading\src"
# folder_path = r"C:\Users\Zander\IdeaProjects\Automation-Gel\Src"
merge_subfolders_into_text(folder_path)