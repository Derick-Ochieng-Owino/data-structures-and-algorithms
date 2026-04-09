nums = [23,56,76,54,98,9,34,12]
#find smallest
smallest = nums[0]

for i in range(len(nums)):
    for j in range(len(nums)):
        if smallest >= nums[i]:
            smallest = nums[i]
        nums[j] = smallest


print(smallest)

