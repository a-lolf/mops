import re

text = """Slot 0:                  24 degrees C / 75 degrees F  Master
Current state            24 degrees C / 75 degrees F
Temperature                 27 degrees C / 80 degrees F
CPU temperature             29 degrees C / 80 degrees F
DRAM                      3857 MB (4096 MB installed)
Memory utilization       19 percent
5 sec CPU utilization:

User                     4 percent
Background               0 percent
Kernel                   3 percent

Interrupt                0 percent
Idle                     92 percent
1 min CPU utilization:

User                     6 percent
Background               0 percent
Kernel                   6 percent

Interrupt                1 percent
Idle                     87 percent
5 min CPU utilization:

User                     7 percent
Background               0 percent
Kernel                   7 percent

Interrupt                1 percent
Idle                     86 percent
15 min CPU utilization:

User                     7 percent
Background               0 percent
Kernel                   7 percent

Interrupt                1 percent
Idle                     86 percent"""

regex = r"(Temperature|CPU temperature)\s+(\d+) degrees C"  # Improved regex

matches = re.findall(regex, text)

temp_dict = {}  # Store in a dictionary for easy access

if matches:
    for item, temp in matches:
        temp_dict[item] = int(temp)  # Store with the label as key and int value

    print(temp_dict)
    # Access individually:
    if "Temperature" in temp_dict:
        print("Temperature:", temp_dict["Temperature"])
    if "CPU temperature" in temp_dict:
        print("CPU temperature:", temp_dict["CPU temperature"])
else:
    print("No temperature values found.")