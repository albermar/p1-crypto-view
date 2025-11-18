from app_obsolete.services.coingecko_client import get_market_chart

def test_get_market_chart():
    data = get_market_chart('bitcoin', 'usd', 7)
    
    print('Type of data:', type(data))
    print('keys:', list(data.keys()))
    
    prices = data.get('prices', [])
    print("Number of price points:", len(prices))
    print("First 3 price points:")
    for point in prices[:3]:
        print(point)
        
if __name__ == "__main__":
    test_get_market_chart()
    
'''
#it returns:
    Type of data: <class 'dict'>
    keys: ['prices', 'market_caps', 'total_volumes']
    Number of price points: 169
    First 3 price points:
    [1762531274958, 100870.55029636277]
    [1762534943707, 101051.07699155441]
    [1762538489126, 101941.67780129392]
'''
#what is the first number? It is a timestamp in milliseconds since the Unix epoch (January 1, 1970).
#the __init__.py files must go in .gitignore? 
# Yes, __init__.py files are typically included in version control systems like Git. They are essential for Python packages as they indicate that the directory should be treated as a package. Therefore, they should not be added to .gitignore unless there is a specific reason to exclude them from version control.
