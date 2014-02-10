TradingBot
==========
A strategy based on GD algorithm as described in: "Steven Gjerstad and John Dickhaut (1998) 
'Price Formation in Double Auctions. Games and Economic Behaviour', 22(1):1 – 29, 1998."

This is the subclass of the Trader class in BSE.py. To use it, just copy whole structure
directly to Trader class. Then add our trader in trader_type() function under populate_market().

All methods mentioned in our report has been applied to the trader, which are:

1. History limitation
2. Time-based profit expectation
3. Best-guess price
4. Profit reduction

Each of above feature was coded as a function, as it is possible to add or remove
any of them during experiments
