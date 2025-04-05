#!/usr/bin/python3

"""
A script to split a large CSV file into smaller, balanced files based on their data size.
Objective: Solve the problem defined at https://sadservers.com/newserver/minneapolis-2

Note: Refer to ../notes/break_a_csv_file_2.md for additional context.
"""

import heapq as heap  # Importing heapq to utilize the min-heap functionality for balancing data distribution.

class CSV:
    """
    A class representing a CSV file with methods to manage its contents and track metadata.

    Attributes:
    ----------
    fileName : str
        The name of the CSV file.
    dataSize : int
        Total size of the data stored in the file (excluding newline characters).
    lineCount : int
        Number of lines in the file.
    data : list
        List storing the lines of data for the file.

    Methods:
    --------
    addLine(line: str, size: int):
        Adds a new line to the CSV file and updates metadata.
    write():
        Writes the accumulated data to the file.
    """
    def __init__(self, fileName):
        self.fileName = fileName
        self.dataSize = 0  # Tracks the total size of data in bytes.
        self.lineCount = 0  # Tracks the number of lines in the file.
        self.data = []  # Stores the actual lines of data.

    # Comparison methods to facilitate heap operations.
    def __eq__(self, other):
        return self.dataSize == other.dataSize

    def __lt__(self, other):
        return self.dataSize < other.dataSize

    def addLine(self, line, size):
        """
        Adds a line of data to the CSV file.

        Parameters:
        ----------
        line : str
            The content of the line to add.
        size : int
            The size of the line in bytes.
        """
        self.data.append(line)
        self.dataSize += size
        self.lineCount += 1

    def write(self):
        """
        Writes all accumulated lines of data to the specified file.
        """
        with open(self.fileName, "w") as file:
            file.write("".join(self.data))

# Create a list of CSV file objects to hold the split data.
csvs = [CSV(f"data-0{i}.csv") for i in range(10)]  # Generate 10 CSV files named data-00.csv to data-09.csv.

# Read the original data from the source file.
with open("/home/admin/data.csv") as file:
    lines = file.readlines()

    # Add the header line to each file.
    for csv in csvs:
        csv.addLine(lines[0], len(lines[0]))  # Header is common across all files.

    # Initialize the heap for balancing data size across files.
    heap.heapify(csvs)

    # Sort the remaining lines by size in descending order for optimal distribution.
    lines = lines[1:]  # Exclude the header line.
    lines.sort(reverse=True, key=lambda line: len(line))  # Sort by line length.

    # Distribute the lines across the files using a min-heap.
    for line in lines:
        csv = heap.heappop(csvs)  # Get the file with the least data size.
        csv.addLine(line, len(line))  # Add the line to the file.
        heap.heappush(csvs, csv)  # Push the file back into the heap.
        heap.heapify(csvs)  # Re-heapify to maintain balance.

# Write the split data to individual files and print metadata for verification.
for csv in csvs:
    print(f"File: {csv.fileName}, Size: {csv.dataSize}, Lines: {csv.lineCount}")
    csv.write()
