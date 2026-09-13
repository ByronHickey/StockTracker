if __name__ == "__main__":
    # 1. Look up current market depth (Bids and Asks)
    quote_data = get_market_quote("VFV.TO") # Vanguard S&P 500 Index ETF (CAD)
    if quote_data:
        print(f"📈 Current Market Specs for {quote_data['ticker']}:")
        print(f"   Best Bid Price: ${quote_data['bid']} (Volume: {quote_data['bid_size']})")
        print(f"   Best Ask Price: ${quote_data['ask']} (Volume: {quote_data['ask_size']})")

    # 2. Purchase Executions (Replace with your actual 8-digit Questrade Account ID)
    MY_ACCOUNT_ID = "12345678" 
    
    # Example A: Standard Market Buy
    # place_order(MY_ACCOUNT_ID, ticker="VFV.TO", quantity=5, order_type="Market")
    
    # Example B: Strategic Limit Buy (Anchored right at the current highest Bid price)
    if quote_data and quote_data['bid']:
        target_bid = quote_data['bid']
        print(f"\nPlacing a limit buy at the active bid price: ${target_bid}")
        
        # Uncomment to use:
        # place_order(MY_ACCOUNT_ID, ticker="VFV.TO", quantity=10, order_type="Limit", price=target_bid)
