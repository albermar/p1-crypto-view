#let's learn about pandas
import pandas as pd 
# Create a simple DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)
print(df)   

#Let's create a new class to sotre a point and a moment in time:

from datetime import datetime

class PricePoint:
    timestamp: datetime
    price: float
    def __init__(self, timestamp: datetime, price: float):
        self.timestamp = timestamp
        self.price = price
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int, price: float):
        self.timestamp = datetime(year, month, day, hour, minute)
        self.price = price

#is it ok the class definition above?
#Yes, the class definition looks good. It defines a PricePoint class with two attributes: timestamp and price, and includes an __init__ method to initialize these attributes when creating an instance of the class. The types of the attributes are also specified, which is helpful for clarity and type checking.

point1 = PricePoint(2025, 6, 1, 14, 56, 100.5)

print(point1.timestamp)
print(point1.price)

#now let's create a dataframe of 10 random price points
import random
price_points = []
for i in range(10):
    year = 2024
    month = 6
    day = random.randint(1, 30)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    price = round(random.uniform(50.0, 150.0), 2)
    point = PricePoint(year, month, day, hour, minute, price)
    price_points.append({'Timestamp': point.timestamp, 'Price': point.price})   
df_prices = pd.DataFrame(price_points) #we can create a dataframa from a list of class? #answer: yes, by converting each class instance to a dictionary
print(df_prices)

#now show me the 10 most used functions of pandas
# Here are 10 commonly used functions in pandas:
'''
1. pd.read_csv(): Reads a CSV file into a DataFrame.    
2. df.head(): Returns the first n rows of the DataFrame.    
3. df.tail(): Returns the last n rows of the DataFrame. 
4. df.info(): Provides a summary of the DataFrame, including data types and non-null counts.
5. df.describe(): Generates descriptive statistics of the DataFrame. for example mean, std, min, max, etc.
6. df.groupby(): Groups the DataFrame using a mapper or by a Series of columns.
7. df.merge(): Merges two DataFrames based on a common column or index.
8. df.sort_values(): Sorts the DataFrame by the values of one or more columns.
9. df.drop(): Removes rows or columns from the DataFrame.
10. df.fillna(): Fills NA/NaN values using the specified method or value.   
'''

#Let's use them in a small example
# Create a sample DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
    'Age': [25, 30, 35, 40, None],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'Salary': [70000, 80000, 90000, None, 60000]
}
df = pd.DataFrame(data)
print(df)

# 1. Read CSV (skipped as we are creating DataFrame directly)
# 2. Head
print(df.head(3))
# 3. Tail
print(df.tail(2))
# 4. Info
print(df.info())
# 5. Describe
print(df.describe())
# 6. GroupBy
print(df.groupby('City').mean(numeric_only=True)) #calculating the mean age and salary for each city
print(df.groupby('City').size()) #count of people in each city
# 7. Merge (skipped as we have only one DataFrame)
# 8. Sort Values
print(df.sort_values(by='Age'))
print(df.sort_values(by='Salary', ascending=True))
# 9. Drop
print(df.drop(columns=['City']))# this do: removes the City column
# 10. Fill NA
print(df.fillna({'Age': df['Age'].mean(), 'Salary': df['Salary'].mean()})) # filling NA values with the mean of the column
#------------------CLEAN ENDPOINT------------------#

#read csv to pandas
df = pd.read_csv("C:\\Users\\alber\\Downloads\\testcsv.csv") 
print(df.head())
print(df.describe())