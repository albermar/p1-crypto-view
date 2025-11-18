#the router
#the one who receives requests from outside and calls the services
#english table only:
'''
| File                           | Rol         | What it does                               | What it does NOT do  |
| ----------------------------   | ----------- | --------------------------------------     | -------------------- |
| 🟣 `coingecko_client.py`      | Messenger   | Calls CoinGecko, fetches JSON               | Does not clean, decide |
| 🟡 `coingecko_normalizer.py`  | Processor   | Cleans and transforms data                  | Does not call APIs        |
| 🟢 `coingecko_service.py`     | Brain       | Orchestrates: client → normalizer → model   | Does not receive requests   |
| 🧩 `models/*.py`              | Final dish  | Defines JSON structure                      | No logic            |
| 🟠 Router                     | Waiter      | Receives inputs, calls the service          | No logic or APIs    |
'''