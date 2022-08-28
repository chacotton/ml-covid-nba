# ml-covid-nba

### Objective
Quantitatively analyze the impact of COVID-19 infections on the outcome of games in the National Basketball Association (NBA).   
##### Process
Deploy two machine learning models, one to predict the outcome of games and one the predict the 'healthiness' of players that are returning from a COVID-19 infection. The models will use periodically collected data to predict the successive 1-3 days of outcomes as well as analyze past games. This analysis will be displayed on a webpage optimized for data analytics.

### Repo Rules
* Make all updates through Pull Requests
  * this ensures there's a record of your code submissions
* Automatic unit tests are run on PR
  * do not override test pass requirement to make push
* Make separate branch for all issues
* Close all code based issues with a PR
* Move the status of issues to in-progress when working
* Do NOT change issue priority
* Do NOT mark issue as 'skip'

### Repo Structure

2 Production Folders
* data_ingestion
* modeling

Production folder structure (required items)
* test folder (pytest test classes, run automatically)
* main.py (script entrypoint)
* dockerfile 
* requirements.txt

Other Folders will not go into production




