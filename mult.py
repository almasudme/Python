X = [[2,0.5,0,0,0], [0,2,0.5,0,0], [0,0,2,0.5,0],[0,0,0,2,0.5],[0,0,0,0,2]]

Y = [[0.5,2,0,0,0], [0,0.5,2,0,0], [0,0,0.5,2,0],[0,0,0,2,0.5],[0,0,0,0,0.5]]
 
result = [[0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

def mult(X,Y):    
    for i in range(len(X)):
        for j in range(len(Y[0])):
            for k in range(len(Y)):
                result[i][j] += X[i][k] * Y[k][j]
            
    return result
    
C = mult(X,Y)
 
print(C)
