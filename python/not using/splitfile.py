import pandas as pd

# File paths
input_file_path = r"C:\Users\ashle\Documents\Projects\hockey\tables\futureGameProbability.csv"
output_directory = r"C:\Users\ashle\Documents\Projects\hockey\tables"
rows_per_file = 500000  # Define the max rows per file

# Load the CSV file in chunks
for i, chunk in enumerate(pd.read_csv(input_file_path, chunksize=rows_per_file)):
    # Define the output file path with numbering
    output_file_path = f"{output_directory}/futureGameProbability_part_{i+1}.csv"
    chunk.to_csv(output_file_path, index=False)
    print(f"Saved chunk {i+1} to {output_file_path}")

print("File splitting completed.")
