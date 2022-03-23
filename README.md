# ml-covid-nba

### Make all updates through Pull Requests
this ensures there's a record of your code submissions

The data folder contains all .csv data files as well as data reading scripts. Please follow docstrings for usage.

The research folder should house all notebooks that test out different modeling approaches

### Instructions for created linux host for Pycharm development

Part 1 - Create linux host
* I recommend creating your own since we're limited to 1 CPU otherwise you will have to compete for resources
1. On OCI go to Compute -> Instances -> Create instance
2. a. Please name it something understandable
   b. SAVE PRIVATE KEY **This is very important**
   c. Create
       **You may need to change the shape to Intel core**
3. chmod 400 private_key
4. copy linux_setup.sh to host
   scp -i /path/to/private/key linux_setup.sh opc@public_ip_address:~/
5. ssh -i /path/to/private/key opc@public_ip_address
6. ./linux_setup
   Note: you will need your github username and a personal access token to complete this step, you will be prompted to input

Part 2 - Pycharm Setup
1. Download Toolbox from JetBrains https://www.jetbrains.com/toolbox-app/ 
2. Open Toolbox and install JetBrains Gateway (it says Beta on it, this is fine)
3. Open JetBrains Gateway and click SSH
4. Click New Connection
5. Enter info and click continue
   1. Username: opc
   2. Host: public_ip_address
   3. Pick your private key file from menu
6. Configure IDE
   1. IDE Version: find Pycharm and click download
   2. Project directory: /home/opc/ml-covid-nba

#### Jupyter notebooks don't seem to run on linux
In notebook environment on oci, you can clone the repo and use that for notebooks

