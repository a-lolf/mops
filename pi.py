import pandas as pd
import io

# Step 1: Parse the text into a DataFrame
text = """Class Item                           Status     Measurement
Temp  PEM 0                          OK         35 degrees C / 95 degrees F
      PEM 1                          OK         35 degrees C / 95 degrees F
      PEM 2                          OK         35 degrees C / 95 degrees F
      PEM 3                          OK         35 degrees C / 95 degrees F
      Routing Engine 0               OK         30 degrees C / 86 degrees F
      Routing Engine 0 CPU           OK         46 degrees C / 114 degrees F
      Routing Engine 1               OK         29 degrees C / 84 degrees F
      Routing Engine 1 CPU           OK         42 degrees C / 107 degrees F
      CB 0 Intake                    OK         31 degrees C / 87 degrees F
      CB 0 Exhaust A                 OK         28 degrees C / 82 degrees F
      CB 0 Exhaust B                 OK         37 degrees C / 98 degrees F
      CB 0 ACBC                      OK         35 degrees C / 95 degrees F
      CB 0 XF A                      OK         48 degrees C / 118 degrees F
      CB 0 XF B                      OK         46 degrees C / 114 degrees F
      CB 1 Intake                    OK         30 degrees C / 86 degrees F
      CB 1 Exhaust A                 OK         28 degrees C / 82 degrees F
      CB 1 Exhaust B                 OK         38 degrees C / 100 degrees F
      CB 1 ACBC                      OK         35 degrees C / 95 degrees F
      CB 1 XF A                      OK         48 degrees C / 118 degrees F
      CB 1 XF B                      OK         46 degrees C / 114 degrees F
      FPC 0 Intake                   OK         37 degrees C / 98 degrees F
      FPC 0 Exhaust A                OK         35 degrees C / 95 degrees F
---(more)---
                                        
      FPC 0 Exhaust B                OK         54 degrees C / 129 degrees F
      FPC 0 XL TSen                  OK         55 degrees C / 131 degrees F
      FPC 0 XL Chip                  OK         49 degrees C / 120 degrees F
      FPC 0 XL_XR0 TSen              OK         55 degrees C / 131 degrees F
      FPC 0 XL_XR0 Chip              OK         52 degrees C / 125 degrees F
      FPC 0 XL_XR1 TSen              OK         55 degrees C / 131 degrees F
      FPC 0 XL_XR1 Chip              OK         54 degrees C / 129 degrees F
      FPC 0 XQ TSen                  OK         55 degrees C / 131 degrees F
      FPC 0 XQ Chip                  OK         46 degrees C / 114 degrees F
      FPC 0 XQ_XR0 TSen              OK         55 degrees C / 131 degrees F
      FPC 0 XQ_XR0 Chip              OK         49 degrees C / 120 degrees F
      FPC 0 XM TSen                  OK         55 degrees C / 131 degrees F
      FPC 0 XM Chip                  OK         65 degrees C / 149 degrees F
      FPC 0 XF TSen                  OK         55 degrees C / 131 degrees F
      FPC 0 XF Chip                  OK         72 degrees C / 161 degrees F
      FPC 0 PLX PCIe Switch TSen     OK         40 degrees C / 104 degrees F
      FPC 0 PLX PCIe Switch Chip     OK         41 degrees C / 105 degrees F
      FPC 0 Aloha FPGA 0 TSen        OK         40 degrees C / 104 degrees F
      FPC 0 Aloha FPGA 0 Chip        OK         57 degrees C / 134 degrees F
      FPC 0 Aloha FPGA 1 TSen        OK         40 degrees C / 104 degrees F
      FPC 0 Aloha FPGA 1 Chip        OK         67 degrees C / 152 degrees F
      FPC 1 Intake                   OK         38 degrees C / 100 degrees F
      FPC 1 Exhaust A                OK         38 degrees C / 100 degrees F
---(more 63%)---
                                        
      FPC 1 Exhaust B                OK         60 degrees C / 140 degrees F
---(more 64%)---
                                        
      FPC 1 XL TSen                  OK         62 degrees C / 143 degrees F
      FPC 1 XL Chip                  OK         53 degrees C / 127 degrees F
      FPC 1 XL_XR0 TSen              OK         62 degrees C / 143 degrees F
      FPC 1 XL_XR0 Chip              OK         55 degrees C / 131 degrees F
      FPC 1 XL_XR1 TSen              OK         62 degrees C / 143 degrees F
      FPC 1 XL_XR1 Chip              OK         58 degrees C / 136 degrees F
      FPC 1 XQ TSen                  OK         62 degrees C / 143 degrees F
      FPC 1 XQ Chip                  OK         49 degrees C / 120 degrees F
      FPC 1 XQ_XR0 TSen              OK         62 degrees C / 143 degrees F
      FPC 1 XQ_XR0 Chip              OK         52 degrees C / 125 degrees F
      FPC 1 XM TSen                  OK         62 degrees C / 143 degrees F
      FPC 1 XM Chip                  OK         71 degrees C / 159 degrees F
      FPC 1 XF TSen                  OK         62 degrees C / 143 degrees F
      FPC 1 XF Chip                  OK         77 degrees C / 170 degrees F
      FPC 1 PLX PCIe Switch TSen     OK         41 degrees C / 105 degrees F
      FPC 1 PLX PCIe Switch Chip     OK         42 degrees C / 107 degrees F
      FPC 1 Aloha FPGA 0 TSen        OK         41 degrees C / 105 degrees F
      FPC 1 Aloha FPGA 0 Chip        OK         62 degrees C / 143 degrees F
      FPC 1 Aloha FPGA 1 TSen        OK         41 degrees C / 105 degrees F
      FPC 1 Aloha FPGA 1 Chip        OK         73 degrees C / 163 degrees F
Fans  Top Rear Fan                   OK         Spinning at intermediate-speed
      Bottom Rear Fan                OK         Spinning at intermediate-speed
      Top Middle Fan                 OK         Spinning at intermediate-speed
---(more 95%)---
                                        
      Bottom Middle Fan              OK         Spinning at intermediate-speed
---(more 97%)---
                                        
      Top Front Fan                  OK         Spinning at intermediate-speed
      Bottom Front Fan               OK         Spinning at intermediate-speed"""

# Use StringIO to simulate a file-like object for pandas to read from
data = io.StringIO(text)

# Read the data into a DataFrame
df = pd.read_csv(data, sep='\s{2,}', engine='python', header=0)

# Step 2: Clean and organize the data
# Forward fill the 'Class' column to fill in missing values
# df['Class'] = df['Class'].ffill()

# Step 3: Iterate through the DataFrame
for index, row in df.iterrows():
    print(f"{index} - {row}")
    print("--------")