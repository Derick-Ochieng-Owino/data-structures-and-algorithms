# Sorts from lowest value to the highest vale
my_array = [23,45,67,43,22,12,89,76]

n = len(my_array)
for i in range(n-1):
    for j in range(n-i-1):
        if my_array[j] > my_array[j+1]:
            my_array[j], my_array[j+1] = my_array[j+1], my_array[j]

for i in range(n):
    print(my_array[i])