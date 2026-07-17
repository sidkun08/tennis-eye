def checkLargestSize(someDict: dict):
    allRadius = []
    for i in someDict.keys():
        radius = someDict.get(i)[2]
        allRadius.append(radius)
    
    max = allRadius[0]

    num = 0
    for i in allRadius:
        if (i > max):
            max = i
            idx = num
        num+=1
    
    for i in someDict.keys():
        if num == idx:
            return i
