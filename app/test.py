class Solution:
    def makeParityAlternating(self, nums: List[int]) -> List[int]:
        n = len(nums)
        dp = [[0]*2 for _ in range(n+1)]

        start_even = set()
        start_odd = set()

        a = start_even
        b = start_odd

        for i in range(1, n+1):
            idx = i-1
            if nums[idx] & 1:
                dp[i][1] = dp[i-1][0]
                dp[i][0] = 1 + dp[i-1][1]
                a.add(idx)
            else:
                dp[i][0] = dp[i-1][1]
                dp[i][1] = 1 + dp[i-1][0]
                b.add(idx)
            max_val = max(max_val, nums[idx])

            a, b = b, a

        start_even_count = dp[n][0] if len(nums) & 1 else dp[n][1]
        start_odd_count = dp[n][1] if len(nums) & 1 else dp[n][0]

        min_val = float("inf")
        max_val = float("-inf")

        for i in range(n):
            if i in start_even:
                max_val = max(max_val, nums[i]-1)
                min_val = min(min_val, nums[i]+1)
            else:
                max_val = max(max_val, nums[i])
                min_val = min(min_val, nums[i])
        
        start_even_diff = max_val - min_val

        min_val = float("inf")
        max_val = float("-inf")

        for i in range(n):
            if i in start_odd:
                max_val = max(max_val, nums[i]-1)
                min_val = min(min_val, nums[i]+1)
            else:
                max_val = max(max_val, nums[i])
                min_val = min(min_val, nums[i])
        
        start_odd_diff = max_val - min_val

        if start_even_count < start_odd_count:
            return [start_even_count, start_even_diff]

        if start_odd_count < start_even_count:
            return [start_odd_count, start_odd_diff]
        
        return [start_even_count, min(start_even_diff, start_odd_diff)]

