from data import Dataset
from data import chance_of_victory

#df = chance_of_victory.WinDataset(problem='regression', optimize=True).get_dataset()
#print(df.head(10))
#winReg = chance_of_victory.WinDataset(problem='regression', optimize=True)

def test_1():
    #regression
    df = chance_of_victory.WinDataset(problem='regression', optimize=True).get_dataset()
    #df = winReg.get_dataset()
    print(df.shape)
    print(df.isnull())
    #assert df.shape[1] == 54
    #assert df.shape[0] == 2112
    
def test_2():
    df = chance_of_victory.WinDataset(problem='classification', optimize=True).get_dataset()
    print(df.shape)
    print(df.isnull())
    #assert df.shape[1] == 54
    #assert df.shape[0] == 2112
    
    
    
    
    #target = chance_of_victory.WinDataset(problem='regression', optimize=True)._target()
    #print(target)
    #print(df._target)
    #print(df.head(10))
    #stats = chance_of_victory.WinDataset(problem='regression', optimize=True)._load_stat_tables()
    #print(stats)
    
    
'''  
def test2():
    df = chance_of_victory.WinDataset(problem='classification', optimize=True).get_dataset()
    print(df.head(10))
    
def test3():
    df = chance_of_victory.WinDataset(problem='classification', optimize=False).get_dataset()
    print(df.head(10))
    
def test4():
    df = chance_of_victory.WinDataset(problem='regression', optimize=False).get_dataset()
    print(df.head(10))
'''

    