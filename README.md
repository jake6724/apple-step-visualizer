# Apple Step Count Visualizer
![Example graph](images/image-2.png)

## How to Generate Visualization:
### 1. Export and Download Apple Health Data from iPhone
- Open the 'Health' app
- In the top-right corner, press the profile icon
- Scroll to the bottom and press "Export All Health Data"
- Press 'Export' when the popup appears and wait for the export to prepare
- Select email and email the data to yourself; after you've recieved the data, download it locally
- Locate and unzip the data

### 2. Clone this Github Repository
### 3. Insert the Data
- From the data you downloaded, copy the file found at export -> apple_health_export -> export.xml to this top level of the repository
### 4. Run the Script
- From the command line and within the repository directory, run `python3 plot_steps.py`.
