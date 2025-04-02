#!/usr/bin/python3

# A script to solve https://sadservers.com/newserver/minneapolis-2
# Note: ../notes/break_a_csv_file_2.md

import heapq as heap


class CSV:
    def __init__(self, fileName):
        self.fileName = fileName
        self.dataSize = 0  # without counting newline
        self.lineCount = 0
        self.data = []

    def __eq__(self, other):
        return self.dataSize == other.dataSize

    def __lt__(self, other):
        return self.dataSize < other.dataSize

    def addLine(self, line, size):
        self.data.append(line)
        self.dataSize += size
        self.lineCount += 1

    def write(self):
        with open(self.fileName, "w") as file:
            file.write("".join(self.data))


csvs = []

for i in range(10):
    csv = CSV(f"data-0{i}.csv")
    csvs.append(csv)


with open("/home/admin/data.csv") as file:
    lines = file.readlines()

    # add header
    for csv in csvs:
        csv.addLine(lines[0], len(lines[0]))

    heap.heapify(csvs)

    lines = lines[1:]
    lines.sort(reverse=True, key=lambda line: len(line))

    for line in lines:
        csv = heap.heappop(csvs)
        csv.addLine(line, len(line))
        heap.heappush(csvs, csv)
        heap.heapify(csvs)

for csv in csvs:
    print(csv.fileName, csv.dataSize, csv.lineCount)
    csv.write()
