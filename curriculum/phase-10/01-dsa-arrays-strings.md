# DSA Arrays & String Manipulation — Java Interview Patterns

## What You'll Master
- The core array patterns that appear in 80% of Java interviews
- String manipulation tricks — reverse, anagram, palindrome, sliding window
- Two-pointer and sliding window techniques
- Time and space complexity analysis for each approach

---

## Two-Pointer Technique

Used when the array is sorted or when you need to avoid O(n²) nested loops.

```java
// Pattern 1: Opposite ends — find pair with target sum
public static int[] twoSum(int[] sorted, int target) {
    int left = 0, right = sorted.length - 1;
    while (left < right) {
        int sum = sorted[left] + sorted[right];
        if (sum == target) return new int[]{left, right};
        else if (sum < target) left++;
        else right--;
    }
    return new int[]{-1, -1};
}
// Time: O(n), Space: O(1)

// Pattern 2: Same direction — remove duplicates in-place
public static int removeDuplicates(int[] nums) {
    if (nums.length == 0) return 0;
    int slow = 0;
    for (int fast = 1; fast < nums.length; fast++) {
        if (nums[fast] != nums[slow]) {
            slow++;
            nums[slow] = nums[fast];
        }
    }
    return slow + 1;
}
```

---

## Sliding Window Technique

Used for contiguous subarray/substring problems.

```java
// Fixed window — max sum of k consecutive elements
public static int maxSumFixed(int[] arr, int k) {
    int windowSum = 0;
    for (int i = 0; i < k; i++) windowSum += arr[i];

    int maxSum = windowSum;
    for (int i = k; i < arr.length; i++) {
        windowSum += arr[i] - arr[i - k]; // slide: add new, remove old
        maxSum = Math.max(maxSum, windowSum);
    }
    return maxSum;
}

// Variable window — longest substring without repeating chars
public static int lengthOfLongestSubstring(String s) {
    Map<Character, Integer> lastSeen = new HashMap<>();
    int maxLen = 0, left = 0;

    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        if (lastSeen.containsKey(c) && lastSeen.get(c) >= left) {
            left = lastSeen.get(c) + 1; // shrink window
        }
        lastSeen.put(c, right);
        maxLen = Math.max(maxLen, right - left + 1);
    }
    return maxLen;
}
// Time: O(n), Space: O(min(n, charset))
```

---

## String Patterns

```java
// Check if two strings are anagrams
public static boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    int[] freq = new int[26];
    for (char c : s.toCharArray()) freq[c - 'a']++;
    for (char c : t.toCharArray()) {
        if (--freq[c - 'a'] < 0) return false;
    }
    return true;
}

// Check if palindrome (ignoring non-alphanumeric)
public static boolean isPalindrome(String s) {
    int left = 0, right = s.length() - 1;
    while (left < right) {
        while (left < right && !Character.isLetterOrDigit(s.charAt(left))) left++;
        while (left < right && !Character.isLetterOrDigit(s.charAt(right))) right--;
        if (Character.toLowerCase(s.charAt(left)) !=
            Character.toLowerCase(s.charAt(right))) return false;
        left++; right--;
    }
    return true;
}

// Group anagrams together
public static Map<String, List<String>> groupAnagrams(String[] words) {
    Map<String, List<String>> map = new HashMap<>();
    for (String w : words) {
        char[] chars = w.toCharArray();
        Arrays.sort(chars);
        String key = new String(chars); // sorted form is the canonical key
        map.computeIfAbsent(key, k -> new ArrayList<>()).add(w);
    }
    return map;
}
```

---

## Array Rotation & Prefix Sum

```java
// Rotate array right by k positions — O(n) time, O(1) space
public static void rotate(int[] nums, int k) {
    k %= nums.length;
    reverse(nums, 0, nums.length - 1);
    reverse(nums, 0, k - 1);
    reverse(nums, k, nums.length - 1);
}

private static void reverse(int[] arr, int l, int r) {
    while (l < r) { int t = arr[l]; arr[l++] = arr[r]; arr[r--] = t; }
}

// Prefix sum — O(1) range sum queries after O(n) preprocessing
int[] prefix = new int[nums.length + 1];
for (int i = 0; i < nums.length; i++) prefix[i+1] = prefix[i] + nums[i];

// Sum from index l to r (inclusive)
int rangeSum = prefix[r+1] - prefix[l];
```

---

## Top Zoho Interview Problems (Arrays & Strings)

| Problem | Technique | Complexity |
|---|---|---|
| Two Sum (sorted) | Two Pointer | O(n) / O(1) |
| Longest substring no repeat | Sliding Window | O(n) / O(k) |
| Trapping Rain Water | Two Pointer | O(n) / O(1) |
| Maximum Subarray (Kadane's) | DP | O(n) / O(1) |
| Group Anagrams | Sorting + HashMap | O(nk log k) |
| Rotate Array | Triple Reverse | O(n) / O(1) |
| Valid Palindrome | Two Pointer | O(n) / O(1) |

---

## Kadane's Algorithm — Maximum Subarray

```java
public static int maxSubArray(int[] nums) {
    int maxSoFar = nums[0], currentMax = nums[0];
    for (int i = 1; i < nums.length; i++) {
        currentMax = Math.max(nums[i], currentMax + nums[i]);
        maxSoFar = Math.max(maxSoFar, currentMax);
    }
    return maxSoFar;
}
// Time: O(n), Space: O(1)
```

---

## Revision Checkpoint

> Given an array of integers and a target sum, find all unique pairs that sum to the target. Handle duplicates in the input. What is the time complexity of your solution?
