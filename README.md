# pennystocks
Track break-out penny stock indicators 

TRACKER BACKGROUND

While getting into pennystock trading, I noticed that some sources seem to be good indicators of short-term break-outs. I am still evaluating the prediction accuracy but it is an interesting and helpful tool to me. With the pennystock tracker you can track the following sources for now:

Stockwits Finviz (preset screener) Tradingview (if you already have screeners set up or are willing to add them) The tracker will tell you:

performance over last seven days of a stock that was picked up by one of the screeners all indicators collected for a stock With this information you can evaluate the data over time and see for yourself if you can pick up on patterns that seem to be good predictions of a short-term break-out. Cutoff price is currently set at $10 but can be altered as necessary.

WHAT YOU NEED

an alphavantage api key (available for free with 5 calls per minute and up to 500 per day) / Premium key that will not slow your code down is available for $50/month if you want to use Tradingview: personal screener setups and facebook login credentials) a selenium webdriver (here Chrome is used) a goodle spreadsheet (see below) SETUP GOOGLE SPREADSHEET FIRST

Follow the steps of this link to set up your google api and get your credentials: https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/

You can chose your own naming or use the one provided in the code (Project: Pennystock Tracker, Sheets: Summary, Stockwits, Finviz, Tradingview)

You will also need (at least) the following collumns for every sheet:

Signal, Sector, Ticker, Log_Date_t0, Log_Price_Closing_Price_t0, Change,_Log_Date, Description, Closing_Price_t0, Closing_Price_t1, Closing_Price_t2, Closing_Price_t7, Change_t0, Change_t1, Change_t2, Change_t7, Absolute_Change, t-_t0, Other_Signals, Total_Signals

SETUP

If you are outside of Germany, you will need to adjust the data consent parts of the code - skip the code if you are outside of Europe and adjust the names of the elements to your language for selenium to be able to pick them up Run the code daily (even on weekends Stockwits can generate relevant data).
