import re
import sys

for line in sys.stdin:
    print(f"inputed: {line.rstrip()}")

    match = re.match("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", line.rstrip())

    if match is not None:
        print("Found match")
        break

    print("Match not found")
    break

