'''
Created on 10 Dec 2012

@author: Tianbo Hao, Yan Yan, Zhanwen Xu

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
'''
class Trader_HXY(Trader):
        def __init__(self, ttype, tid, balance):

                self.tid = tid
                self.ttype = ttype
                self.balance = balance
                self.blotter = []
                self.orders = []
                # this is the transaction history recorded by this trader
                # only trading price will be recorded for each transaction
                # most recent trading price will be inserted at the begining
                # of the list
                self.history_transac = [] 
                
                
                                          
        def getorder(self, time, countdown, lob):
            
                # Get the acceptance possibility of a price existing
                # in the transaction history.
                # Params. price: target price
                def getP(price):
                        otype = self.orders[0].otype
                        # History limitation is set to 100
                        m = 100
                        
                        # if the length of history is lower than 100
                        # then set history limitation to the length
                        # of history until the length is greater than
                        #100
                        if len(self.history_transac)<100:
                                m = len(self.history_transac)
                                
                        if otype == 'Bid':
                                success = 0.0                              
                                for i in range(0,m):
                                        value = self.history_transac[i]
                                        if value<=price:                                           
                                                success+=1                                                          
                                if m == 0.0:
                                        return 0.0
                                else:
                                        return success/m
                        
                        if otype == 'Ask':
                                success = 0.0
                                for i in range(0,m):
                                        value = self.history_transac[i]
                                        if value>=price:
                                                success+=1                                  
                                                                                       
                                if m == 0.0:
                                        return 0.0
                                else:
                                        return success/m
                        
                
                    
                # Calculate expectation of a price
                # Params. price: target price
                #         profit: the profit gains by target price
                #         profit_rate: the profit rate (profit/limit price) of a target price
                def getE(price,profit,profit_rate):
                        possibility = getP(price)
                        return possibility**3*profit*profit_rate
                
                
                
                
                # Calculate the best-guess price based on known expectation
                # of each price in transaction history
                # Params. knownlist: a list of [expectation,price] for each target price
                #                    i.e. [[e1,p1],[e2,p2]...]
                #         knownbest: the highest expectation with its price in knownlist
                #                    i.e. [e,p]
                def getbgprice(knownlist,knownbest):
                        knownlist.sort(key=lambda x:x[1]) # sort by price
                        position = knownlist.index(knownbest) # position of known best price
#                        print 'kb position',position,'list len',len(knownlist)
                        kbprice = knownbest[1] # get price of know best E-price item
                        kbE = knownbest[0] # get E of know best E-price item
                        bgprice = kbprice # initialize the hidden best price to known best price
                        if position!=0 and position!=len(knownlist)-1: # if known-best price is not at first and last position in list
                                left = knownlist[position-1] # get E-price item by shifting left of 1
                                right = knownlist[position+1] # get E-price item by shifting right of 1
                                leftprice = left[1] # get price of left E-price item
                                leftE = left[0] # get E of left E-price item
                                rightprice = right[1] # get price of right E-price item
                                rightE = right[0] #get E of right E-price item
                                
                                # now calculate the best gest price (bgprice)
                                part1 = (kbE-rightE)*(leftprice**2-kbprice**2)-(leftE-kbE)*(kbprice**2-rightprice**2)
                                part2 = 2.0*((leftE-kbE)*(rightprice-kbprice)-(kbE-rightE)*(kbprice-leftprice))
                                
                                if part2 !=0:                  
                                        bgprice = part1/part2
                                        # according to assumption, bgprice should be between leftprice and rightprice
                                        if not(bgprice>leftprice and bgprice<rightprice):
                                                print 'bgprice error'
                        
                        return bgprice
                    
                    
                    
                # Calculate the quote price using geometric mean method
                # a gmprice will be returned if there was a best price
                # in LOB, otherwise the quote price will remain the same
                # Params. price: the quote price we have got so far 
                def getgmprice(price):      
                        otype = self.orders[0].otype
                        # limit price of the order
                        limitprice = self.orders[0].price
                        # quote price calculated by gemotric mean method
                        gmprice = 0
                        if otype =='Bid':
                                # best bid price in LOB at present
                                bidbestprice = lob['bids']['best']
                                if bidbestprice!=None:
                                        if bidbestprice<limitprice:
                                                gmprice = (bidbestprice*price)**(0.5)
                                        if bidbestprice>limitprice:
                                                gmprice = (limitprice*price)**(0.5)
                                        return gmprice
                                else:
                                        return price
                        if otype =='Ask':
                                # best ask price in LOB at present
                                askbestprice = lob['asks']['best']
                                if askbestprice!=None:
                                        if askbestprice>limitprice:
                                                gmprice = (askbestprice*price)**(0.5)
                                        if askbestprice<limitprice:
                                                gmprice = (limitprice*price)**(0.5)
                                        return gmprice
                                else:
                                        return price
                
                # Calculate the quote price
                def getquoteprice():
                        otype = self.orders[0].otype
                        limitprice = self.orders[0].price
                        # if the type of oder is to bid..                      
                        if otype == 'Bid':
                                profit_price = [] # structure: a list of [expectation,price]
                                temp = [] # temp list to avoid adding expectation of same price to profit_price list
                                
                                # get each target price from transaction history
                                for price in self.history_transac:
                                        # ensure a target price produces profit and its expection 
                                        # has not been calculated yet
                                        if price<limitprice and price not in temp :
                                                temp.append(price)
                                                profit = limitprice-price # profit made by target price
                                                profit_rate = float(profit)/float(limitprice) # profit rate of the target price
                                                E = getE(price,profit,profit_rate) # expectation of the target price
                                                if E!=0:
                                                        profit_price.append([E,price]) # add [E,price] to the list
                                profit_price.sort(reverse=True) # sort list from higher E to lower E
                                
                                # if profit_price contains elements, which means there existing some
                                #  price in history that can make profit
                                if len(profit_price)!=0:
                                        # get the first element in the list, which contains the highest E 
                                        # and corresponding price
                                        knownbest = profit_price[0] 
                                        # price with the highest E we have got so far, if best-guess 
                                        # method not applied
                                        kbprice = knownbest[1]
                                        
                                        # calculate the best-guess price 
                                        bgprice = getbgprice(profit_price,knownbest)
                                        
                                        # calculate the geometric mean price
                                        gmprice = getgmprice(bgprice)
                                        return gmprice
                                    
                                # if there was nothing in the list, that means none of existing price
                                # can make profit, then we quote same price as limit price
                                else: 
                                        return limitprice
                        
                        # if the type of order is to ask, similar as 'Bid' above
                        if otype == 'Ask':
                                profit_price = [] # [profit expectation,price]
                                temp = []
                                for price in self.history_transac:
                                        
                                        if price>limitprice and price not in temp :
                                                temp.append(price)
                                                profit = price - limitprice
                                                profit_rate = float(profit)/float(limitprice)
                                                E = getE(price,profit,profit_rate) 
                                                if E!=0:
                                                        profit_price.append([E,price])
                                profit_price.sort(reverse=True)
                                if len(profit_price)!=0:
                                        knownbest = profit_price[0]
                                        kbprice = knownbest[1]
                                        
                                        # calculate the best-guess price 
                                        bgprice = getbgprice(profit_price,knownbest)
                                        
                                        # calculate the geometric mean price
                                        gmprice = getgmprice(bgprice)
                                        return gmprice
                                else:
                                        return limitprice
                            
                if len(self.orders) < 1:
                        #no orders: return NULL
                        order = None
                else:
                        # get quote price
                        quoteprice = getquoteprice()
                        # pass order to LOB with quote price
                        order=Order(self.tid, self.orders[0].otype, quoteprice, self.orders[0].qty, time)

                return order


        # Every time a new order was placed in LOB, market_session() will invoke
        # respond() function of each trader. Therefore our trader will update
        # transaction history here using the LOB passed by market_session()
        # This methond is rewrite from Trader class
        def respond(self, time, lob, trade, verbose):
                
                # update transaction history
                def updatehistory():
                        # trading price
                        price = trade['price']
                        # trading quantity
                        count = trade['qty']
                        # each transaction will be recored multiple times
                        # if the quantity > 0. However in BSE, the quantity
                        # of transaction will always be 1
                        while count!=0:
                            # most recent transaction will be inserted at the beginning
                            self.history_transac.insert(0, price)
                            count -=1
                
                # if there was a transaction occurred in the market, then 
                # we update transaction history
                if trade!=None:
                        updatehistory()