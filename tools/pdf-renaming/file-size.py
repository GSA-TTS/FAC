import re
import time

size = 0
count = 0
for line in open("census-file-listing.txt", "r"):
    # 2023-07-12 18:54:09    1340634 FACPDFs/ElectronicallyCollected-2008Plus/01309834.pdf
    m = re.match("(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\d+)\s+(FACPDFs/.*?)\n", line)
    if m:
        # print(m[3])
        count += 1
        size += int(m[3])
        # time.sleep(0.001)
print(f"{size} bytes")
print(f"{size/1000} KB")
print(f"{size/1000000} MB")
print(f"{size/1000000000} GB")

print(f"{size/1000000000000} TB")
print(count)
