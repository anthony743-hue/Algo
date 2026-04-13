def permutation(s):
    n = len(s)
    if n == 1:
        return s

    arr = []    
    # print(s)
    for i in range(0, n):
        temp_arr = s[:i] + s[i+1:] 
        print(temp_arr)
        t = permutation(temp_arr)
        # print(t)
        for j in t:
            temp = s[i] + j
            arr.append(temp)
    return arr

def allWords(A,res,lst=[],n=0) -> None:
    if n == 0:
        res.append(lst)
        return

    for a in A:
        temp = lst + [a]
        allWords(A,res,temp,n - 1)


A = "ABC"
res = []
n = 3
allWords(A=A, res=res, n=3)
print(res)