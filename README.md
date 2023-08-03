# Easy budget Telegram bot
### Description
Telegram bot for personal spending calculation during the month and any other period. 

*Easily add new spending via message to the bot:*
![New spend](https://github.com/antoncp/easy_budget_tgbot/assets/64245819/8460f97a-fa65-4775-b476-7c486ebe0082)

*Get a monthly overview of your expenses by category with each transaction explanation:*
![Monthly overview](https://github.com/antoncp/easy_budget_tgbot/assets/64245819/b63d8df4-c088-4af8-9ded-ae3a988bacd1)

*Use the default or create your own expense categories:*
![Categories Picker](https://github.com/antoncp/easy_budget_tgbot/assets/64245819/2e3f88e1-6d8f-4222-a10a-79302ddbb8b1)
### Technologies
`pyTelegramBotAPI`
`SQLite`

### How to launch the project 
- Clone the repository
```
git clone git@github.com:antoncp/easy_budget_tgbot.git
``` 
- Create and activate virtual environment
```
python3.9 -m venv venv
``` 
- Install dependencies from requirements.txt file with activated virtual environment
```
pip install -r requirements.txt
```
- Execute python command to run the bot in a polling mode 
```
python main.py
``` 