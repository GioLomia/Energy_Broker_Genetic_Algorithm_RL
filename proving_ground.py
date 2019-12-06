import pandas

df=pandas.read_csv("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Code_ground_zero.csv",index_col=0,header=0)
df.index=df.index[::-1]
print(df.iloc[:].iloc[::-1])