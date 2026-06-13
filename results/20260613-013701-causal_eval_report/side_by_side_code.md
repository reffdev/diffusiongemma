## code-001

**prompt:** Write a Python function `is_palindrome(s: str) -> bool` that returns True if the string is a palindrome, ignoring case and non-alphanumeric characters.

**causal:**

```
To solve this, we can use the `.isalnum()` method to filter out non-alphanumeric characters and `.lower()` to ensure the comparison is case-insensitive.

Here is the implementation:

```python
def is_palindrome(s: str) -> bool:
    # Filter the string: keep only alphanumeric characters and convert to lowercase
    filtered_chars = [char.lower() for char in s if char.isalnum()]
    
    # Compare the list of characters with its reverse
    return filtered_chars == filtered_chars[::-1]

# --- Test Cases ---
print(is_palindrome("A man, a plan, a canal: Panama")) # True
print(is_palindrome("race a car"))                     # False
print(is_palindrome("Was it a car or a cat I saw?"))   # True
print(is_palindrome("No 'x' in Nixon"))                # True
print(is_palindrome("12321"))                          # True
```

### How it works:
1.  **List Comprehension**: We iterate through every character in the input string `s`.
2.  **`char.isalnum()`**: This checks if the character is either a letter or a number, effectively ignoring spaces, commas, colons, and other symbols.
3.  **`char.lower()`**: This converts all letters to lowercase so that 'A' is treated the same as 'a'.
4.  **Slicing (`[::-1]`)**: This is a Pythonic way to create a reversed copy of the list.
5.  **Comparison**: We return the result of the equality check between the filtered list and its reverse.
```

**gemma4:**

```
To solve this problem, we can use a "filter and compare" approach: first, clean the string to remove non-alphanumeric characters and normalize the case, then check if the resulting string is equal to its reverse.

Here is the implementation:

```python
import re

def is_palindrome(s: str) -> bool:
    """
    Returns True if the string is a palindrome, ignoring case 
    and non-alphanumeric characters.
    """
    # 1. Filter the string: keep only alphanumeric characters and convert to lowercase
    # We use a generator expression inside "".join() for efficiency
    cleaned_chars = [char.lower() for char in s if char.isalnum()]
    
    # 2. Compare the list of characters with its reverse
    return cleaned_chars == cleaned_chars[::-1]

# --- Test Cases ---
if __name__ == "__main__":
    test_cases = [
        ("A man, a plan, a canal: Panama", True),
        ("race a car", False),
        ("Was it a car or a cat I saw?", True),
        ("No 'x' in Nixon", True),
        ("12321", True),
        ("123456", False),
        (" ", True),  # An empty/whitespace string is technically a palindrome
    ]

    for text, expected in test_cases:
        result = is_palindrome(text)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} | Input: '{text}' | Expected: {expected} | Got: {result}")
```

### Explanation:

1.  **`char.isalnum()`**: This built-in Python method returns `True` if a character is either a letter or a number. This effectively ignores spaces, punctuation, and special symbols (like `,`, `:`, or `?`).
2.  **`.lower()`**: This ensures the comparison is case-insensitive (e.g., 'A' is treated the same as 'a').
3.  **List Comprehension**: `[char.lower() for char in s if char.isalnum()]` creates a new list containing only the valid characters in lowercase.
4.  **Slicing `[::-1]`**: This is a highly optimized Pythonic way
```

## code-002

**prompt:** Implement `def fib(n: int) -> int` returning the nth Fibonacci number iteratively. Assume n >= 0.

**causal:**

```
Here is the iterative implementation of the Fibonacci sequence. This approach uses $O(n)$ time complexity and $O(1)$ space complexity.

```python
def fib(n: int) -> int:
    """
    Returns the nth Fibonacci number iteratively.
    Sequence: 0, 1, 1, 2, 3, 5, 8, 13, ...
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    a, b = 0, 1
    
    # We have already handled 0 and 1, so we iterate from 2 to n
    for _ in range(2, n + 1):
        a, b = b, a + b
        
    return b

# Examples
if __name__ == "__main__":
    print(f"fib(0): {fib(0)}")   # Output: 0
    print(f"fib(1): {fib(1)}")   # Output: 1
    print(f"fib(7): {fib(7)}")   # Output: 13
    print(f"fib(10): {fib(10)}") # Output: 55
```

### Explanation:
1.  **Base Cases**: We handle $n=0$ and $n=1$ immediately, as they are the starting points of the sequence.
2.  **State Variables**: We use two variables, `a` and `b`, to store the two most recent numbers in the sequence. This avoids the $O(n)$ space requirement of storing the entire sequence in a list.
3.  **The Loop**: We iterate from $2$ up to $n$. In each step, we update `a` to be the previous `b`, and `b` to be the sum of the two previous numbers (`a + b`).
4.  **Efficiency**: 
    *   **Time Complexity**: $O(n)$, as we perform a single pass up to $n$.
    *   **Space Complexity**: $O(1)$, as we only store two integer variables regardless of the size of $n$.
```

**gemma4:**

```
Here is the iterative implementation of the Fibonacci sequence.

```python
def fib(n: int) -> int:
    """
    Returns the nth Fibonacci number using an iterative approach.
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    if n == 0:
        return 0
    if n == 1:
        return 1

    a, b = 0, 1
    
    # We iterate from 2 up to n (inclusive)
    for _ in range(2, n + 1):
        # Update a and b: 
        # 'a' becomes the previous 'b'
        # 'b' becomes the sum of the previous 'a' and 'b'
        a, b = b, a + b
        
    return b

# Test cases
if __name__ == "__main__":
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(4) == 3
    assert fib(5) == 5
    assert fib(10) == 55
    print("All tests passed!")
```

### Explanation:
1.  **Base Cases**: We handle $n=0$ and $n=1$ immediately, as they are the starting points of the sequence.
2.  **State Variables**: We use two variables, `a` and `b`, to keep track of the two most recent numbers in the sequence. This allows us to calculate the next number without storing the entire sequence in a list.
3.  **The Loop**: We loop from $2$ to $n$. In each iteration, we perform a "tuple unpacking" assignment (`a, b = b, a + b`). This calculates the new sum and updates both variables simultaneously, effectively sliding our window one step forward in the sequence.
4.  **Complexity**:
    *   **Time Complexity**: $O(n)$, because we perform a single loop that runs $n-1$ times.
    *   **Space Complexity**: $O(1)$, because we only store two integer variables regardless of how large $n$ is.
```

## code-003

**prompt:** Write a function `merge_sorted(a: list[int], b: list[int]) -> list[int]` that merges two ascending-sorted lists into one ascending-sorted list.

**causal:**

```
To merge two sorted lists efficiently, we use the **two-pointer approach**. This allows us to build the new list in $O(n + m)$ time, where $n$ and $m$ are the lengths of the two lists.

```python
def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    merged = []
    i = 0  # Pointer for list a
    j = 0  # Pointer for list b

    # Traverse both lists and append the smaller element to the result
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1

    # If there are remaining elements in a, append them
    while i < len(a):
        merged.append(a[i])
        i += 1

    # If there are remaining elements in b, append them
    while j < len(b):
        merged.append(b[j])
        j += 1

    return merged

# Example usage:
# list1 = [1, 3, 5, 7]
# list2 = [2, 4, 6, 8, 10]
# print(merge_sorted(list1, list2)) 
# Output: [1, 2, 3, 4, 5, 6, 7, 8, 10]
```

### How it works:
1. **Initialization**: We create an empty list `merged` and two pointers, `i` and `j`, starting at the beginning of each list.
2. **Comparison Loop**: We compare the elements at `a[i]` and `b[j]`. We append the smaller value to our result and increment that specific pointer. This continues until we reach the end of one of the lists.
3. **Cleanup**: After the first loop, one list might still have elements left (because it was longer or had larger values). We use two more `while` loops to append any remaining elements to the end of the `merged` list.

### Complexity:
*   **Time Complexity**: $O(n +
```

**gemma4:**

```
To merge two sorted lists efficiently, the best approach is to use the **two-pointer technique**. This allows us to build the new list in a single pass with a time complexity of $O(n + m)$, where $n$ and $m$ are the lengths of the input lists.

Here is the implementation:

```python
def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    """
    Merges two ascending-sorted lists into one ascending-sorted list
    using the two-pointer technique.
    """
    merged = []
    i = 0  # Pointer for list 'a'
    j = 0  # Pointer for list 'b'

    # Traverse both lists and append the smaller element to 'merged'
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1

    # If there are remaining elements in 'a', append them
    # (This happens if list 'b' was exhausted first)
    if i < len(a):
        merged.extend(a[i:])

    # If there are remaining elements in 'b', append them
    # (This happens if list 'a' was exhausted first)
    if j < len(b):
        merged.extend(b[j:])

    return merged

# --- Test Cases ---
if __name__ == "__main__":
    print(merge_sorted([1, 3, 5], [2, 4, 6]))     # Expected: [1, 2, 3, 4, 5, 6]
    print(merge_sorted([1, 1, 2], [0, 2, 3]))     # Expected: [0, 1, 1, 2, 2, 3]
    print(merge_sorted([], [1, 2, 3]))            # Expected: [1, 2, 3]
    print(merge_sorted([10, 20], [1, 2, 3, 4]))   # Expected: [1, 2, 3
```

## code-004

**prompt:** Edit this function to handle an empty list without raising:

def average(xs):
    return sum(xs) / len(xs)

**causal:**

```
To handle an empty list, you should check if the list is empty before performing the division. If it is empty, you can return `0`, `None`, or any other value that makes sense for your specific use case.

Here are the three most common ways to do it:

### Option 1: Return 0 (Most common for math)
This prevents the `ZeroDivisionError` and returns a numerical result.

```python
def average(xs):
    if not xs:
        return 0
    return sum(xs) / len(xs)
```

### Option 2: Return `None`
This is useful if you need to distinguish between a list that sums to zero and a list that is actually empty.

```python
def average(xs):
    if not xs:
        return None
    return sum(xs) / len(xs)
```

### Option 3: One-liner (Using a conditional expression)
This is a more concise version of Option 1.

```python
def average(xs):
    return sum(xs) / len(xs) if xs else 0
```

### Why this works:
In Python, an empty list `[]` is "falsy." Using `if not xs:` is the idiomatic way to check if a list is empty. If the list has items, it evaluates to `True`, and the division proceeds as normal.
1.  **Check if the list is empty:** Use `if not xs:` to see if the list has any elements.
2.  **Return a default value:** If the list is empty, return `0` (or `None`) instead of trying to divide by `len(xs)`, which would be zero.
3.  **Perform the calculation:** If the list is not empty, proceed with `sum(xs) / len(xs)`.
1.  **Check if the list is empty:** Use `if not xs:` to see if the list has any elements.
2.  **Return a default value:** If the list is empty, return `0` (or `None`) instead of trying to divide by `len(xs)`, which would be zero.
3.  **Perform the calculation:** If the list is not empty, proceed with `sum(xs) / len(xs)`.
```

**gemma4:**

```
To handle an empty list, you need to check if the list is empty before performing the division to avoid a `ZeroDivisionError`.

Here are the three most common ways to do this, depending on how you want the function to behave:

### Option 1: Return `0` (Most common for simple scripts)
This is the safest approach if you want the code to keep running without any special logic elsewhere.

```python
def average(xs):
    if not xs:
        return 0
    return sum(xs) / len(xs)
```

### Option 2: Return `None` (Best for data analysis)
Returning `None` is often better because it distinguishes between a list that sums to zero (e.g., `[-1, 1]`) and a list that has no data at all.

```python
def average(xs):
    if not xs:
        return None
    return sum(xs) / len(xs)
```

### Option 3: The "One-Liner" (Pythonic)
If you prefer concise code, you can use a conditional expression (ternary operator).

```python
def average(xs):
    return sum(xs) / len(xs) if xs else 0
```

### Which one should you choose?
*   **Use `0`** if you are calculating something like a score where "no data" should be treated as "no points."
*   **Use `None`** if you are performing statistical analysis and need to know that the data was missing.
*   **Avoid** simply returning `0` if your list could contain negative numbers, as `0` might be a valid mathematical result, making it impossible to tell if the list was empty or if the average was actually zero.
```

## code-005

**prompt:** Write `def count_words(text: str) -> dict[str, int]` that returns a case-insensitive word frequency count, splitting on whitespace.

**causal:**

```
Here is the implementation using the built-in `split()` method and a dictionary to track counts.

```python
def count_words(text: str) -> dict[str, int]:
    """
    Returns a case-insensitive word frequency count, 
    splitting on whitespace.
    """
    counts = {}
    # .split() without arguments splits by any whitespace 
    # and discards empty strings from multiple spaces.
    words = text.lower().split()
    
    for word in words:
        counts[word] = counts.get(word, 0) + 1
        
    return counts

# Example usage:
# count_words("Hello world hello") -> {'hello': 2, 'world': 1}
```

### Explanation:
1.  **`.lower()`**: Converts the entire string to lowercase to ensure the count is case-insensitive (e.g., "Apple" and "apple" are treated as the same word).
2.  **`.split()`**: When called without arguments, it automatically splits the string by any whitespace (spaces, tabs, newlines) and handles multiple consecutive spaces gracefully.
3.  **`.get(word, 0)`**: This is a safe way to access the dictionary. If the word doesn't exist yet, it returns `0`; otherwise, it returns the current count, which we then increment by `1`.

*Note: If you are working with very large datasets, you could also use `collections.Counter` for a more concise version:*

```python
from collections import Counter

def count_words(text: str) -> dict[str, int]:
    return dict(Counter(text.lower().split()))
```
```

**gemma4:**

```
Here is the implementation. It uses the `.lower()` method to ensure case-insensitivity and `.split()` to handle any whitespace characters (spaces, tabs, newlines).

```python
def count_words(text: str) -> dict[str, int]:
    """
    Returns a case-insensitive word frequency count, 
    splitting on whitespace.
    """
    # Convert to lowercase to ensure case-insensitivity
    words = text.lower().split()
    
    counts = {}
    for word in words:
        # Increment count if word exists, otherwise initialize to 1
        counts[word] = counts.get(word, 0) + 1
        
    return counts

# Examples
if __name__ == "__main__":
    example_text = "Apple banana apple Orange BANANA apple"
    print(count_words(example_text))
    # Output: {'apple': 3, 'banana': 2, 'orange': 1}
```

### Explanation:
1.  **`.lower()`**: This converts the entire string to lowercase so that "Apple" and "apple" are treated as the same key.
2.  **`.split()`**: When called without arguments, this method automatically splits by any whitespace (including multiple spaces, `\n`, or `\t`) and discards empty strings from the resulting list.
3.  **`.get(word, 0)`**: This is a clean way to handle dictionary keys. It looks for the current count of the word; if the word isn't in the dictionary yet, it returns `0` instead of throwing a `KeyError`.

### Alternative (Using Python Standard Library):
For a more "Pythonic" and highly optimized version, you can use `collections.Counter`:

```python
from collections import Counter

def count_words(text: str) -> dict[str, int]:
    return dict(Counter(text.lower().split()))
```
```

## code-006

**prompt:** Implement a Python function `binary_search(arr: list[int], target: int) -> int` returning the index of target or -1 if absent.

**causal:**

```
Here is the implementation of the binary search algorithm in Python.

```python
def binary_search(arr: list[int], target: int) -> int:
    """
    Performs a binary search on a sorted list to find the index of the target.
    
    Args:
        arr: A sorted list of integers.
        target: The integer to search for.
        
    Returns:
        The index of the target if found, otherwise -1.
    """
    low = 0
    high = len(arr) - 1

    while low <= high:
        # Calculate the middle index
        # (low + high) // 2 is standard, but (low + (high - low) // 2) 
        # prevents potential overflow in other languages.
        mid = (low + high) // 2
        
        # Check if target is present at mid
        if arr[mid] == target:
            return mid
        
        # If target is greater, ignore left half
        elif arr[mid] < target:
            low = mid + 1
            
        # If target is smaller, ignore right half
        else:
            high = mid - 1

    # Target was not found in the list
    return -1

# --- Example Usage ---
if __name__ == "__main__":
    nums = [1, 3, 5, 7, 9, 11, 13, 15]
    
    print(binary_search(nums, 7))   # Output: 3
    print(binary_search(nums, 1))   # Output: 0
    print(binary_search(nums, 15))  # Output: 7
    print(binary_search(nums, 4))   # Output: -1
```

### Key Details:
1.  **Time Complexity**: $O(\log n)$, where $n$ is the number of elements in the list. This is because the search space is halved in every iteration.
2.  **Space Complexity**: $O(1)$, as it uses a constant amount of extra space.
3.  **Requirement**: The input list `arr` **must be sorted** for binary search to work correctly.
```

**gemma4:**

```
Here is the implementation of the `binary_search` function using the iterative approach, which is memory-efficient.

```python
def binary_search(arr: list[int], target: int) -> int:
    """
    Performs a binary search on a sorted list to find the index of the target.

    Args:
        arr: A sorted list of integers.
        target: The integer to search for.

    Returns:
        The index of the target if found, otherwise -1.
    """
    low = 0
    high = len(arr) - 1

    while low <= high:
        # Calculate the middle index. 
        # (low + high) // 2 is standard, but (low + (high - low) // 2) 
        # prevents potential overflow in other languages.
        mid = low + (high - low) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            # Target is in the right half
            low = mid + 1
        else:
            # Target is in the left half
            high = mid - 1

    return -1

# --- Test Cases ---
if __name__ == "__main__":
    test_list = [1, 3, 5, 7, 9, 11, 13, 15]
    
    print(f"Index of 7: {binary_search(test_list, 7)}")    # Expected: 3
    print(f"Index of 1: {binary_search(test_list, 1)}")    # Expected: 0
    print(f"Index of 15: {binary_search(test_list, 15)}")  # Expected: 7
    print(f"Index of 4: {binary_search(test_list, 4)}")    # Expected: -1
    print(f"Index of 20: {binary_search(test_list, 20)}")  # Expected: -1
    print(f"Empty list: {binary_search([], 5)}")           # Expected: -1
```

### Complexity Analysis:
*   **Time Complexity: $O(\log n)$**
```

## code-007

**prompt:** Write `def flatten(nested: list) -> list` that flattens an arbitrarily nested list of integers into a flat list.

**causal:**

```
To flatten an arbitrarily nested list, the most effective approach is to use **recursion**. We iterate through each element: if the element is a list, we call the function recursively; if it is an integer, we append it to our result.

Here are two ways to implement this:

### 1. The Standard Recursive Approach
This is the most readable version. It uses a helper function or a simple loop to build the flat list.

```python
def flatten(nested: list) -> list:
    flat_list = []
    for item in nested:
        if isinstance(item, list):
            # Recursively flatten the sub-list and extend the result
            flat_list.extend(flatten(item))
        else:
            # If it's an integer, just append it
            flat_list.append(item)
    return flat_list

# Example usage:
nested_list = [1, [2, [3, 4], 5], 6, [7, 8]]
print(flatten(nested_list)) 
# Output: [1, 2, 3, 4, 5, 6, 7, 8]
```

### 2. The Generator Approach (Memory Efficient)
If you are dealing with very large lists, using a generator is more memory-efficient because it yields items one by one instead of creating a new list in memory at every level of recursion.

```python
def flatten(nested: list) -> list:
    def _gen(items):
        for item in items:
            if isinstance(item, list):
                yield from _gen(item)
            else:
                yield item
    
    return list(_gen(nested))

# Example usage:
print(flatten([1, [2, [3]], 4])) 
# Output: [1, 2, 3, 4]
```

### How it works:
1. **Base Case:** When the loop encounters an integer (not a list), it simply adds it to the output.
2. **Recursive Step:** When the loop encounters a list, it pauses the current execution, enters the `flatten` function again for that sub-list, and waits for that sub-list to be fully flattened before continuing.
3. **`isinstance(item, list)`**: This check ensures
```

**gemma4:**

```
To flatten an arbitrarily nested list, the most effective approach is to use **recursion**. We iterate through each element: if the element is a list, we call the function again; if it is an integer, we append it to our result.

Here is the implementation:

```python
def flatten(nested: list) -> list:
    """
    Flattens an arbitrarily nested list of integers into a single flat list.
    """
    flat_list = []
    
    for item in nested:
        # Check if the item is a list to decide whether to recurse
        if isinstance(item, list):
            # Extend the flat_list with the result of the recursive call
            flat_list.extend(flatten(item))
        else:
            # If it's an integer (or not a list), append it directly
            flat_list.append(item)
            
    return flat_list

# --- Test Cases ---
if __name__ == "__main__":
    test1 = [1, 2, 3]
    test2 = [1, [2, 3], 4]
    test3 = [1, [2, [3, 4], 5], 6]
    test4 = [[[[1]]], 2, [3, [4, [5]]]]

    print(f"Test 1: {flatten(test1)}")  # Expected: [1, 2, 3]
    print(f"Test 2: {flatten(test2)}")  # Expected: [1, 2, 3, 4]
    print(f"Test 3: {flatten(test3)}")  # Expected: [1, 2, 3, 4, 5, 6]
    print(f"Test 4: {flatten(test4)}")  # Expected: [1, 2, 3, 4, 5]
```

### How it works:
1.  **Base Case:** The loop naturally handles the base case. If an element is not a list (e.g., an integer), it is simply appended to `flat_list`.
2.  **Recursive Step:** If an element is a `list`, the function calls itself (`flatten(item)`). This "drills down" into the nested structure regardless of
```

## code-008

**prompt:** Add type hints and a docstring to this function:

def clamp(x, lo, hi):
    return max(lo, min(x, hi))

**causal:**

```
Here are a few ways to add type hints and docstrings, depending on how specific you want to be.

### Option 1: Using `float` (Most Common)
Since `int` is a subtype of `float` in many type-checking contexts, using `float` is the standard way to indicate that the function handles both integers and decimals.

```python
def clamp(x: float, lo: float, hi: float) -> float:
    """
    Clamps a value between a lower and upper bound.

    Args:
        x: The value to be clamped.
        lo: The lower bound.
        hi: The upper bound.

    Returns:
        The value of x if it is within [lo, hi], otherwise lo or hi.
    """
    return max(lo, min(x, hi))
```

### Option 2: Using Generics (Most Precise)
If you want to ensure that if a user passes in an `int`, they get an `int` back (and the same for `float`), you can use `TypeVar`. This is the "pro" way to handle numeric types in modern Python.

```python
from typing import TypeVar

T = TypeVar("T", int, float)

def clamp(x: T, lo: T, hi: T) -> T:
    """
    Clamps a numeric value between a lower and upper bound.

    Args:
        x: The value to be clamped.
        lo: The lower bound.
        hi: The upper bound.

    Returns:
        The clamped value.
    """
    return max(lo, min(x, hi))
```

### Key Improvements Made:
1.  **Type Annotations**: Added `: float` for inputs and `-> float` for the return type.
2.  **Google-style Docstring**: Included a summary, an `Args` section, and a `Returns` section. This is compatible with documentation generators like Sphinx or Pydoc.
3.  **Clarity**: The docstring explains the logic (clamping) which might not be immediately obvious to someone unfamiliar with the term.
```

**gemma4:**

```
Here are a few ways to do this, depending on how strict you want to be with your type definitions.

### Option 1: Using `TypeVar` (Recommended)
Since `clamp` works on any comparable type (integers, floats, or even strings), the most professional way is to use a `TypeVar`. This tells the type checker that if you pass in an `int`, you will get an `int` back.

```python
from typing import TypeVar

# T represents any type that supports comparison (<, >)
T = TypeVar('T', int, float)

def clamp(x: T, lo: T, hi: T) -> T:
    """
    Clamps a value between a lower and upper bound.

    Args:
        x: The value to clamp.
        lo: The lower bound.
        hi: The upper bound.

    Returns:
        The clamped value: lo if x < lo, hi if x > hi, otherwise x.
    """
    return max(lo, min(x, hi))
```

### Option 2: Simple (Using `float`)
If you are primarily using this for mathematical calculations, it is common to simply hint everything as `float`. In Python, `float` type hints are generally accepted for `int` inputs as well.

```python
def clamp(x: float, lo: float, hi: float) -> float:
    """
    Clamps a value between a lower and upper bound.

    Args:
        x: The value to clamp.
        lo: The lower bound.
        hi: The upper bound.

    Returns:
        The value of x restricted to the range [lo, hi].
    """
    return max(lo, min(x, hi))
```

### Key Improvements Made:
1.  **Type Hints**: Added `: T` and `-> T` to define input and output types.
2.  **Docstring Format**: Used the **Google Style** docstring format, which is widely used in the industry for its readability.
3.  **Clarity**: The docstring explains not just what the function does, but the logic of the return value.

### Which one should you use?
*   Use **Option 1** if you are building a library or a large codebase where you want strict type safety (e.
```

## code-009

**prompt:** Write `def fizzbuzz(n: int) -> list[str]` returning the FizzBuzz sequence from 1 to n as a list of strings.

**causal:**

```
Here is the implementation of the `fizzbuzz` function:

```python
def fizzbuzz(n: int) -> list[str]:
    """
    Returns the FizzBuzz sequence from 1 to n as a list of strings.
    - Multiples of 3 are replaced with "Fizz"
    - Multiples of 5 are replaced with "Buzz"
    - Multiples of both 3 and 5 are replaced with "FizzBuzz"
    - Other numbers are returned as strings of the number
    """
    result = []
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result

# Example usage:
# print(fizzbuzz(15))
# Output: ['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']
```

### Explanation:
1. **Initialization**: We create an empty list `result` to store the strings.
2. **Iteration**: We use `range(1, n + 1)` to iterate through every integer from 1 up to and including `n`.
3. **Logic**:
   - We check for `i % 3 == 0 and i % 5 == 0` first. If we checked for 3 or 5 individually first, "FizzBuzz" would never be reached because the individual conditions would trigger first.
   - We use `elif` for the remaining cases (multiples of 3, then multiples of 5).
   - If none of the conditions are met, we convert the integer to a string using `str(i)`.
4. **Return**: Finally, we return the populated list.
```

**gemma4:**

```
Here is the implementation of the `fizzbuzz` function:

```python
def fizzbuzz(n: int) -> list[str]:
    """
    Returns the FizzBuzz sequence from 1 to n as a list of strings.
    - For multiples of 3, return 'Fizz'.
    - For multiples of 5, return 'Buzz'.
    - For multiples of both 3 and 5, return 'FizzBuzz'.
    - Otherwise, return the number as a string.
    """
    result = []
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result

# Example usage:
# print(fizzbuzz(15))
# Output: ['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']
```

### Explanation:
1.  **Range**: We use `range(1, n + 1)` to ensure the loop includes the number `n`.
2.  **Logic Order**: We check for `i % 3 == 0 and i % 5 == 0` first. If we checked for 3 or 5 individually first, the code would append "Fizz" or "Buzz" and skip the "FizzBuzz" condition.
3.  **Type Conversion**: For numbers that don't meet the Fizz/Buzz criteria, we use `str(i)` to ensure the list contains only strings, as specified by the type hint `list[str]`.
```

## code-010

**prompt:** Implement `def reverse_words(s: str) -> str` that reverses the order of words in a sentence while preserving single spaces.

**causal:**

```
To implement this, the most efficient approach is to split the string into a list of words based on spaces, reverse that list, and then join the words back together with a single space.

Here is the implementation:

```python
def reverse_words(s: str) -> str:
    # .split() without arguments handles multiple spaces and leading/trailing whitespace.
    # However, if the requirement is to preserve the exact structure of single spaces 
    # and only reverse the word order, we split by a single space.
    words = s.split(' ')
    
    # Reverse the list of words in place
    words.reverse()
    
    # Join the words back into a string with a single space
    return ' '.join(words)

# Test cases
if __name__ == "__main__":
    print(f"'{reverse_words('hello world')}'")        # Expected: 'world hello'
    print(f"'{reverse_words('The quick brown fox')}'") # Expected: 'fox brown quick The'
    print(f"'{reverse_words('Python')}'")             # Expected: 'Python'
```

### How it works:
1.  **`s.split(' ')`**: This breaks the string into a list of substrings every time it encounters a space. By specifying `' '`, we ensure that if there are multiple spaces, they are treated as empty strings in the list, preserving the spacing structure.
2.  **`words.reverse()`**: This reverses the order of the elements in the list.
3.  **`' '.join(words)`**: This takes the reversed list and concatenates the elements back into a single string, placing a space between each element.

### Complexity:
*   **Time Complexity**: $O(n)$, where $n$ is the length of the string. We traverse the string to split it, traverse the list to reverse it, and traverse it again to join it.
*   **Space Complexity**: $O(n)$, as we create a list of words that, in total, take up the same amount of space as the original string.
```

**gemma4:**

```
To implement this, the most efficient approach is to split the string into a list of words, reverse that list, and then join them back together using a single space as a separator.

Here is the implementation:

```python
def reverse_words(s: str) -> str:
    """
    Reverses the order of words in a sentence while preserving single spaces.
    
    Args:
        s: The input string containing words separated by spaces.
        
    Returns:
        A string with the words in reverse order.
    """
    # .split() without arguments handles multiple spaces and leading/trailing whitespace
    # If the requirement is to strictly treat every single space as a delimiter, 
    # use .split(' ') instead.
    words = s.split()
    
    # Reverse the list of words
    reversed_words = words[::-1]
    
    # Join the words back into a single string with a single space between them
    return " ".join(reversed_words)

# --- Test Cases ---
if __name__ == "__main__":
    # Standard case
    print(f"'{reverse_words('the sky is blue')}'") 
    # Expected: 'blue is sky the'

    # Case with extra spaces (split() handles this by default)
    print(f"'{reverse_words('  hello world  ')}'") 
    # Expected: 'world hello'

    # Single word
    print(f"'{reverse_words('Python')}'") 
    # Expected: 'Python'

    # Empty string
    print(f"'{reverse_words('')}'") 
    # Expected: ''
```

### Complexity Analysis:
1.  **Time Complexity: $O(n)$**, where $n$ is the length of the input string. 
    *   `split()` traverses the string once: $O(n)$.
    *   `[::-1]` (reversing the list) traverses the list of words: $O(n)$.
    *   `join()` traverses the list to build the new string: $O(n)$.
2.  **Space Complexity: $O(n)$**.
    *   We create a list of words and a new resulting string, both of which scale linearly with the input size.

### Key Implementation Detail: `split()`
```

## code-011

**prompt:** Write a recursive function `def factorial(n: int) -> int` for n >= 0, returning 1 for n == 0.

**causal:**

```
Here is the recursive implementation of the factorial function in Python:

```python
def factorial(n: int) -> int:
    # Base case: if n is 0, return 1
    if n == 0:
        return 1
    # Recursive step: n! = n * (n-1)!
    else:
        return n * factorial(n - 1)
```

### Explanation:
1.  **Base Case**: The function checks if `n` is `0`. If it is, it returns `1`. This is crucial to prevent infinite recursion and to satisfy the mathematical definition of $0!$.
2.  **Recursive Step**: If `n` is greater than `0`, the function calls itself with the argument `n - 1`. It multiplies the current value of `n` by the result of that call until it eventually hits the base case.

### Example Usage:
```python
print(factorial(0))  # Output: 1
print(factorial(5))  # Output: 120 (5 * 4 * 3 * 2 * 1)
```
```

**gemma4:**

```
Here is the recursive implementation of the factorial function in Python:

```python
def factorial(n: int) -> int:
    # Base case: if n is 0, return 1
    if n == 0:
        return 1
    # Recursive step: n! = n * (n-1)!
    else:
        return n * factorial(n - 1)

# Examples of usage:
print(factorial(0))  # Output: 1
print(factorial(5))  # Output: 120 (5 * 4 * 3 * 2 * 1)
```

### Explanation:
1.  **Base Case**: Every recursive function needs a stopping condition to prevent infinite recursion. Since the problem defines $0! = 1$, we check `if n == 0` and return `1`.
2.  **Recursive Step**: For any number greater than 0, the factorial of $n$ is defined as $n$ multiplied by the factorial of the number preceding it ($n-1$). The function calls itself with a smaller value until it eventually hits the base case.
3.  **Complexity**:
    *   **Time Complexity**: $O(n)$, as the function performs $n$ recursive calls.
    *   **Space Complexity**: $O(n)$, due to the call stack depth required for the recursion.
```

## code-012

**prompt:** Implement `def gcd(a: int, b: int) -> int` using the Euclidean algorithm.

**causal:**

```
The Euclidean algorithm is based on the principle that the greatest common divisor of two numbers does not change if the larger number is replaced by its difference with the smaller number (or more efficiently, by its remainder when divided by the smaller number).

Here are two ways to implement this in Python:

### 1. Iterative Approach (Recommended)
This is generally more efficient in Python as it avoids the overhead of recursion and potential recursion depth limits.

```python
def gcd(a: int, b: int) -> int:
    """
    Computes the greatest common divisor of a and b using 
    the iterative Euclidean algorithm.
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
```

### 2. Recursive Approach
This is a more mathematically direct translation of the algorithm.

```python
def gcd(a: int, b: int) -> int:
    """
    Computes the greatest common divisor of a and b using 
    the recursive Euclidean algorithm.
    """
    a, b = abs(a), abs(b)
    if b == 0:
        return a
    return gcd(b, a % b)
```

### How it works:
1. **`abs(a), abs(b)`**: We take the absolute value because the GCD is defined as a positive integer, regardless of the signs of the inputs.
2. **`while b:`**: The loop continues as long as `b` is not zero.
3. **`a, b = b, a % b`**: This is the core of the algorithm. We replace `a` with `b`, and `b` with the remainder of `a` divided by `b`.
4. **Return `a`**: When `b` becomes zero, `a` contains the greatest common divisor.

### Example Usage:
```python
print(gcd(48, 18))  # Output: 6
print(gcd(101, 10)) # Output: 1
print(gcd(-48, 18)) # Output: 6
```

*Note: For production code, Python provides this function built-in via `math.gcd(a, b)`.*
```

**gemma4:**

```
The Euclidean algorithm is based on the principle that the greatest common divisor of two numbers does not change if the larger number is replaced by its remainder when divided by the smaller number.

Here are two ways to implement this in Python: the **iterative** approach (more memory efficient) and the **recursive** approach (more concise).

### 1. Iterative Implementation (Recommended)
This version uses a `while` loop to update the values until the remainder becomes zero.

```python
def gcd(a: int, b: int) -> int:
    """
    Computes the greatest common divisor of a and b 
    using the iterative Euclidean algorithm.
    """
    # Ensure we work with absolute values to handle negative inputs
    a, b = abs(a), abs(b)
    
    while b != 0:
        # a becomes b, and b becomes the remainder of a divided by b
        a, b = b, a % b
    return a

# Test cases
print(gcd(48, 18))   # Output: 6
print(gcd(101, 10))  # Output: 1
print(gcd(0, 5))     # Output: 5
```

### 2. Recursive Implementation
This version follows the mathematical definition directly: $\text{gcd}(a, b) = \text{gcd}(b, a \pmod b)$.

```python
def gcd(a: int, b: int) -> int:
    """
    Computes the greatest common divisor of a and b 
    using the recursive Euclidean algorithm.
    """
    a, b = abs(a), abs(b)
    
    if b == 0:
        return a
    return gcd(b, a % b)

# Test cases
print(gcd(48, 18))   # Output: 6
print(gcd(1071, 462)) # Output: 21
```

### Complexity Analysis
*   **Time Complexity:** $O(\log(\min(a, b)))$. The number of steps grows logarithmically with the size of the input numbers.
*   **Space Complexity:** 
    *   **Iterative:** $O(1)$ (constant space).
    *   **Recursive:** $O(\log(\
```

## code-013

**prompt:** Write `def is_prime(n: int) -> bool` that returns True if n is a prime number.

**causal:**

```
Here is a common and efficient implementation of the primality test. It uses the property that a number $n$ is prime if it is not divisible by any integer up to $\sqrt{n}$.

```python
import math

def is_prime(n: int) -> bool:
    """Returns True if n is a prime number, False otherwise."""
    # Prime numbers must be greater than 1
    if n <= 1:
        return False
    
    # 2 and 3 are prime
    if n <= 3:
        return True
    
    # Eliminate even numbers and multiples of 3 immediately
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    # Check divisors from 5 up to sqrt(n)
    # We use a step of 6 (checking i and i + 2) because all primes 
    # greater than 3 are of the form 6k ± 1
    limit = int(math.sqrt(n))
    for i in range(5, limit + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
            
    return True
```

### How it works:
1.  **Edge Cases:** It immediately returns `False` for numbers $\le 1$.
2.  **Small Primes:** It handles $2$ and $3$ as special cases.
3.  **Efficiency (Trial Division):** It skips all even numbers and multiples of 3.
4.  **Square Root Optimization:** Instead of checking all numbers up to $n$, it only checks up to $\sqrt{n}$. If $n$ has a factor larger than its square root, it must also have a corresponding factor smaller than its square root.
5.  **6k ± 1 Optimization:** Every prime number greater than 3 can be written in the form $6k \pm 1$. By checking `i` and `i + 2` while incrementing by 6, we skip unnecessary checks for multiples of 2 and 3, making the loop roughly 3 times faster than a basic trial division.

### Example Usage:
```python
print(is_prime(11))  # True
print(is_prime(15
```

**gemma4:**

```
Here is the most efficient standard implementation for checking primality. It uses the property that all primes greater than 3 can be written in the form $6k \pm 1$, which allows us to skip many unnecessary checks.

```python
import math

def is_prime(n: int) -> bool:
    """Returns True if n is a prime number, False otherwise."""
    # 1. Handle numbers less than 2
    if n <= 1:
        return False
    
    # 2. Handle 2 and 3 (the only primes that don't follow 6k +/- 1)
    if n <= 3:
        return True
    
    # 3. Eliminate even numbers and multiples of 3 immediately
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    # 4. Check divisors from 5 up to sqrt(n)
    # We skip even numbers and multiples of 3 by incrementing by 6
    # and checking (i) and (i + 2)
    limit = int(math.isqrt(n))
    for i in range(5, limit + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
            
    return True

# --- Test Cases ---
if __name__ == "__main__":
    test_cases = {
        -5: False, 0: False, 1: False, 2: True, 3: True, 
        4: False, 5: True, 11: True, 15: False, 25: False, 
        97: True, 100: False
    }
    
    for num, expected in test_cases.items():
        result = is_prime(num)
        print(f"is_prime({num:3}) -> {str(result):5} | {'✅' if result == expected else '❌'}")
```

### Key Optimizations Explained:
1.  **Trial Division up to $\sqrt{n}$**: If $n$ has a factor, at least one factor must be less than or equal to its square root. This reduces the time complexity from $O(
```

## code-014

**prompt:** Implement `def sum_even(xs: list[int]) -> int` returning the sum of the even numbers in the list.

**causal:**

```
Here are a few ways to implement this in Python, ranging from a standard loop to a more concise functional approach.

### Option 1: Using a List Comprehension (Recommended)
This is the most "Pythonic" way. It is concise and highly readable.

```python
def sum_even(xs: list[int]) -> int:
    """Returns the sum of all even numbers in the list."""
    return sum(x for x in xs if x % 2 == 0)
```

### Option 2: Using a Standard Loop
This approach is the most explicit and is helpful if you are just learning how loops work.

```python
def sum_even(xs: list[int]) -> int:
    total = 0
    for x in xs:
        if x % 2 == 0:
            total += x
    return total
```

### Option 3: Using `filter`
This uses a functional programming style.

```python
def sum_even(xs: list[int]) -> int:
    return sum(filter(lambda x: x % 2 == 0, xs))
```

### Example Usage:
```python
print(sum_even([1, 2, 3, 4, 5, 6])) # Output: 12 (2 + 4 + 6)
print(sum_even([1, 3, 5]))          # Output: 0
print(sum_even([]))                 # Output: 0
```

### Explanation:
1.  **`x % 2 == 0`**: This uses the modulo operator. If a number divided by 2 has a remainder of 0, it is even.
2.  **`sum()`**: A built-in Python function that adds up all the elements in an iterable.
3.  **Generator Expression**: In Option 1, `(x for x in xs if x % 2 == 0)` creates an iterator that only yields even numbers, which `sum()` then processes efficiently without creating a new list in memory.
```

**gemma4:**

```
Here are a few ways to implement this function, ranging from the most common "Pythonic" way to a more manual approach.

### 1. The Pythonic Way (Recommended)
Using a **generator expression** inside the `sum()` function is the most efficient and readable method.

```python
def sum_even(xs: list[int]) -> int:
    """Returns the sum of all even numbers in the list."""
    return sum(x for x in xs if x % 2 == 0)
```

### 2. The Functional Way
Using `filter`, which is often preferred by those coming from functional programming backgrounds.

```python
def sum_even(xs: list[int]) -> int:
    """Returns the sum of all even numbers in the list."""
    return sum(filter(lambda x: x % 2 == 0, xs))
```

### 3. The Manual Way (Looping)
If you are a beginner or want to see the explicit logic, you can use a standard `for` loop.

```python
def sum_even(xs: list[int]) -> int:
    """Returns the sum of all even numbers in the list."""
    total = 0
    for x in xs:
        if x % 2 == 0:
            total += x
    return total
```

### Explanation of the Logic:
1.  **`x % 2 == 0`**: This uses the modulo operator. If a number divided by 2 has a remainder of 0, it is even.
2.  **`sum(...)`**: This built-in function takes an iterable of numbers and adds them all together.
3.  **Complexity**: 
    *   **Time Complexity**: $O(n)$, where $n$ is the length of the list, because we must check every number exactly once.
    *   **Space Complexity**: $O(1)$, as we are only storing a single running total.

### Example Usage:
```python
print(sum_even([1, 2, 3, 4, 5, 6])) # Output: 12 (2 + 4 + 6)
print(sum_even([1, 3, 5]))          # Output: 0
print(sum_even([]))                 # Output: 0
```

## code-015

**prompt:** Write `def max_of_three(a: float, b: float, c: float) -> float` without using the built-in max.

**causal:**

```
Here are a few ways to implement this.

### Option 1: Using `if-elif-else` (Most Readable)
This is the most straightforward approach, comparing the numbers step-by-step.

```python
def max_of_three(a: float, b: float, c: float) -> float:
    if a >= b and a >= c:
        return a
    elif b >= a and b >= c:
        return b
    else:
        return c
```

### Option 2: Using a Temporary Variable (Most Scalable)
This approach is useful if you want to understand the logic used to find a maximum in a list of any size.

```python
def max_of_three(a: float, b: float, c: float) -> float:
    largest = a
    if b > largest:
        largest = b
    if c > largest:
        largest = c
    return largest
```

### Option 3: Using a Ternary Operator (One-Liner)
This is a condensed version of the logic, often used for brevity.

```python
def max_of_three(a: float, b: float, c: float) -> float:
    return a if (a >= b and a >= c) else (b if b >= c else c)
```

### Example Usage:
```python
print(max_of_three(10.5, 20.1, 15.0)) # Output: 20.1
print(max_of_three(5.0, 5.0, 2.0))    # Output: 5.0
print(max_of_three(-1.0, -5.0, -0.5)) # Output: -0.5
```
```

**gemma4:**

```
Here are a few ways to implement this. The most common approach is using conditional `if/else` statements.

### Option 1: Using standard `if/else` (Most readable)
This approach compares the numbers step-by-step to find the largest.

```python
def max_of_three(a: float, b: float, c: float) -> float:
    if a >= b and a >= c:
        return a
    elif b >= a and b >= c:
        return b
    else:
        return c
```

### Option 2: Using a "Current Max" variable (Most scalable)
This pattern is better if you were to expand the function to handle more than three numbers, as it tracks the highest value found so far.

```python
def max_of_three(a: float, b: float, c: float) -> float:
    largest = a
    if b > largest:
        largest = b
    if c > largest:
        largest = c
    return largest
```

### Option 3: Using a Ternary Operator (One-liner)
This is a condensed version of the logic, useful if you want to keep the function extremely brief.

```python
def max_of_three(a: float, b: float, c: float) -> float:
    return a if (a >= b and a >= c) else (b if b >= c else c)
```

### Explanation of the logic:
1.  **Option 1** checks if `a` is the king of the hill. If not, it checks if `b` is. If neither is, `c` must be the largest by default.
2.  **Option 2** assumes `a` is the largest initially. It then compares that "champion" against `b`, and then compares the winner against `c`.
3.  **Option 3** is simply a nested version of the first option written in a single line of code.
```

## code-016

**prompt:** Implement `def celsius_to_fahrenheit(c: float) -> float` converting Celsius to Fahrenheit.

**causal:**

```
To convert Celsius to Fahrenheit, you multiply the Celsius temperature by $9/5$ (or $1.8$) and add $32$.

Here is the implementation:

```python
def celsius_to_fahrenheit(c: float) -> float:
    """
    Converts a temperature from Celsius to Fahrenheit.
    
    Args:
        c: The temperature in degrees Celsius.
        
    Returns:
        The temperature in degrees Fahrenheit.
    """
    return (c * 9/5) + 32

# Examples
if __name__ == "__main__":
    print(celsius_to_fahrenheit(0))    # Expected: 32.0 (Freezing point)
    print(celsius_to_fahrenheit(100))  # Expected: 212.0 (Boiling point)
    print(celsius_to_fahrenheit(-40))  # Expected: -40.0 (Intersection point)
```
```

**gemma4:**

```
Here is the implementation of the function.

The formula to convert Celsius to Fahrenheit is:  
$F = (C \times \frac{9}{5}) + 32$

```python
def celsius_to_fahrenheit(c: float) -> float:
    """
    Converts a temperature from Celsius to Fahrenheit.

    Args:
        c (float): The temperature in Celsius.

    Returns:
        float: The temperature in Fahrenheit.
    """
    return (c * 9/5) + 32

# Examples/Tests
if __name__ == "__main__":
    print(f"0°C is {celsius_to_fahrenheit(0):.1f}°F")      # Expected: 32.0
    print(f"100°C is {celsius_to_fahrenheit(100):.1f}°F")  # Expected: 212.0
    print(f"-40°C is {celsius_to_fahrenheit(-40):.1f}°F")  # Expected: -40.0
    print(f"37°C is {celsius_to_fahrenheit(37):.1f}°F")    # Expected: 98.6
```
```

## code-017

**prompt:** Write `def count_vowels(s: str) -> int` counting the vowels (a, e, i, o, u) in a string, case-insensitive.

**causal:**

```
Here are a few ways to implement this in Python.

### Option 1: Using a Generator Expression (Most Pythonic)
This is the most concise and efficient way to write it. It iterates through the string and sums `1` for every character that is found in the vowel set.

```python
def count_vowels(s: str) -> int:
    vowels = "aeiouAEIOU"
    return sum(1 for char in s if char in vowels)
```

### Option 2: Using a Simple Loop
This approach is very readable and easy for beginners to understand.

```python
def count_vowels(s: str) -> int:
    count = 0
    vowels = "aeiou"
    # Convert to lowercase once to make the check case-insensitive
    for char in s.lower():
        if char in vowels:
            count += 1
    return count
```

### Option 3: Using `map` and `count` (Functional approach)
If you prefer a functional programming style, you can use `map` to normalize the string.

```python
def count_vowels(s: str) -> int:
    s = s.lower()
    return sum(s.count(v) for v in "aeiou")
```

### Example Usage:
```python
print(count_vowels("Hello World"))  # Output: 3
print(count_vowels("Python Programming"))  # Output: 4
print(count_vowels("AEIOU"))  # Output: 5
```

**Which one should you use?**
**Option 1** is generally preferred in professional Python code because it is memory-efficient and uses a highly optimized internal loop.
```

**gemma4:**

```
Here are a few ways to implement this. The most efficient and "Pythonic" way is using a generator expression inside the `sum()` function.

### Option 1: The Pythonic Approach (Recommended)
This method is concise and memory-efficient.

```python
def count_vowels(s: str) -> int:
    """Counts the vowels (a, e, i, o, u) in a string, case-insensitive."""
    vowels = "aeiou"
    # Convert string to lowercase once, then check if each char is in vowels
    return sum(1 for char in s.lower() if char in vowels)
```

### Option 2: The Explicit Loop
This is the best approach if you are a beginner and want to see exactly how the logic flows step-by-step.

```python
def count_vowels(s: str) -> int:
    count = 0
    vowels = "aeiouAEIOU"  # Including both cases avoids calling .lower()
    for char in s:
        if char in vowels:
            count += 1
    return count
```

### Explanation:
1.  **Case-Insensitivity**: In Option 1, we use `.lower()` to turn the entire string into lowercase so we only have to compare against `"aeiou"`. In Option 2, we simply include uppercase vowels in our lookup string.
2.  **The `sum()` function**: In Option 1, `sum(1 for char in s if ...)` creates a generator that yields the number `1` every time a vowel is found. Adding those `1`s together gives the total count.
3.  **Complexity**: 
    *   **Time Complexity**: $O(n)$, where $n$ is the length of the string, because we must inspect every character exactly once.
    *   **Space Complexity**: $O(1)$, as we only store a small constant amount of data (the vowel set and the counter).

### Test Cases
```python
print(count_vowels("Hello World"))  # Output: 3 (e, o, o)
print(count_vowels("AEIOU"))        # Output: 5
print(count_vowels("bcdfg"))        # Output: 0
print(count_vowels(""))             # Output:
```

## code-018

**prompt:** Implement `def dedupe(xs: list) -> list` that removes duplicates while preserving first-seen order.

**causal:**

```
To implement this efficiently, the best approach is to use a **set** to keep track of the elements we have already encountered. This allows for $O(1)$ average-time complexity lookups, resulting in an overall $O(n)$ time complexity for the function.

Here are the two most common ways to implement this in Python:

### Option 1: The Classic Approach (Most Readable)
This approach is explicit and works in all versions of Python.

```python
def dedupe(xs: list) -> list:
    seen = set()
    result = []
    for item in xs:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result
```

### Option 2: The Modern Approach (Most Concise)
In Python 3.7+, regular dictionaries are guaranteed to maintain insertion order. We can exploit this by creating a dictionary where the list items are keys, then converting it back to a list.

```python
def dedupe(xs: list) -> list:
    return list(dict.fromkeys(xs))
```

### Comparison

| Feature | Option 1 (Set + Loop) | Option 2 (`dict.fromkeys`) |
| :--- | :--- | :--- |
| **Time Complexity** | $O(n)$ | $O(n)$ |
| **Space Complexity** | $O(n)$ | $O(n)$ |
| **Readability** | Very clear logic | Very concise |
| **Compatibility** | Works in all Python versions | Requires Python 3.7+ |
| **Requirement** | Items must be hashable | Items must be hashable |

### Example Usage
```python
data = [1, 2, 2, 3, 4, 4, 5, 1]
print(dedupe(data)) 
# Output: [1, 2, 3, 4, 5]

data_strings = ["apple", "orange", "apple", "banana"]
print(dedupe(data_strings))
# Output: ['apple', 'orange', 'banana']
```

**Note:** Both methods require the elements in the list to be **hashable** (e.g., integers, strings, tuples). If your list contains unhashable items like nested lists
```

**gemma4:**

```
To implement this efficiently, the best approach is to use a **`set`** to keep track of the elements we have already encountered. A `set` provides $O(1)$ average-case time complexity for lookups, ensuring the overall function runs in $O(n)$ time.

Here is the implementation:

```python
def dedupe(xs: list) -> list:
    """
    Removes duplicates from a list while preserving the original order.
    
    Args:
        xs: A list of hashable elements.
        
    Returns:
        A new list containing only the first occurrence of each element.
    """
    seen = set()
    result = []
    for item in xs:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

# --- Test Cases ---
if __name__ == "__main__":
    # Test 1: Standard integers
    assert dedupe([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
    
    # Test 2: Strings
    assert dedupe(["apple", "banana", "apple", "orange"]) == ["apple", "banana", "orange"]
    
    # Test 3: Already unique
    assert dedupe([1, 2, 3]) == [1, 2, 3]
    
    # Test 4: All duplicates
    assert dedupe([1, 1, 1, 1]) == [1]
    
    # Test 5: Empty list
    assert dedupe([]) == []

    print("All tests passed!")
```

### Complexity Analysis
*   **Time Complexity: $O(n)$**
    We iterate through the list exactly once. Each lookup (`item in seen`) and insertion (`seen.add`) in a set takes $O(1)$ on average.
*   **Space Complexity: $O(n)$**
    In the worst case (where all elements are unique), we store all $n$ elements in both the `seen` set and the `result` list.

### Alternative (Python 3.7+)
If you are using Python 3.7 or newer, regular dictionaries are guaranteed to maintain insertion order. You can use
```

## code-019

**prompt:** Write `def to_title_case(s: str) -> str` that capitalizes the first letter of each word.

**causal:**

```
There are two main ways to approach this in Python, depending on how you want to handle special cases (like words with internal capital letters or apostrophes).

### Option 1: Using the built-in `.title()` method
This is the simplest way, but be aware that it capitalizes letters following apostrophes (e.g., "they're" becomes "They'Re").

```python
def to_title_case(s: str) -> str:
    return s.title()
```

### Option 2: Using `.capitalize()` (Recommended)
This is usually the preferred method because it correctly handles apostrophes (e.g., "they're" stays "They're") by splitting the string into words manually.

```python
def to_title_case(s: str) -> str:
    # Split by whitespace, capitalize each word, and join back together
    return ' '.join(word.capitalize() for word in s.split())

# Examples:
print(to_title_case("hello world"))      # "Hello World"
print(to_title_case("THE QUICK BROWN"))  # "The Quick Brown"
print(to_title_case("it's a test"))      # "It's A Test"
```

### Which one should you use?
*   **Use Option 1** if you want a quick solution and don't care about apostrophes.
*   **Use Option 2** if you want "natural" looking text where words like "don't" or "it's" are formatted correctly.

3.  **Wait, what about "small words"?**
    If you are looking for **"Title Case"** in the grammatical sense (where words like "a", "an", "the", and "of" are lowercase unless they are the first word), you need a more complex approach:

```python
def to_title_case_grammar(s: str) -> str:
    exceptions = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of'}
    words = s.lower().split()
    
    result = []
    for i, word in enumerate(words):
        if i == 0 or word not
```

**gemma4:**

```
There are two main ways to approach this in Python, depending on how you want to handle edge cases (like words with internal capital letters or apostrophes).

### Option 1: Using the built-in `.title()` method
Python has a built-in string method for this. However, be aware that `.title()` capitalizes the first letter after **any** non-alphabetical character (e.g., `"they're"` becomes `"They'Re"`).

```python
def to_title_case(s: str) -> str:
    return s.title()

# Example:
# print(to_title_case("hello world")) -> "Hello World"
# print(to_title_case("they're here")) -> "They'Re Here" (Note the 'R')
```

### Option 2: Using `.split()` and `.capitalize()` (Recommended)
If you want to ensure that only the first letter of a word is capitalized and that apostrophes don't trigger extra capitalization, this is the standard approach.

```python
def to_title_case(s: str) -> str:
    """
    Capitalizes the first letter of each word separated by whitespace.
    """
    return ' '.join(word.capitalize() for word in s.split())

# Example:
# print(to_title_case("hello world"))    -> "Hello World"
# print(to_title_case("they're here"))   -> "They're Here" (Correct behavior)
# print(to_title_case("i'm a little tea pot")) -> "I'm A Little Tea Pot"
```

### Comparison of behaviors:

| Input | `.title()` | `.split()` + `.capitalize()` |
| :--- | :--- | :--- |
| `"hello world"` | `"Hello World"` | `"Hello World"` |
| `"they're"` | `"They'Re"` | `"They're"` |
| `"macdonald"` | `"Macdonald"` | `"Macdonald"` |
| `"iPhone"` | `"Iphone"` | `"Iphone"` |

### Which one should you use?
*   Use **Option 1** if you want a quick, built-in solution and don't care about apostrophes.
*   Use **Option 2** if you want "
```

## code-020

**prompt:** Implement `def sum_digits(n: int) -> int` returning the sum of the decimal digits of a non-negative integer.

**causal:**

```
Here are two common ways to implement this function in Python.

### Option 1: Mathematical Approach (Recommended)
This approach uses the modulo operator (`%`) to get the last digit and floor division (`//`) to remove it. This is generally more efficient as it avoids string conversion.

```python
def sum_digits(n: int) -> int:
    """Returns the sum of the decimal digits of a non-negative integer."""
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total
```

### Option 2: String Conversion (Concise)
This approach converts the integer to a string, iterates through each character, converts it back to an integer, and sums them up.

```python
def sum_digits(n: int) -> int:
    """Returns the sum of the decimal digits of a non-negative integer."""
    return sum(int(digit) for digit in str(n))
```

### Example Usage:
```python
print(sum_digits(123))   # Output: 6 (1+2+3)
print(sum_digits(4005))  # Output: 9 (4+0+0+5)
print(sum_digits(0))     # Output: 0
```

### Which one should you use?
*   **Use Option 1** if you are working with extremely large numbers or in a performance-critical environment, as it avoids the overhead of creating string objects.
*   **Use Option 2** if you want the most readable, "Pythonic" one-liner.
```

**gemma4:**

```
Here are the two most common ways to implement this function in Python.

### Option 1: Mathematical Approach (Recommended)
This approach uses the modulo operator `%` to get the last digit and integer division `//` to remove it. This is generally more efficient as it avoids converting the number to a string.

```python
def sum_digits(n: int) -> int:
    """Returns the sum of the decimal digits of a non-negative integer."""
    total = 0
    while n > 0:
        total += n % 10  # Get the last digit
        n //= 10         # Remove the last digit
    return total
```

### Option 2: String Conversion Approach (Pythonic/Concise)
This approach converts the integer to a string, iterates through each character, converts it back to an integer, and sums them up. It is very readable and idiomatic for Python.

```python
def sum_digits(n: int) -> int:
    """Returns the sum of the decimal digits of a non-negative integer."""
    return sum(int(digit) for digit in str(n))
```

### Comparison

| Feature | Mathematical Approach | String Approach |
| :--- | :--- | :--- |
| **Complexity** | $O(\log_{10} n)$ | $O(\log_{10} n)$ |
| **Memory** | $O(1)$ (Constant) | $O(\log_{10} n)$ (Creates a string) |
| **Performance** | Faster for extremely large numbers | Slightly slower due to type conversion |
| **Readability** | Standard algorithmic logic | Very high (one-liner) |

### Test Cases
You can use these to verify the implementation:

```python
print(sum_digits(123))   # Output: 6 (1+2+3)
print(sum_digits(405))   # Output: 9 (4+0+5)
print(sum_digits(0))     # Output: 0
print(sum_digits(9999))  # Output: 36
```
```

## code-021

**prompt:** Write `def second_largest(xs: list[int]) -> int` returning the second-largest distinct value. Raise ValueError if there are fewer than two distinct values.

**causal:**

```
To find the second-largest distinct value, we can convert the list to a `set` to remove duplicates, sort the unique values, and then select the second-to-last element.

```python
def second_largest(xs: list[int]) -> int:
    # Remove duplicates by converting to a set
    unique_values = set(xs)
    
    # Check if there are at least two distinct values
    if len(unique_values) < 2:
        raise ValueError("List must contain at least two distinct values")
    
    # Sort the unique values and return the second to last
    return sorted(unique_values)[-2]
```

### Alternative O(n) Approach
If the list is very large, sorting ($O(n \log n)$) might be inefficient. Here is an $O(n)$ implementation that tracks the largest and second-largest values in a single pass:

```python
def second_largest(xs: list[int]) -> int:
    if not xs:
        raise ValueError("List is empty")

    first = second = float('-inf')
    found_distinct = False

    for x in xs:
        if x > first:
            second = first
            first = x
            if second != float('-inf'):
                found_distinct = True
        elif x < first and x > second:
            second = x
            found_distinct = True
        elif x < first and second == float('-inf'):
            # This handles the case where we found a second distinct value
            # but it's smaller than the first one found so far
            second = x
            found_distinct = True

    # Re-check logic for edge cases (like all elements being the same)
    # A simpler way to verify distinct count is using the set length
    if len(set(xs)) < 2:
        raise ValueError("List must contain at least two distinct values")
        
    return int(second)
```

**Recommendation:** Use the first (set-based) version for readability unless you are dealing with millions of integers and need maximum performance.
```python
def second_largest(xs: list[int]) -> int:
    """
    Returns the second-largest distinct value in the list.
    Raises ValueError if there are fewer than two
```

**gemma4:**

```
To solve this, the most efficient way is to iterate through the list once while keeping track of the largest and second-largest values encountered so far. Using a `set` first is also a valid approach to handle distinct values, but a single pass is more performant for large lists.

Here is the implementation:

```python
def second_largest(xs: list[int]) -> int:
    """
    Returns the second-largest distinct value in the list.
    Raises ValueError if there are fewer than two distinct values.
    """
    # Initialize with None to handle negative integers correctly
    largest = None
    second = None

    for x in xs:
        # Case 1: We found a new largest value
        if largest is None or x > largest:
            second = largest
            largest = x
        # Case 2: x is smaller than largest, but larger than the current second
        # We must ensure x is not equal to largest to maintain 'distinct' requirement
        elif x < largest and (second is None or x > second):
            second = x

    if second is None:
        raise ValueError("List must contain at least two distinct values.")
    
    return second

# --- Test Cases ---
if __name__ == "__main__":
    print(second_largest([1, 2, 3, 4, 5]))     # Expected: 4
    print(second_largest([10, 10, 9, 8, 10]))  # Expected: 9
    print(second_largest([-1, -5, -2, -10]))   # Expected: -2
    print(second_largest([1]))                 # Raises ValueError
    try:
        second_largest([1, 1, 1])              # Raises ValueError
    except ValueError as e:
        print(f"Caught expected error: {e}")
```

### Explanation:
1.  **Initialization**: We initialize `largest` and `second` to `None`. This allows the function to work correctly even if the list contains negative integers (using `0` as a placeholder would fail if all numbers were negative).
2.  **The Loop**:
    *   If the current number `x` is greater than `largest`, the old `largest` becomes the `second` largest, and `
```

## code-022

**prompt:** Implement `def transpose(matrix: list[list[int]]) -> list[list[int]]` returning the transpose of a rectangular matrix.

**causal:**

```
To transpose a rectangular matrix, we need to convert its rows into columns. This means if the input matrix has dimensions $M \times N$, the output matrix will have dimensions $N \times M$.

Here are two ways to implement this: the **Pythonic approach** (using `zip`) and the **manual approach** (using nested loops).

### Option 1: The Pythonic Approach (Recommended)
This method uses the built-in `zip` function combined with the unpacking operator `*`. `zip(*matrix)` takes each row as a separate argument and groups the $i$-th elements together.

```python
def transpose(matrix: list[list[int]]) -> list[list[int]]:
    # zip(*matrix) creates tuples of columns
    # map(list, ...) converts those tuples back into lists
    return [list(row) for row in zip(*matrix)]
```

### Option 2: The Manual Approach (Algorithmic)
If you want to understand the underlying logic or avoid built-in functions, you can use nested loops.

```python
def transpose(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return []

    rows = len(matrix)
    cols = len(matrix[0])
    
    # Initialize a new matrix with dimensions cols x rows
    # filled with placeholder zeros
    result = [[0 for _ in range(rows)] for _ in range(cols)]
    
    for r in range(rows):
        for c in range(cols):
            # The element at (r, c) moves to (c, r)
            result[c][r] = matrix[r][c]
            
    return result
```

### Example Usage
```python
matrix = [
    [1, 2, 3],
    [4, 5, 6]
]

print(transpose(matrix))
# Output: [[1, 4], [2, 5], [3, 6]]
```

### Complexity Analysis
*   **Time Complexity:** $O(M \times N)$, where $M$ is the number of rows and $N$ is the number of columns, as every element must be visited exactly once.
*   **Space Complexity:** $O(M \times N)$
```

**gemma4:**

```
To transpose a rectangular matrix, you need to convert its rows into columns. This means if the input matrix has dimensions $M \times N$, the resulting matrix will have dimensions $N \times M$.

Here are the two most common ways to implement this in Python.

### Option 1: The Pythonic Way (Using `zip`)
The most efficient and readable way to transpose a matrix in Python is using the built-in `zip` function combined with the unpacking operator `*`.

```python
def transpose(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return []
    
    # zip(*matrix) takes each row as a separate argument and 
    # groups the i-th elements of each row together.
    return [list(row) for row in zip(*matrix)]
```

**How it works:**
1. `*matrix` unpacks the list of lists. If `matrix` is `[[1, 2], [3, 4], [5, 6]]`, it passes `[1, 2]`, `[3, 4]`, and `[5, 6]` as three separate arguments to `zip`.
2. `zip` takes the first element from every list `(1, 3, 5)`, then the second element `(2, 4, 6)`, creating tuples.
3. The list comprehension converts those tuples back into lists.

---

### Option 2: The Algorithmic Way (Using Nested Loops)
If you are practicing for a coding interview where built-in functions like `zip` might be discouraged, you can implement it using manual indexing.

```python
def transpose(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return []

    rows = len(matrix)
    cols = len(matrix[0])

    # Create a new matrix with dimensions: cols x rows
    # We initialize it with zeros (or any placeholder)
    result = [[0 for _ in range(rows)] for _ in range(cols)]

    for r in range(rows):
        for c in range(cols):
            # The element at [r][c] moves to [c][r]
            result[c][r]
```

## code-023

**prompt:** Write `def roman_to_int(s: str) -> int` converting a Roman numeral string to an integer.

**causal:**

```
To convert a Roman numeral to an integer, the most efficient approach is to iterate through the string and compare the value of the current character with the value of the next character. 

If the current value is **less than** the next value, it means we are looking at a "subtractive" case (like IV or IX), so we subtract the current value from the total. Otherwise, we add it.

Here is the implementation:

```python
def roman_to_int(s: str) -> int:
    # Map of Roman numerals to their integer values
    roman_map = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }
    
    total = 0
    n = len(s)
    
    for i in range(n):
        current_val = roman_map[s[i]]
        
        # If this is not the last character and the current value 
        # is less than the next value, subtract it.
        if i + 1 < n and current_val < roman_map[s[i + 1]]:
            total -= current_val
        else:
            total += current_val
            
    return total

# Test cases
print(roman_to_int("III"))      # Output: 3
print(roman_to_int("LVIII"))    # Output: 58
print(roman_to_int("MCMXCIV"))  # Output: 1994
```

### How it works:
1. **The Dictionary**: We store the basic Roman symbols in a hash map for $O(1)$ lookup time.
2. **The Loop**: We traverse the string from left to right.
3. **The Logic**:
   - In Roman numerals, if a smaller number precedes a larger one (e.g., `IV`), it is subtracted ($5 - 1 = 4$).
   - If a number is followed by one of equal or lesser value (e.g., `VI`), it is added ($5 + 1 = 6$).
4. **Complexity**:
```

**gemma4:**

```
To convert a Roman numeral to an integer, the most efficient approach is to iterate through the string and compare each numeral with the one following it. If a numeral is smaller than the next one (e.g., `IV`), it means we should **subtract** its value; otherwise, we **add** it.

Here is the implementation:

```python
def roman_to_int(s: str) -> int:
    """
    Converts a Roman numeral string to an integer.
    """
    # Mapping of Roman numerals to their integer values
    roman_map = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }
    
    total = 0
    n = len(s)
    
    for i in range(n):
        # Get the value of the current symbol
        current_val = roman_map[s[i]]
        
        # If this is not the last character and the current value 
        # is less than the next value, we subtract it (subtractive notation)
        if i + 1 < n and current_val < roman_map[s[i + 1]]:
            total -= current_val
        else:
            total += current_val
            
    return total

# --- Test Cases ---
if __name__ == "__main__":
    test_cases = {
        "III": 3,
        "LVIII": 58,
        "MCMXCIV": 1994,
        "IX": 9,
        "XL": 40
    }

    for roman, expected in test_cases.items():
        result = roman_to_int(roman)
        print(f"{roman} => {result} (Expected: {expected}) {'✅' if result == expected else '❌'}")
```

### How it works:
1.  **The Dictionary**: We store the basic Roman numeral values in a hash map (dictionary) for $O(1)$ lookup.
2.  **The Logic**: 
    *   In Roman numerals, if a
```

## code-024

**prompt:** Implement `def int_to_roman(n: int) -> str` converting an integer (1-3999) to a Roman numeral.

**causal:**

```
To convert an integer to a Roman numeral, the most efficient approach is to map the standard Roman symbols (and their subtractive combinations like "IV" or "CM") to their integer values in descending order. We then iterate through this mapping, subtracting the value from the input number until it is exhausted.

Here is the implementation:

```python
def int_to_roman(n: int) -> str:
    """
    Converts an integer (1-3999) to a Roman numeral.
    """
    # Define the mapping of values to Roman symbols in descending order.
    # We include subtractive combinations (like IV, IX, XL, etc.) 
    # to simplify the greedy subtraction logic.
    roman_map = [
        (1000, "M"), (900, "CM"), (500, "D"), (900, "CM"), # Wait, 900 is CM
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]
    
    # Cleaned up mapping list
    mapping = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]
    
    result = []
    
    for value, symbol in mapping:
        # Determine how many times the current symbol fits into n
        count = n // value
        if count > 0:
            result.append(symbol * count)
            n %= value
            
    return "".join(result)

# Examples
if __name__ == "__main__":
    print(int
```

**gemma4:**

```
To convert an integer to a Roman numeral, the most efficient approach is to map the standard Roman symbols (including the "subtractive" combinations like `IV` or `CM`) to their integer values in descending order. We then iterate through this mapping, subtracting the value from $n$ as many times as possible while appending the corresponding symbol to our result string.

Here is the implementation:

```python
def int_to_roman(n: int) -> str:
    """
    Converts an integer (1-3999) to a Roman numeral string.
    """
    # Define the mapping of values to Roman symbols in descending order.
    # We include subtractive combinations (like IV, IX, etc.) to simplify the logic.
    roman_map = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    
    result = []
    
    for value, symbol in roman_map:
        # If n is 0, we can stop early
        if n == 0:
            break
            
        # Determine how many times the current symbol fits into n
        count = n // value
        if count > 0:
            result.append(symbol * count)
            # Reduce n by the amount we just converted
            n %= value
            
    return "".join(result)

# --- Test Cases ---
if __name__ == "__main__":
    test_cases = {
        3: "III",
        58: "LVIII",
        1994: "MCMXCIV",
        3999: "MMMCMXCIX"
    }

    for num, expected in test_cases.items():
        actual = int_to_roman(num)
        print(f"Input: {num:4} | Expected: {expected:10} | Actual: {actual:10} | {'✅' if actual == expected else
```

## code-025

**prompt:** Write `def is_anagram(a: str, b: str) -> bool` that returns True if the two strings are anagrams, ignoring case and spaces.

**causal:**

```
To determine if two strings are anagrams while ignoring case and spaces, the most efficient approach is to normalize both strings (remove spaces and convert to lowercase) and then compare their sorted character lists.

Here is the implementation:

```python
def is_anagram(a: str, b: str) -> bool:
    # Remove spaces and convert to lowercase
    clean_a = a.replace(" ", "").lower()
    clean_b = b.replace(" ", "").lower()
    
    # If lengths differ after cleaning, they cannot be anagrams
    if len(clean_a) != len(clean_b):
        return False
    
    # Compare sorted versions of the strings
    return sorted(clean_a) == sorted(clean_b)

# Test cases
print(is_anagram("Listen", "Silent"))      # True
print(is_anagram("Clint Eastwood", "Old West Action")) # True
print(is_anagram("Hello", "World"))        # False
```

### How it works:
1. **Normalization**: We use `.replace(" ", "")` to strip out all whitespace and `.lower()` to ensure the comparison is case-insensitive.
2. **Length Check**: A quick optimization; if the strings don't have the same number of characters after cleaning, they cannot be anagrams.
3. **Sorting**: Anagrams contain the exact same characters with the exact same frequencies. By sorting both strings, we create a "canonical form." If the sorted lists are identical, the strings are anagrams.

**Complexity:**
*   **Time Complexity**: $O(N \log N)$, where $N$ is the length of the strings (due to the sorting algorithm).
*   **Space Complexity**: $O(N)$ to store the cleaned and sorted versions of the strings.
```

**gemma4:**

```
To solve this, we need to normalize both strings by removing spaces and converting them to lowercase. Once normalized, two strings are anagrams if they contain the exact same characters with the same frequencies.

The most efficient way to do this is by using a character count (via `collections.Counter`).

```python
from collections import Counter

def is_anagram(a: str, b: str) -> bool:
    """
    Returns True if the two strings are anagrams, 
    ignoring case and spaces.
    """
    # Normalize strings: remove spaces and convert to lowercase
    clean_a = a.replace(" ", "").lower()
    clean_b = b.replace(" ", "").lower()
    
    # If lengths differ after cleaning, they cannot be anagrams
    if len(clean_a) != len(clean_b):
        return False
    
    # Compare character frequencies
    return Counter(clean_a) == Counter(clean_b)

# --- Test Cases ---
if __name__ == "__main__":
    print(is_anagram("Listen", "Silent"))          # True
    print(is_anagram("Clint Eastwood", "Old West Action")) # True
    print(is_anagram("hello", "world"))            # False
    print(is_anagram("Dormitory", "Dirty Room"))   # True
    print(is_anagram("a", "aa"))                   # False
```

### Explanation:
1.  **Normalization**: We use `.replace(" ", "")` to strip all whitespace and `.lower()` to ensure the comparison is case-insensitive.
2.  **Length Check**: A quick optimization; if the number of characters differs after cleaning, we return `False` immediately.
3.  **`Counter`**: This class from the `collections` module creates a dictionary-like object where keys are characters and values are their counts. Comparing two `Counter` objects checks if every character appears the same number of times in both strings.
4.  **Complexity**:
    *   **Time Complexity**: $O(n)$, where $n$ is the length of the strings, as we iterate through the strings a constant number of times.
    *   **Space Complexity**: $O(k)$, where $k$ is the number of unique characters in the alphabet (at most 26 for English letters).
```

## code-026

**prompt:** Implement `def rle_encode(s: str) -> str` performing run-length encoding, e.g. 'aaabb' -> 'a3b2'.

**causal:**

```
To implement Run-Length Encoding (RLE), we iterate through the string while keeping track of the current character and its consecutive count. When the character changes, we append the character and its count to the result string.

Here is the implementation:

```python
def rle_encode(s: str) -> str:
    if not s:
        return ""

    encoded_parts = []
    current_char = s[0]
    count = 0

    for char in s:
        if char == current_char:
            count += 1
        else:
            # Append the previous character and its count
            encoded_parts.append(f"{current_char}{count}")
            # Reset for the new character
            current_char = char
            count = 1

    # Append the final character and count after the loop finishes
    encoded_parts.append(f"{current_char}{count}")

    return "".join(encoded_parts)

# Test cases
print(rle_encode("aaabb"))      # Output: 'a3b2'
print(rle_encode("aaabbbba"))   # Output: 'a3b4a1'
print(rle_encode("abc"))        # Output: 'a1b1c1'
print(rle_encode(""))           # Output: ''
```

### Key Details:
1.  **Efficiency**: We use a list (`encoded_parts`) to collect the strings and `"".join()` at the end. This is more efficient than repeated string concatenation (`s += ...`), which creates a new string object in every iteration ($O(n^2)$ complexity).
2.  **Edge Cases**: The function handles empty strings immediately by returning `""`.
3.  **Complexity**: 
    *   **Time Complexity**: $O(n)$, where $n$ is the length of the string, as we traverse the string exactly once.
    *   **Space Complexity**: $O(n)$ to store the encoded result.
```

**gemma4:**

```
To implement Run-Length Encoding (RLE), we iterate through the string while keeping track of the current character and how many times it has appeared consecutively. When the character changes, we append the character and its count to a list and reset the counter.

Here is the implementation:

```python
def rle_encode(s: str) -> str:
    """
    Performs run-length encoding on the input string.
    Example: 'aaabb' -> 'a3b2'
    """
    if not s:
        return ""

    encoded_parts = []
    current_char = s[0]
    count = 0

    for char in s:
        if char == current_char:
            count += 1
        else:
            # Append the previous character and its count
            encoded_parts.append(f"{current_char}{count}")
            # Reset for the new character
            current_char = char
            count = 1

    # Append the final group after the loop finishes
    encoded_parts.append(f"{current_char}{count}")

    return "".join(encoded_parts)

# Test cases
if __name__ == "__main__":
    print(f"aaabb     -> {rle_encode('aaabb')}")      # Expected: a3b2
    print(f"abbcccdd  -> {rle_encode('abbcccdd')}")   # Expected: a1b2c3d2
    print(f"abc       -> {rle_encode('abc')}")        # Expected: a1b1c1
    print(f"aaaaa     -> {rle_encode('aaaaa')}")      # Expected: a5
    print(f"''        -> '{rle_encode('')}'")         # Expected: ''
```

### Key Details:
1.  **Complexity**: 
    *   **Time Complexity**: $O(n)$, where $n$ is the length of the string, as we traverse the string exactly once.
    *   **Space Complexity**: $O(n)$ in the worst case (e.g., "abcde" becomes "a1b1c1d1e1") to store the resulting string parts.
2.  **Efficiency**: I used a list (`encoded_parts`) and
```

## code-027

**prompt:** Write `def caesar(s: str, shift: int) -> str` applying a Caesar cipher to letters, leaving non-letters unchanged.

**causal:**

```
To implement a Caesar cipher, we iterate through each character in the string. If the character is a letter, we shift it within the bounds of the alphabet (26 letters) while preserving its case (uppercase or lowercase). Non-letter characters are returned as-is.

Here is the implementation:

```python
def caesar(s: str, shift: int) -> str:
    result = []
    
    for char in s:
        if char.isalpha():
            # Determine if the character is uppercase or lowercase to set the ASCII base
            start = ord('A') if char.isupper() else ord('a')
            
            # 1. Convert char to 0-25 scale (char - start)
            # 2. Apply the shift
            # 3. Use modulo 26 to handle wrap-around (and negative shifts)
            # 4. Convert back to ASCII ( + start)
            new_char = chr((ord(char) - start + shift) % 26 + start)
            result.append(new_char)
        else:
            # If it's not a letter, leave it unchanged
            result.append(char)
            
    return "".join(result)

# Examples:
# caesar("Hello, World!", 3)  -> "Khoor, Zruog!"
# caesar("abc", -1)           -> "zab"
```

### How it works:
1. **`ord(char)`**: Converts a character into its integer ASCII/Unicode value (e.g., 'A' is 65).
2. **`start`**: We subtract the base value (65 for 'A', 97 for 'a') to turn the letter into a number between 0 and 25. This makes the math easier.
3. **`% 26`**: This is the most important part. It ensures that if the shift goes past 'Z', it wraps back around to 'A'. It also correctly handles negative shifts.
4. **`chr(...)`**: Converts the resulting integer back into a character.
5. **`"".join(result)`**: We collect characters in a list and join them at the end, which is more memory-efficient than repeated string concatenation in Python.
```

**gemma4:**

```
To implement a Caesar cipher, we iterate through each character in the string. If the character is a letter, we shift it within its case boundaries (`a-z` or `A-Z`) using modulo arithmetic to ensure it wraps around. Non-letter characters are appended to the result unchanged.

Here is the implementation:

```python
def caesar(s: str, shift: int) -> str:
    result = []
    
    for char in s:
        if char.isalpha():
            # Determine if the character is uppercase or lowercase to set the ASCII base
            start = ord('A') if char.isupper() else ord('a')
            
            # 1. Convert char to 0-25 scale (char - start)
            # 2. Apply the shift
            # 3. Use modulo 26 to handle wrap-around and negative shifts
            # 4. Convert back to ASCII ( + start)
            new_char = chr((ord(char) - start + shift) % 26 + start)
            result.append(new_char)
        else:
            # If it's not a letter (space, punctuation, digit), leave it as is
            result.append(char)
            
    return "".join(result)

# Examples
if __name__ == "__main__":
    print(caesar("Hello, World!", 3))    # Output: "Khoor, Zruog!"
    print(caesar("abc", -1))             # Output: "zab" (handles negative shifts)
    print(caesar("Python 3.10", 5))      # Output: "Udymts 3.10" (ignores numbers/dots)
```

### Key Details:
1.  **`ord()` and `chr()`**: `ord()` converts a character to its integer Unicode point, and `chr()` converts an integer back to a character.
2.  **Modulo Operator (`% 26`)**: This is the most important part. It ensures that if you shift 'z' by 1, it wraps back to 'a'. It also automatically handles negative shifts (e.g., `-1 % 26` becomes `25` in Python), making the function robust for decoding.
3.  **Complexity**: 
    *   **Time Complexity**: $
```

## code-028

**prompt:** Implement `def moving_average(xs: list[float], k: int) -> list[float]` returning the simple moving average over a window of size k.

**causal:**

```
To implement a moving average efficiently, we use a **sliding window** approach. Instead of re-summing $k$ elements for every position (which would be $O(n \cdot k)$), we maintain a running sum, adding the new element and subtracting the one that just left the window ($O(n)$).

Here is the implementation:

```python
def moving_average(xs: list[float], k: int) -> list[float]:
    """
    Returns the simple moving average of xs over a window of size k.
    The result list will have length len(xs) - k + 1.
    """
    if not xs or k <= 0:
        return []
    if k > len(xs):
        return []

    result = []
    current_window_sum = sum(xs[:k])
    result.append(current_window_sum / k)

    for i in range(len(xs) - k):
        # Subtract the element leaving the window, add the element entering
        current_window_sum = current_window_sum - xs[i] + xs[i + k]
        result.append(current_window_sum / k)

    return result

# Example usage:
# data = [1.0, 2.0, 3.0, 4.0, 5.0]
# print(moving_average(data, 3)) 
# Output: [2.0, 3.0, 4.0] -> (1+2+3)/3, (2+3+4)/3, (3+4+5)/3
```

### Key Details:
1.  **Time Complexity**: $O(n)$, where $n$ is the length of `xs`. We traverse the list once.
2.  **Space Complexity**: $O(n - k)$, to store the resulting averages.
3.  **Edge Cases**: 
    *   If $k$ is larger than the list length, it returns an empty list.
    *   If $k$ is 0 or negative, it returns an empty list.
4.  **Precision**: For extremely large lists or very small floating-point numbers, repeated addition/subtraction can lead to floating-point drift. However, for standard use cases, this sliding
```

**gemma4:**

```
To implement a moving average efficiently, the best approach is to use a **sliding window**. Instead of re-summing $k$ elements for every position (which would be $O(n \cdot k)$), we maintain a running sum, add the new element entering the window, and subtract the element leaving it. This ensures $O(n)$ time complexity.

Here is the implementation:

```python
def moving_average(xs: list[float], k: int) -> list[float]:
    """
    Returns the simple moving average of xs over a window of size k.
    
    Args:
        xs: A list of floats.
        k: The size of the moving window.
        
    Returns:
        A list of floats representing the moving averages. 
        The length of the returned list will be len(xs) - k + 1.
        Returns an empty list if k > len(xs) or k <= 0.
    """
    n = len(xs)
    if k <= 0 or k > n:
        return []

    # Calculate the sum of the first window
    current_window_sum = sum(xs[:k])
    result = [current_window_sum / k]

    # Slide the window across the rest of the list
    for i in range(n - k):
        # Subtract the element leaving the window (xs[i])
        # Add the element entering the window (xs[i + k])
        current_window_sum += xs[i + k] - xs[i]
        result.append(current_window_sum / k)

    return result

# --- Test Cases ---
if __name__ == "__main__":
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    
    # Window size 3: 
    # [(1+2+3)/3, (2+3+4)/3, (3+4+5)/3, (4+5+6)/3]
    print(f"k=3: {moving_average(data, 3)}") 
    # Expected: [2.0, 3.0, 4.0, 5.0]

    # Window size
```

## code-029

**prompt:** Write `def chunk(xs: list, size: int) -> list[list]` that splits a list into consecutive chunks of the given size.

**causal:**

```
Here are the two most common ways to implement this in Python.

### Option 1: Using a List Comprehension (Recommended)
This is the most "Pythonic" and concise way. It uses slicing to grab segments of the list.

```python
def chunk(xs: list, size: int) -> list[list]:
    """Splits a list into consecutive chunks of the given size."""
    if size <= 0:
        raise ValueError("Chunk size must be greater than 0")
    
    return [xs[i : i + size] for i in range(0, len(xs), size)]
```

### Option 2: Using a Generator (Memory Efficient)
If you are dealing with a very large list and don't want to create a new list of lists in memory immediately, use a generator.

```python
from typing import Generator

def chunk_generator(xs: list, size: int) -> Generator[list, None, None]:
    """Yields consecutive chunks of the given size."""
    if size <= 0:
        raise ValueError("Chunk size must be greater than 0")
        
    for i in range(0, len(xs), size):
        yield xs[i : i + size]

# Usage:
# for c in chunk_generator(my_list, 3):
#     print(c)
```

### How it works:
1. **`range(0, len(xs), size)`**: This creates a sequence of numbers starting at 0, ending at the length of the list, and skipping by the `size` amount (e.g., 0, 3, 6, 9...).
2. **`xs[i : i + size]`**: This uses Python's slicing syntax. It takes the elements from index `i` up to (but not including) `i + size`.
3. **The Final Chunk**: Python's slicing is forgiving; if `i + size` is greater than the length of the list, it simply returns the remaining elements, so you don't need extra logic to handle the "tail" of the list.

### Example Usage:
```python
data = [1, 2, 3, 4, 5, 6, 7, 8]
print(chunk(data, 3))
#
```

**gemma4:**

```
Here are the two most common ways to implement this.

### Option 1: Using a List Comprehension (Most Pythonic)
This is the most concise and readable way to solve the problem using Python's slicing syntax.

```python
def chunk(xs: list, size: int) -> list[list]:
    """Splits a list into consecutive chunks of the given size."""
    if size <= 0:
        raise ValueError("Size must be a positive integer.")
    return [xs[i : i + size] for i in range(0, len(xs), size)]

# Example usage:
print(chunk([1, 2, 3, 4, 5, 6, 7, 8], 3))
# Output: [[1, 2, 3], [4, 5, 6], [7, 8]]
```

### Option 2: Using a Generator (Memory Efficient)
If you are dealing with extremely large lists, it is better to use a **generator**. This avoids creating a new list of lists in memory all at once, instead yielding one chunk at a time.

```python
from typing import Generator

def chunk_generator(xs: list, size: int) -> Generator[list, None, None]:
    """Yields consecutive chunks of the given size one by one."""
    if size <= 0:
        raise ValueError("Size must be a positive integer.")
    for i in range(0, len(xs), size):
        yield xs[i : i + size]

# Example usage:
for c in chunk_generator([1, 2, 3, 4, 5, 6, 7, 8], 3):
    print(c)
# Output:
# [1, 2, 3]
# [4, 5, 6]
# [7, 8]
```

### Key Details:
1.  **Slicing Safety**: Python's slicing (`xs[i : i + size]`) is "safe." If the remaining elements are fewer than the `size`, it will simply return the remaining elements rather than throwing an error.
2.  **Complexity**: 
    *   **Time Complexity**: $O(n)$, where $n$ is the length of the list, as we must
```

## code-030

**prompt:** Implement `def deep_get(d: dict, path: str, default=None)` that looks up a dotted key path like 'a.b.c' in nested dicts.

**causal:**

```
To implement this, we can split the path by the dot delimiter and iterate through the dictionary levels. We must handle cases where a key is missing or where a value in the path is not a dictionary (which would prevent further nesting).

Here is the implementation:

```python
def deep_get(d: dict, path: str, default=None):
    """
    Look up a dotted key path in a nested dictionary.
    
    Args:
        d (dict): The dictionary to search.
        path (str): The dotted path (e.g., 'a.b.c').
        default: The value to return if the path is not found.
        
    Returns:
        The value at the path if found, otherwise the default.
    """
    if not isinstance(d, dict):
        return default
    
    keys = path.split('.')
    current = d
    
    for key in keys:
        # Check if current level is a dict and contains the key
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
            
    return current

# --- Test Cases ---
data = {
    "user": {
        "id": 1,
        "profile": {
            "name": "Alice",
            "settings": {"theme": "dark"}
        }
    },
    "status": "active"
}

print(deep_get(data, "user.profile.name"))           # Output: Alice
print(deep_get(data, "user.profile.settings.theme")) # Output: dark
print(deep_get(data, "user.id"))                     # Output: 1
print(deep_get(data, "user.age", "N/A"))             # Output: N/A (Missing key)
print(deep_get(data, "status.code"))                 # Output: None (Not a dict)
```

### How it works:
1. **`path.split('.')`**: We break the string (e.g., `"a.b.c"`) into a list of keys `['a', 'b', 'c']`.
2. **Iteration**: We loop through each key.
3. **Type Checking**: At every step, we
```

**gemma4:**

```
To implement this, the most robust approach is to split the path by the delimiter (`.`) and iterate through the dictionary levels. We must also handle cases where a key might not exist or where a value in the path is not a dictionary (which would prevent further nesting).

Here is the implementation:

```python
def deep_get(d: dict, path: str, default=None):
    """
    Look up a dotted key path in a nested dictionary.
    
    :param d: The dictionary to search.
    :param path: A string representing the path (e.g., 'a.b.c').
    :param default: The value to return if the path is not found.
    :return: The value at the path or the default value.
    """
    if not path:
        return d
    
    keys = path.split('.')
    current = d
    
    for key in keys:
        # Check if current is a dict and contains the key
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
            
    return current

# --- Test Cases ---
data = {
    "a": {
        "b": {
            "c": 42,
            "d": None
        },
        "e": [1, 2, 3]
    },
    "f": "hello"
}

print(f"Found value: {deep_get(data, 'a.b.c')}")          # Expected: 42
print(f"Found None:  {deep_get(data, 'a.b.d')}")         # Expected: None
print(f"Missing key: {deep_get(data, 'a.x.y', 'N/A')}")  # Expected: 'N/A'
print(f"Wrong type:  {deep_get(data, 'f.g', 'N/A')}")    # Expected: 'N/A' (f is a string, not a dict)
print(f"Empty path:  {deep_get(data, '')}")               # Expected: Entire dict
```

### Key Features of this Implementation:

1.  **Type Safety**: It uses `isinstance(current, dict
```

## code-031

**prompt:** Fix the off-by-one bug in this function:

def last_n(xs, n):
    return xs[len(xs) - n - 1:]

**causal:**

```
The off-by-one bug is caused by the `- 1` in the slice index. In Python, the slice `[start:]` includes the element at the `start` index. To get the last $n$ elements, you simply need to subtract $n$ from the total length.

Here is the fixed function:

```python
def last_n(xs, n):
    return xs[len(xs) - n:]
```

### Pythonic Alternative
In Python, you can use **negative indexing** to achieve the same result more concisely. `xs[-n:]` automatically starts $n$ elements from the end of the list:

```python
def last_n(xs, n):
    return xs[-n:] if n > 0 else []
```

### Why the original was broken:
If `xs = [1, 2, 3, 4, 5]` and `n = 2`:
*   **Original:** `xs[5 - 2 - 1:]` $\rightarrow$ `xs[2:]` $\rightarrow$ `[3, 4, 5]` (3 elements instead of 2)
*   **Fixed:** `xs[5 - 2:]` $\rightarrow$ `xs[3:]` $\rightarrow$ `[4, 5]` (Correct)
```

**gemma4:**

```
The bug is in the slice index: `len(xs) - n - 1`. By subtracting an extra `1`, you are actually returning $n+1$ elements instead of $n$.

In Python, the most idiomatic and safest way to get the last $n$ elements is to use a **negative index**.

### Fixed Version (Idiomatic)
This version is cleaner and automatically handles cases where $n$ is larger than the list length.

```python
def last_n(xs, n):
    return xs[-n:] if n > 0 else []
```

### Fixed Version (Mathematical)
If you want to keep your original logic of calculating the starting index, simply remove the `- 1`:

```python
def last_n(xs, n):
    # If n is 0, this would return xs[len(xs):] which is [] (correct)
    # If n is larger than len(xs), this would result in a negative index 
    # which Python handles gracefully.
    return xs[len(xs) - n:]
```

### Why the original was broken:
If `xs = [1, 2, 3, 4, 5]` and `n = 2`:
* **Expected:** `[4, 5]`
* **Your code:** `len(xs) - n - 1` $\rightarrow$ `5 - 2 - 1` = `2`.
* **Result:** `xs[2:]` $\rightarrow$ `[3, 4, 5]` (3 elements instead of 2).

### Edge Case Note:
If `n = 0`, the idiomatic `xs[-n:]` becomes `xs[0:]`, which returns the **entire list**. I added a conditional `if n > 0 else []` in the idiomatic version to ensure that requesting zero elements correctly returns an empty list.
```

## code-032

**prompt:** Add error handling so this returns None instead of raising on bad input:

def parse_int(s):
    return int(s)

**causal:**

```
You can use a `try...except` block to catch the `ValueError` that occurs when `int()` fails.

```python
def parse_int(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None
```

### Explanation:
*   **`ValueError`**: Caught if the input is a string that doesn't look like a number (e.g., `"abc"`).
*   **`TypeError`**: Caught if the input is a type that cannot be converted to an integer at all (e.g., a `list` or `None`).
*   **`return None`**: This ensures the function exits gracefully without crashing your program.
```

**gemma4:**

```
To handle errors and return `None` instead of raising a `ValueError` (which occurs when the input cannot be converted to an integer), you should use a `try...except` block.

Here is the updated code:

```python
def parse_int(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None
```

### Explanation:
1.  **`try:`**: This block attempts to execute the conversion.
2.  **`except (ValueError, TypeError):`**: 
    *   `ValueError` handles cases where the input is a string that doesn't look like a number (e.g., `"abc"`).
    *   `TypeError` handles cases where the input is a type that cannot be converted at all (e.g., `None` or a `list`).
3.  **`return None`**: If either error occurs, the function exits gracefully and returns `None`.

### Test Cases:
```python
print(parse_int("123"))    # Output: 123
print(parse_int("abc"))    # Output: None
print(parse_int(None))     # Output: None
print(parse_int("12.5"))   # Output: None (int() fails on decimal strings)
```
```

## code-033

**prompt:** Rewrite this recursive function iteratively:

def sum_to(n):
    if n == 0:
        return 0
    return n + sum_to(n - 1)

**causal:**

```
To rewrite this recursive function iteratively, you can use a `while` loop or a `for` loop to accumulate the sum.

Here are the two most common ways to do it:

### Option 1: Using a `while` loop (Most direct translation)
This approach mimics the recursive logic by decrementing `n` until it reaches 0.

```python
def sum_to(n):
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total
```

### Option 2: Using a `for` loop (More Pythonic)
This approach uses the built-in `range` function, which is generally faster and cleaner in Python.

```python
def sum_to(n):
    total = 0
    # range(start, stop, step)
    # We go from n down to 1
    for i in range(n, 0, -1):
        total += i
    return total
```

### Option 3: The Mathematical Approach (Most Efficient)
While not "iterative" in the sense of using a loop, it is the most efficient way to solve this specific problem (O(1) time complexity) using Gauss's formula:

```python
def sum_to(n):
    return n * (n + 1) // 2
```

### Comparison
| Method | Time Complexity | Space Complexity | Note |
| :--- | :--- | :--- | :--- |
| **Recursive** | $O(n)$ | $O(n)$ | Risk of `RecursionError` for large $n$. |
| **Iterative** | $O(n)$ | $O(1)$ | Safe for large $n$. |
| **Mathematical**| $O(1)$ | $O(1)$ | Fastest possible solution. |
```

**gemma4:**

```
To rewrite this function iteratively, you need to replace the recursive calls with a loop and a variable to keep track of the running total.

Here are the two most common ways to do it:

### 1. Using a `while` loop (Closest to the original logic)
This approach mimics the recursive process by decrementing `n` until it reaches zero.

```python
def sum_to(n):
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total
```

### 2. Using a `for` loop (More Pythonic)
Since we know the range of numbers we are summing, a `for` loop with `range()` is cleaner and more efficient in Python.

```python
def sum_to(n):
    total = 0
    # range(1, n + 1) includes all numbers from 1 up to and including n
    for i in range(1, n + 1):
        total += i
    return total
```

### Comparison

| Feature | Recursive Version | Iterative Version |
| :--- | :--- | :--- |
| **Memory** | Uses $O(n)$ stack space (can cause `RecursionError` for large $n$). | Uses $O(1)$ space (constant memory). |
| **Speed** | Slower due to function call overhead. | Faster. |
| **Limit** | Limited by Python's maximum recursion depth. | Limited only by your computer's memory/integer size. |

**Note:** If you want the absolute most efficient way to calculate this mathematically, you would use **Gauss's Formula**:
```python
def sum_to(n):
    return n * (n + 1) // 2
```
```

## code-034

**prompt:** Fix the mutable default argument bug:

def append_item(item, items=[]):
    items.append(item)
    return items

**causal:**

```
To fix the mutable default argument bug, you should set the default value to `None` and initialize the list inside the function body.

### The Fixed Code
```python
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Why the original code was broken
In Python, default arguments are evaluated only **once** at the time the function is defined, not every time the function is called. 

If you use a mutable object like a list (`[]`) as a default argument, that same list object is shared across every single call to the function. This leads to unexpected behavior where items from previous calls persist in the list.

### Comparison

**The Buggy Way:**
```python
print(append_item("apple")) # ['apple']
print(append_item("banana")) # ['apple', 'banana'] (Wait, what?)
```

**The Fixed Way:**
```python
print(append_item("apple")) # ['apple']
print(append_item("banana")) # ['banana'] (Correct behavior)
```
```

**gemma4:**

```
To fix this bug, you should use `None` as the default value and initialize the list inside the function body. 

In Python, default arguments are evaluated only once at the time the function is defined, not every time the function is called. This causes the same list object to be reused across all calls.

### The Fixed Code

```python
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Why this works:
1. **`items=None`**: `None` is immutable. Every time the function is called without a second argument, it starts with the same `None` value.
2. **`if items is None`**: Inside the function, we check if the user provided a list. If they didn't, we create a **new** empty list `[]` locally.
3. **Isolation**: Because a new list is created during the function execution, calls to the function no longer share state.

### Comparison

**The Buggy Version:**
```python
print(append_item(1)) # Output: [1]
print(append_item(2)) # Output: [1, 2] (Wait, where did the 1 come from?)
```

**The Fixed Version:**
```python
print(append_item(1)) # Output: [1]
print(append_item(2)) # Output: [2] (Correct!)
```
```

## code-035

**prompt:** Make this function pure (no print, return the result instead):

def greet(name):
    print(f'Hello, {name}!')

**causal:**

```
To make this function pure, you should remove the side effect (the `print` statement) and instead `return` the string.

```python
def greet(name):
    return f'Hello, {name}!'
```

### Why this is now "pure":
1.  **No Side Effects:** It no longer modifies the outside world (printing to the console is considered a side effect).
2.  **Deterministic:** Given the same input (e.g., `"Alice"`), it will always return the exact same output (`"Hello, Alice!"`).
3.  **Testable:** You can now easily test the function by asserting its return value.
```

**gemma4:**

```
To make this function pure, you must remove the side effect (the `print` statement) and instead `return` the string that would have been printed.

```python
def greet(name):
    return f'Hello, {name}!'
```

### Why this is now "pure":
1.  **No Side Effects:** It no longer interacts with the outside world (the console/terminal). It only computes a value.
2.  **Deterministic:** Given the same input (e.g., `"Alice"`), it will always return the exact same output (`"Hello, Alice!"`).
3.  **Testability:** You can now easily write a test to check if the output is correct (e.g., `assert greet("Alice") == "Hello, Alice!"`), which is much harder to do when a function only prints to the console.
```

## code-036

**prompt:** Implement `def bubble_sort(xs: list[int]) -> list[int]` returning a new sorted list using bubble sort.

**causal:**

```
To implement bubble sort while returning a **new** sorted list, we first create a copy of the input list to ensure the original remains unmodified.

Here is the implementation:

```python
def bubble_sort(xs: list[int]) -> list[int]:
    # Create a copy of the list to avoid mutating the original input
    sorted_list = list(xs)
    n = len(sorted_list)
    
    # Outer loop to traverse through all list elements
    for i in range(n):
        # Last i elements are already in place, so we ignore them
        # We use a flag to optimize: if no swaps happen, the list is sorted
        swapped = False
        
        for j in range(0, n - i - 1):
            # Compare the element with the next one
            if sorted_list[j] > sorted_list[j + 1]:
                # Swap if the element found is greater than the next element
                sorted_list[j], sorted_list[j + 1] = sorted_list[j + 1], sorted_list[j]
                swapped = True
        
        # If no two elements were swapped by inner loop, then break
        if not swapped:
            break
            
    return sorted_list

# Example usage:
if __name__ == "__main__":
    nums = [64, 34, 25, 12, 22, 11, 90]
    sorted_nums = bubble_sort(nums)
    print(f"Original: {nums}")
    print(f"Sorted:   {sorted_nums}")
```

### Key Features of this Implementation:
1.  **Immutability**: By calling `list(xs)`, we ensure the function follows functional programming principles by not modifying the input argument.
2.  **Optimization (The `swapped` flag)**: Bubble sort has a worst-case complexity of $O(n^2)$, but with the `swapped` flag, it achieves $O(n)$ in the best-case scenario (when the list is already sorted).
3.  **Efficiency**: The inner loop range `n - i - 1` ensures we don't re-check the end of the list that has already been "bubbled" into
```

**gemma4:**

```
To implement `bubble_sort` such that it returns a **new** sorted list (leaving the original list unchanged), we first create a copy of the input list and then perform the in-place bubble sort algorithm on that copy.

Here is the implementation:

```python
def bubble_sort(xs: list[int]) -> list[int]:
    """
    Returns a new list containing the elements of xs sorted in ascending order
    using the bubble sort algorithm.
    """
    # Create a copy to ensure the original list is not mutated
    sorted_list = list(xs)
    n = len(sorted_list)
    
    # Outer loop for the number of passes
    for i in range(n):
        # Flag to optimize: if no swaps occur in a pass, the list is already sorted
        swapped = False
        
        # Inner loop for comparisons
        # The last i elements are already in place, so we ignore them
        for j in range(0, n - i - 1):
            if sorted_list[j] > sorted_list[j + 1]:
                # Swap the elements
                sorted_list[j], sorted_list[j + 1] = sorted_list[j + 1], sorted_list[j]
                swapped = True
        
        # If no two elements were swapped by inner loop, then break
        if not swapped:
            break
            
    return sorted_list

# Example usage:
if __name__ == "__main__":
    original = [64, 34, 25, 12, 22, 11, 90]
    sorted_version = bubble_sort(original)
    
    print(f"Original: {original}")
    print(f"Sorted:   {sorted_version}")
```

### Key Details:
1.  **Immutability**: By calling `sorted_list = list(xs)`, we ensure that the function adheres to the requirement of returning a *new* list, preventing side effects on the input list.
2.  **Complexity**: 
    *   **Time Complexity**: $O(n^2)$ in the worst and average cases.
    *   **Space Complexity**: $O(n)$ to store the new list.
3.
```

## code-037

**prompt:** Write `def quicksort(xs: list[int]) -> list[int]` returning a new sorted list using quicksort.

**causal:**

```
Here is a clean, idiomatic implementation of the Quicksort algorithm in Python. This version uses **list comprehensions** to create a new list, ensuring the original input remains unmodified.

```python
def quicksort(xs: list[int]) -> list[int]:
    # Base case: if the list has 0 or 1 elements, it is already sorted
    if len(xs) <= 1:
        return xs
    
    # Choosing the middle element as the pivot
    pivot = xs[len(xs) // 2]
    
    # Partition the list into three parts:
    # 1. Elements smaller than the pivot
    left = [x for x in xs if x < pivot]
    
    # 2. Elements equal to the pivot (handles duplicates)
    middle = [x for x in xs if x == pivot]
    
    # 3. Elements larger than the pivot
    right = [x for x in xs if x > pivot]
    
    # Recursively sort the left and right, then combine
    return quicksort(left) + middle + quicksort(right)

# Example usage:
if __name__ == "__main__":
    nums = [3, 6, 8, 10, 1, 2, 1]
    sorted_nums = quicksort(nums)
    print(f"Original: {nums}")
    print(f"Sorted:   {sorted_nums}")
```

### How it works:
1.  **Base Case**: If the list is empty or contains only one item, it returns the list immediately.
2.  **Pivot Selection**: We select the middle element as the `pivot`. Using the middle (rather than the first or last) helps avoid $O(n^2)$ worst-case performance on already-sorted lists.
3.  **Partitioning**:
    *   `left`: All elements strictly less than the pivot.
    *   `middle`: All elements equal to the pivot (this ensures the algorithm handles duplicate numbers efficiently).
    *   `right`: All elements strictly greater than the pivot.
4.  **Recursion**: The function calls itself on the `left` and `right` lists and concatenates the results with the `middle`.
```

**gemma4:**

```
Here is a clean, idiomatic implementation of the Quicksort algorithm in Python. This version uses list comprehensions to ensure it returns a **new** list rather than modifying the original one in place.

```python
def quicksort(xs: list[int]) -> list[int]:
    """
    Returns a new list containing the elements of xs in ascending order
    using the Quicksort algorithm.
    """
    # Base case: a list with 0 or 1 elements is already "sorted"
    if len(xs) <= 1:
        return xs
    
    # Choosing the middle element as the pivot to avoid O(n^2) 
    # performance on already sorted lists.
    pivot = xs[len(xs) // 2]
    
    # Partition the list into three parts:
    # 1. Elements strictly less than the pivot
    left = [x for x in xs if x < pivot]
    
    # 2. Elements equal to the pivot (handles duplicate values)
    middle = [x for x in xs if x == pivot]
    
    # 3. Elements strictly greater than the pivot
    right = [x for x in xs if x > pivot]
    
    # Recursively sort the left and right, then combine
    return quicksort(left) + middle + quicksort(right)

# Example usage:
if __name__ == "__main__":
    unsorted = [3, 6, 8, 10, 1, 2, 1]
    sorted_list = quicksort(unsorted)
    print(f"Original: {unsorted}")
    print(f"Sorted:   {sorted_list}")
```

### Key Details of this Implementation:

1.  **Immutability**: By using list comprehensions and returning `quicksort(left) + middle + quicksort(right)`, the original input list `xs` remains unchanged.
2.  **Pivot Selection**: I used `xs[len(xs) // 2]` (the middle element) instead of `xs[0]`. This is a simple optimization that prevents the algorithm from degrading to $O(n^2)$ time complexity when the input list is already sorted.
3.  **Handling Duplicates**: By creating a `middle` list containing all elements
```

## code-038

**prompt:** Implement `def hamming(a: str, b: str) -> int` returning the Hamming distance between two equal-length strings.

**causal:**

```
To calculate the Hamming distance between two strings of equal length, you need to count the number of positions at which the corresponding characters are different.

Here is the implementation using a generator expression within the `sum()` function, which is the most Pythonic and efficient approach:

```python
def hamming(a: str, b: str) -> int:
    """
    Returns the Hamming distance between two equal-length strings.
    
    Args:
        a: The first string.
        b: The second string.
        
    Returns:
        The number of positions at which the characters differ.
        
    Raises:
        ValueError: If the strings are not of equal length.
    """
    if len(a) != len(b):
        raise ValueError("Strings must be of equal length")
    
    # zip pairs characters from both strings: (a[0], b[0]), (a[1], b[1]), etc.
    # We count 1 for every pair where the characters are not equal.
    return sum(char_a != char_b for char_a, char_b in zip(a, b))

# Examples
print(hamming("karolin", "kathrin"))  # Output: 3
print(hamming("1011101", "1001001"))  # Output: 2
print(hamming("abc", "abc"))          # Output: 0
```

### How it works:
1.  **Validation**: The Hamming distance is only defined for strings of equal length, so we first check `len(a) != len(b)` and raise a `ValueError` if they differ.
2.  **`zip(a, b)`**: This function takes two iterables and aggregates them into tuples. For example, `zip("abc", "abd")` produces `('a', 'a'), ('b', 'b'), ('c', 'd')`.
3.  **Generator Expression**: `char_a != char_b for char_a, char_b in zip(a, b)` creates a sequence of Booleans (`False`, `False`, `True`).
4.  **`sum(...)`**: In Python, `True` is treated as `1` and `False` as `0`. Summing the Booleans effectively counts how many times the characters
```

**gemma4:**

```
To calculate the Hamming distance, you need to count the number of positions at which the corresponding characters are different.

Here is the implementation:

```python
def hamming(a: str, b: str) -> int:
    """
    Returns the Hamming distance between two equal-length strings.
    
    Args:
        a: The first string.
        b: The second string.
        
    Returns:
        The number of positions at which the characters are different.
        
    Raises:
        ValueError: If the strings are not of equal length.
    """
    if len(a) != len(b):
        raise ValueError("Strings must be of equal length")

    # zip pairs characters from both strings: (a[0], b[0]), (a[1], b[1]), etc.
    # We count 1 for every pair where the characters are not equal.
    return sum(c1 != c2 for c1, c2 in zip(a, b))

# --- Test Cases ---
if __name__ == "__main__":
    # Standard case
    print(hamming("karolin", "kerstin"))  # Output: 3
    
    # Identical strings
    print(hamming("abc", "abc"))          # Output: 0
    
    # Completely different strings
    print(hamming("abc", "xyz"))          # Output: 3
    
    # Error case
    try:
        hamming("abc", "abcd")
    except ValueError as e:
        print(f"Caught expected error: {e}") # Output: Strings must be of equal length
```

### Explanation:
1.  **Validation**: The Hamming distance is only defined for sequences of equal length. We check `len(a) != len(b)` and raise a `ValueError` if they differ.
2.  **`zip(a, b)`**: This function iterates through both strings simultaneously, yielding tuples of characters at the same index.
3.  **Generator Expression**: `(c1 != c2 for c1, c2 in zip(a, b))` creates a sequence of Booleans (`True` if characters differ, `False` if they are the same).
4.  **`sum(...)`**: In Python, `True` is treated as `1` and `False` as `
```

## code-039

**prompt:** Write `def valid_parentheses(s: str) -> bool` checking that (), [], and {} are balanced and correctly nested.

**causal:**

```
To solve this problem, we use a **stack** data structure. The stack allows us to keep track of the most recently opened brackets and ensure they are closed in the correct order (Last-In, First-Out).

### The Logic
1.  **Iterate** through each character in the string.
2.  If the character is an **opening bracket** (`(`, `[`, `{`), push it onto the stack.
3.  If the character is a **closing bracket** (`)`, `]`, `}`):
    *   Check if the stack is empty. If it is, there is no matching opening bracket, so return `False`.
    *   Pop the top element from the stack. If the popped element does not match the current closing bracket, return `False`.
4.  After the loop, if the stack is **empty**, all brackets were matched correctly. If not, some brackets were left open, so return `False`.

### The Implementation

```python
def valid_parentheses(s: str) -> bool:
    # Map closing brackets to their corresponding opening brackets
    bracket_map = {")": "(", "]": "[", "}": "{"}
    stack = []

    for char in s:
        # If the character is a closing bracket
        if char in bracket_map:
            # Pop the top element if stack isn't empty, else use a dummy value
            top_element = stack.pop() if stack else '#'
            
            # If the popped element doesn't match the required opening bracket
            if bracket_map[char] != top_element:
                return False
        else:
            # If it's an opening bracket, push it onto the stack
            stack.append(char)

    # If the stack is empty, all brackets were matched
    return not stack

# --- Test Cases ---
print(valid_parentheses("()"))       # True
print(valid_parentheses("()[]{}"))   # True
print(valid_parentheses("(]"))       # False
print(valid_parentheses("([)]"))     # False
print(valid_parentheses("{[]}"))     # True
```

### Complexity Analysis
*   **Time Complexity:** $O(n)$, where $n$ is the length of the string. We traverse the string exactly once.
*
```

**gemma4:**

```
To solve this problem, the most efficient approach is to use a **stack** data structure. 

As we iterate through the string, we push opening brackets onto the stack. When we encounter a closing bracket, we check if it matches the most recent opening bracket (the top of the stack). If it matches, we pop it; if it doesn't, or if the stack is empty, the string is invalid.

Here is the implementation:

```python
def valid_parentheses(s: str) -> bool:
    # Map closing brackets to their corresponding opening brackets
    bracket_map = {
        ')': '(',
        ']': '[',
        '}': '{'
    }
    stack = []

    for char in s:
        # If the character is a closing bracket
        if char in bracket_map:
            # Pop the top element if stack isn't empty, otherwise use a dummy value
            top_element = stack.pop() if stack else '#'
            
            # If the popped element doesn't match the required opening bracket
            if bracket_map[char] != top_element:
                return False
        else:
            # If it's an opening bracket, push it onto the stack
            stack.append(char)

    # If the stack is empty, all brackets were matched correctly
    return not stack

# --- Test Cases ---
if __name__ == "__main__":
    print(valid_parentheses("()"))        # True
    print(valid_parentheses("()[]{}"))    # True
    print(valid_parentheses("(]"))        # False
    print(valid_parentheses("([)]"))      # False
    print(valid_parentheses("{[]}"))      # True
    print(valid_parentheses("["))         # False
    print(valid_parentheses("]"))         # False
```

### Complexity Analysis:
1.  **Time Complexity: $O(n)$**
    We traverse the string exactly once, and each stack operation (`push` and `pop`) takes $O(1)$ time.
2.  **Space Complexity: $O(n)$**
    In the worst case (e.g., a string consisting only of opening brackets like `((((((`), we store all $n$ characters in the stack.

### How it works
```

## code-040

**prompt:** Implement `def two_sum(nums: list[int], target: int) -> tuple[int, int] | None` returning the indices of two numbers that sum to target.

**causal:**

```
To solve this problem efficiently, we use a **hash map** (dictionary in Python). This allows us to find the complement of the current number in $O(1)$ average time, resulting in an overall time complexity of $O(n)$.

```python
def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """
    Finds the indices of two numbers in the list that sum up to the target.
    
    Args:
        nums: A list of integers.
        target: The integer sum to search for.
        
    Returns:
        A tuple containing the two indices if found, otherwise None.
    """
    # Map to store the value as the key and its index as the value
    prev_map = {}  # val : index

    for i, n in enumerate(nums):
        diff = target - n
        if diff in prev_map:
            return (prev_map[diff], i)
        prev_map[n] = i
        
    return None

# --- Examples ---
if __name__ == "__main__":
    print(two_sum([2, 7, 11, 15], 9))   # Output: (0, 1)
    print(two_sum([3, 2, 4], 6))        # Output: (1, 2)
    print(two_sum([3, 3], 6))           # Output: (0, 1)
    print(two_sum([1, 2, 3], 7))        # Output: None
```

### How it works:
1. **Initialization**: We create an empty dictionary `prev_map` to keep track of the numbers we have seen so far and their corresponding indices.
2. **Iteration**: We loop through the list using `enumerate` to get both the index (`i`) and the value (`n`).
3. **Calculation**: For every number, we calculate the `diff` (the value needed to reach the `target`).
4. **Lookup**: 
   - If the `diff` is already in our dictionary, it means we found the pair. We return the index of the `diff` and the current index.
   - If it is not in the dictionary, we add the
```

**gemma4:**

```
To solve this problem efficiently, the best approach is to use a **hash map** (dictionary in Python). This allows us to find the "complement" of the current number in constant time $O(1)$ on average.

Here is the implementation:

```python
def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """
    Returns the indices of two numbers in 'nums' that sum up to 'target'.
    Returns None if no such pair exists.
    """
    # Map to store: {value: index}
    prev_map = {}

    for i, n in enumerate(nums):
        diff = target - n
        
        # If the complement exists in our map, we found the pair
        if diff in prev_map:
            return (prev_map[diff], i)
        
        # Otherwise, store the current number and its index
        prev_map[n] = i

    return None

# --- Test Cases ---
if __name__ == "__main__":
    # Case 1: Standard case
    print(two_sum([2, 7, 11, 15], 9))   # Expected: (0, 1)

    # Case 2: Numbers are not adjacent
    print(two_sum([3, 2, 4], 6))        # Expected: (1, 2)

    # Case 3: Using the same value twice (different indices)
    print(two_sum([3, 3], 6))           # Expected: (0, 1)

    # Case 4: No solution exists
    print(two_sum([1, 2, 3], 7))        # Expected: None
```

### Complexity Analysis

1.  **Time Complexity: $O(n)$**
    *   We iterate through the list exactly once.
    *   Each lookup and insertion in the dictionary (hash map) takes $O(1)$ on average.
    *   Therefore, the total time complexity is linear relative to the size of the input list.

2.  **Space Complexity: $O(n)$**
    *   In the worst-case scenario (e.g., the pair is at the very end or doesn't exist),
```

## code-041

**prompt:** Write `def group_by_parity(xs: list[int]) -> dict[str, list[int]]` returning a dict with keys 'even' and 'odd'.

**causal:**

```
Here is the implementation of the `group_by_parity` function:

```python
def group_by_parity(xs: list[int]) -> dict[str, list[int]]:
    """
    Groups a list of integers into a dictionary with keys 'even' and 'odd'.
    """
    result = {'even': [], 'odd': []}
    for num in xs:
        if num % 2 == 0:
            result['even'].append(num)
        else:
            result['odd'].append(num)
    return result

# Example usage:
# print(group_by_parity([1, 2, 3, 4, 5, 6]))
# Output: {'even': [2, 4, 6], 'odd': [1, 3, 5]}
```

### Explanation:
1. **Initialization**: We initialize a dictionary with the keys `'even'` and `'odd'`, each pointing to an empty list. This ensures that even if the input list is empty or contains only one type of parity, both keys will still exist in the output.
2. **Iteration**: We loop through every integer `num` in the input list `xs`.
3. **Modulo Operator**: We use `num % 2 == 0` to check if the number is divisible by 2.
4. **Appending**: Based on the result of the check, we append the number to the corresponding list in the dictionary.
```

**gemma4:**

```
Here is the implementation of the function:

```python
def group_by_parity(xs: list[int]) -> dict[str, list[int]]:
    """
    Groups a list of integers into a dictionary with keys 'even' and 'odd'.
    """
    result = {'even': [], 'odd': []}
    for x in xs:
        if x % 2 == 0:
            result['even'].append(x)
        else:
            result['odd'].append(x)
    return result

# Examples
if __name__ == "__main__":
    print(group_by_parity([1, 2, 3, 4, 5, 6])) 
    # Output: {'even': [2, 4, 6], 'odd': [1, 3, 5]}

    print(group_by_parity([0, -2, -3, 7]))     
    # Output: {'even': [0, -2], 'odd': [-3, 7]}

    print(group_by_parity([]))                 
    # Output: {'even': [], 'odd': []}
```

### Explanation:
1.  **Initialization**: We initialize a dictionary with the keys `'even'` and `'odd'`, each pointing to an empty list. This ensures that even if the input list is empty or contains only one type of parity, both keys are present in the output.
2.  **Iteration**: We loop through every integer `x` in the input list `xs`.
3.  **Modulo Operator**: We use `x % 2 == 0` to check if the number is divisible by 2.
    *   If `True`, the number is **even** and appended to the `'even'` list.
    *   If `False`, the number is **odd** and appended to the `'odd'` list.
4.  **Complexity**: 
    *   **Time Complexity**: $O(n)$, where $n$ is the length of the list, as we visit each element exactly once.
    *   **Space Complexity**: $O(n)$ to store the resulting lists.
```

## code-042

**prompt:** Implement `def longest_common_prefix(strs: list[str]) -> str` returning the longest common leading substring.

**causal:**

```
To find the longest common prefix among a list of strings, the most efficient approach is to compare the strings character by character or to leverage the fact that the common prefix must be shared by the lexicographically smallest and largest strings in the list.

Here are two ways to implement this:

### Option 1: The Lexicographical Approach (Most Efficient)
By sorting the list, we only need to compare the first and the last strings. Any prefix common to both the alphabetically "smallest" and "largest" strings must be common to all strings in between.

```python
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""
    
    # Sort the strings lexicographically
    strs.sort()
    
    # Compare the first and the last string
    first = strs[0]
    last = strs[-1]
    i = 0
    
    # Find the point where characters stop matching
    while i < len(first) and i < len(last) and first[i] == last[i]:
        i += 1
        
    return first[:i]
```

### Option 2: The Horizontal Scanning Approach (Standard)
This approach assumes the first string is the prefix and iteratively shortens it as it compares it against the other strings in the list.

```python
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""
    
    # Start by assuming the first string is the prefix
    prefix = strs[0]
    
    for i in range(1, len(strs)):
        # Shorten the prefix until it matches the start of strs[i]
        while not strs[i].startswith(prefix):
            prefix = prefix[:-1]
            # If prefix becomes empty, there is no common prefix
            if not prefix:
                return ""
                
    return prefix
```

### Complexity Analysis
*   **Time Complexity**: 
    *   **Option 1**: $O(N \cdot L \log N)$, where $N$ is the number of strings and $L$ is the average length (due to sorting).
    *   **Option 2**: $O(S)$, where $S$ is the sum of all characters in all strings.
*   **Space Complexity
```

**gemma4:**

```
Here are two ways to implement this. The first is the most efficient "Pythonic" way, and the second is the classic algorithmic approach.

### Option 1: The Pythonic Approach (Most Efficient)
This method uses Python's built-in `min()` and `max()` functions on strings. In Python, comparing strings lexicographically means `min()` returns the string that would appear first in a dictionary, and `max()` returns the last. The common prefix of the entire list must be the common prefix between these two extreme strings.

```python
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""

    # The common prefix of the whole list must be 
    # a prefix of the lexicographically smallest and largest strings.
    s1 = min(strs)
    s2 = max(strs)

    for i, char in enumerate(s1):
        if i >= len(s2) or char != s2[i]:
            return s1[:i]
            
    return s1
```

### Option 2: The Vertical Scanning Approach (Classic)
This method compares characters index by index across all strings. It is more intuitive if you are coming from a C++ or Java background.

```python
def longest_common_prefix(strs: list[str]) -> str:
    if not strs:
        return ""

    # Take the first string as a reference
    first = strs[0]
    
    for i in range(len(first)):
        char = first[i]
        
        # Check this character against the same position in all other strings
        for j in range(1, len(strs)):
            # If we reached the end of one string OR characters don't match
            if i == len(strs[j]) or strs[j][i] != char:
                return first[:i]
                
    return first
```

### Complexity Analysis

| Approach | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Option 1** | $O(N \cdot K)$ | $O(1)$ | $N$ is number of strings, $K$ is avg length. `min/max` scans the list once. |
| **Option 2**
```

## code-043

**prompt:** Write `def rotate(xs: list, k: int) -> list` that rotates a list right by k positions.

**causal:**

```
To rotate a list right by $k$ positions, we can use Python's slicing syntax. 

The logic is to handle cases where $k$ is larger than the list length using the modulo operator (`%`), and then concatenate the last $k$ elements with everything before them.

```python
def rotate(xs: list, k: int) -> list:
    if not xs:
        return xs
    
    # Handle cases where k is larger than the list length
    # and handle negative k (which would rotate left)
    n = len(xs)
    k = k % n
    
    # Slice the list: 
    # xs[-k:] gets the last k elements
    # xs[:-k] gets everything except the last k elements
    return xs[-k:] + xs[:-k]

# Examples:
print(rotate([1, 2, 3, 4, 5], 2))  # Output: [4, 5, 1, 2, 3]
print(rotate([1, 2, 3], 4))        # Output: [3, 1, 2] (same as k=1)
print(rotate([1, 2, 3], -1))       # Output: [2, 3, 1] (left rotation)
```

### How it works:
1. **`n = len(xs)`**: We find the length of the list.
2. **`k = k % n`**: This ensures that if $k$ is greater than the length of the list, we only perform the necessary number of rotations (e.g., rotating a list of length 5 by 7 positions is the same as rotating it by 2). It also correctly handles negative integers by converting them into their positive equivalent rotation.
3. **`xs[-k:]`**: This slice takes the elements from the $k$-th position from the end to the very end of the list.
4. **`xs[:-k]`**: This slice takes all elements from the start up to (but not including) the $k$-th position from the end.
5. **`+`**: We concatenate these two slices to form the new rotated list.
```

**gemma4:**

```
To rotate a list to the right by $k$ positions, the elements at the end of the list move to the front. 

The most efficient way to handle this is to use the modulo operator (`k % len(xs)`) to account for cases where $k$ is larger than the list length, and then use Python's list slicing.

```python
def rotate(xs: list, k: int) -> list:
    """
    Rotates a list right by k positions.
    """
    if not xs:
        return xs
    
    # Handle cases where k is greater than the length of the list
    n = len(xs)
    k = k % n
    
    # If k is 0, no rotation is needed
    if k == 0:
        return xs[:]
    
    # Slice the list: 
    # xs[-k:] gets the last k elements
    # xs[:-k] gets everything except the last k elements
    return xs[-k:] + xs[:-k]

# --- Test Cases ---
if __name__ == "__main__":
    print(rotate([1, 2, 3, 4, 5], 2))   # Expected: [4, 5, 1, 2, 3]
    print(rotate([1, 2, 3], 4))         # Expected: [3, 1, 2] (4 % 3 = 1)
    print(rotate([1, 2, 3], 0))         # Expected: [1, 2, 3]
    print(rotate([], 5))                # Expected: []
    print(rotate([1, 2, 3], -1))        # Expected: [2, 3, 1] (Left rotation)
```

### Explanation:
1.  **Edge Case (`if not xs`)**: If the list is empty, we return it immediately to avoid a `ZeroDivisionError` when calculating the modulo.
2.  **Modulo Operator (`k % n`)**: If a list has 5 elements and you rotate it 7 times, it is the same as rotating it 2 times ($7 \pmod 5 = 2$). This also handles negative integers (rotating right by -1 is equivalent to rotating left by 1).
3
```

## code-044

**prompt:** Implement `def is_armstrong(n: int) -> bool` checking whether n equals the sum of its digits each raised to the number of digits.

**causal:**

```
To determine if a number is an Armstrong number (also known as a narcissistic number), we need to:
1. Count the number of digits in $n$.
2. Extract each digit.
3. Raise each digit to the power of the total digit count.
4. Sum these values and compare the result to the original $n$.

Here is the implementation:

```python
def is_armstrong(n: int) -> bool:
    # Negative numbers are typically not considered Armstrong numbers
    if n < 0:
        return False
    
    # Convert number to string to easily iterate over digits and find the length
    s = str(n)
    num_digits = len(s)
    
    # Calculate the sum of each digit raised to the power of num_digits
    total_sum = sum(int(digit) ** num_digits for digit in s)
    
    # Return True if the sum equals the original number
    return total_sum == n

# Test cases
if __name__ == "__main__":
    print(is_armstrong(153))  # True (1^3 + 5^3 + 3^3 = 1 + 125 + 27 = 153)
    print(is_armstrong(9))    # True (9^1 = 9)
    print(is_armstrong(9474)) # True (9^4 + 4^4 + 7^4 + 4^4 = 6561 + 256 + 2401 + 256 = 9474)
    print(is_armstrong(10))   # False (1^2 + 0^2 = 1)
```

### Mathematical Approach (Without String Conversion)
If you prefer to solve this using purely mathematical operations (avoiding string conversion), you can use this version:

```python
def is_armstrong(n: int) -> bool:
    if n < 0: return False
    if n == 0: return True
    
    # Find the number of digits
    num_digits = 0
    temp = n
    while temp > 0:
        temp //= 10
        num_digits += 1
```

**gemma4:**

```
To implement this, we need to:
1. Convert the number to a string (or use math) to count the number of digits.
2. Iterate through each digit.
3. Raise each digit to the power of the total count.
4. Sum these values and compare the result to the original number.

Here is the implementation:

```python
def is_armstrong(n: int) -> bool:
    """
    Checks whether n equals the sum of its digits each raised to 
    the power of the number of digits.
    """
    # Negative numbers are typically not considered Armstrong numbers
    if n < 0:
        return False
    
    # Convert number to string to easily iterate over digits and find length
    s = str(n)
    num_digits = len(s)
    
    # Calculate the sum of each digit raised to the power of num_digits
    total_sum = sum(int(digit) ** num_digits for digit in s)
    
    # Return True if the sum equals the original number
    return total_sum == n

# Test cases
if __name__ == "__main__":
    print(is_armstrong(153))   # True  (1^3 + 5^3 + 3^3 = 1 + 125 + 27 = 153)
    print(is_armstrong(9474))  # True  (9^4 + 4^4 + 7^4 + 4^4 = 6561 + 256 + 2401 + 256 = 9474)
    print(is_armstrong(10))    # False (1^2 + 0^2 = 1)
    print(is_armstrong(9))     # True  (9^1 = 9)
```

### Complexity Analysis:
*   **Time Complexity:** $O(d)$, where $d$ is the number of digits in $n$. We iterate through the digits exactly once.
*   **Space Complexity:** $O(d)$ to store the string representation of the number.

### Mathematical Alternative (Without String Conversion):
If you prefer to avoid string conversion for a purely mathematical approach, you can use this version:

```python
```

## code-045

**prompt:** Write `def collatz_length(n: int) -> int` returning the number of steps to reach 1 in the Collatz sequence.

**causal:**

```
Here is the implementation of the `collatz_length` function. 

This function follows the Collatz conjecture rules: if the number is even, divide it by 2; if it is odd, multiply it by 3 and add 1. The count starts at 0 and increments until the number reaches 1.

```python
def collatz_length(n: int) -> int:
    """
    Returns the number of steps to reach 1 in the Collatz sequence.
    """
    if n < 1:
        raise ValueError("The Collatz sequence is defined for positive integers.")
    
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

# Examples
print(collatz_length(6))   # Output: 8 (6 -> 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1)
print(collatz_length(1))   # Output: 0
print(collatz_length(12))  # Output: 9
```

### Explanation:
1. **Input Validation**: The Collatz conjecture is defined for positive integers ($n > 0$).
2. **The Loop**: We use a `while n != 1` loop because we want to stop as soon as the sequence hits 1.
3. **Even/Odd Logic**:
   - `n % 2 == 0` checks if the number is even. We use floor division `//` to ensure the result remains an integer.
   - If odd, we apply $3n + 1$.
4. **Counter**: The `steps` variable increments by 1 for every transformation performed.
```

**gemma4:**

```
Here is the implementation of the `collatz_length` function. 

I have included a version using a `while` loop, which is the most memory-efficient way to solve this, and a version using memoization, which is significantly faster if you are calling the function many times (e.g., for Project Euler problems).

### Standard Implementation
This version follows the logic directly: if $n$ is even, divide by 2; if $n$ is odd, multiply by 3 and add 1.

```python
def collatz_length(n: int) -> int:
    """
    Returns the number of steps to reach 1 in the Collatz sequence.
    The sequence starts at n and ends at 1.
    """
    if n < 1:
        raise ValueError("n must be a positive integer.")
        
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

# Example usage:
# Sequence for 6: 6 -> 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1 (8 steps)
print(collatz_length(6))  # Output: 8
```

---

### Optimized Implementation (with Memoization)
If you are calculating the lengths for a large range of numbers (e.g., finding the longest sequence between 1 and 1,000,000), you should use a dictionary to store previously calculated lengths to avoid redundant math.

```python
_cache = {1: 0}

def collatz_length_memo(n: int) -> int:
    if n in _cache:
        return _cache[n]
    
    if n % 2 == 0:
        res = 1 + collatz_length_memo(n // 2)
    else:
        res = 1 + collatz_length_memo(3 * n + 1)
    
    _cache[n] = res
    return res

# Example usage:
print(collatz_length_memo(6))  # Output: 8
```
```

## code-046

**prompt:** Implement `def primes_up_to(n: int) -> list[int]` using the Sieve of Eratosthenes.

**causal:**

```
Here is the implementation of the Sieve of Eratosthenes in Python.

```python
def primes_up_to(n: int) -> list[int]:
    """
    Returns a list of all prime numbers up to (and including) n 
    using the Sieve of Eratosthenes algorithm.
    """
    if n < 2:
        return []

    # Initialize a boolean list "prime[0..n]" and set all 
    # entries to True. A value in prime[i] will finally 
    # be False if i is Not a prime, else True.
    primes_mask = [True] * (n + 1)
    primes_mask[0] = primes_mask[1] = False  # 0 and 1 are not prime

    # We only need to iterate up to the square root of n
    for p in range(2, int(n**0.5) + 1):
        # If primes_mask[p] is not changed, then it is a prime
        if primes_mask[p]:
            # Update all multiples of p starting from p*p
            # (smaller multiples will have already been marked)
            for i in range(p * p, n + 1, p):
                primes_mask[i] = False

    # Collect all indices that are still marked as True
    return [num for num, is_prime in enumerate(primes_mask) if is_prime]

# Example usage:
if __name__ == "__main__":
    print(primes_up_to(30))
    # Output: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### How it works:
1.  **Initialization**: We create a list of booleans of size $n+1$, assuming every number is prime initially.
2.  **Base Cases**: We explicitly mark $0$ and $1$ as `False` because they are not prime numbers.
3.  **The Sieve**: We iterate starting from $2$. If a number $p$ is still marked `True`, it is prime. We then mark all multiples of $p$ (starting from $p^2$) as
```

**gemma4:**

```
Here is the implementation of the Sieve of Eratosthenes.

```python
def primes_up_to(n: int) -> list[int]:
    """
    Returns a list of all prime numbers up to (and including) n 
    using the Sieve of Eratosthenes algorithm.
    """
    if n < 2:
        return []

    # Initialize a boolean list "is_prime" where index represents the number.
    # We assume all numbers are prime initially.
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False  # 0 and 1 are not prime numbers

    # Iterate from 2 up to the square root of n.
    # If a number is prime, its multiples are composite.
    for p in range(2, int(n**0.5) + 1):
        if is_prime[p]:
            # Mark multiples of p starting from p*p as False.
            # We start at p*p because smaller multiples (e.g., 2p, 3p) 
            # would have already been marked by smaller primes.
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False

    # Collect all indices that remained True.
    return [num for num, prime in enumerate(is_prime) if prime]

# Example usage:
if __name__ == "__main__":
    print(primes_up_to(30))
    # Output: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### Complexity Analysis:
1.  **Time Complexity: $O(n \log \log n)$**
    The Sieve of Eratosthenes is highly efficient. The inner loop runs fewer times as $p$ increases, resulting in this near-linear complexity.
2.  **Space Complexity: $O(n)$**
    We require a boolean array of size $n+1$ to keep track of the primality of each number.

### Key Optimizations used:
*   **Square Root Limit:** The outer loop only needs to
```

## code-047

**prompt:** Write `def diagonal_sum(matrix: list[list[int]]) -> int` returning the sum of both diagonals of a square matrix (count the center once).

**causal:**

```
To solve this, we iterate through the matrix once. For each row $i$, the primary diagonal element is at index `[i][i]` and the secondary diagonal element is at index `[i][n - 1 - i]`. If the indices are the same (which happens at the center of an odd-sized matrix), we only add the value once.

```python
def diagonal_sum(matrix: list[list[int]]) -> int:
    n = len(matrix)
    total_sum = 0
    
    for i in range(n):
        # Add the primary diagonal element
        total_sum += matrix[i][i]
        
        # Add the secondary diagonal element
        # only if it's not the same as the primary diagonal element
        secondary_index = n - 1 - i
        if secondary_index != i:
            total_sum += matrix[i][secondary_index]
            
    return total_sum

# Examples:
# [[1, 2, 3], [4, 5, 6], [7, 8, 9]] -> 1+5+9 + 3+7 = 25
# [[1, 2], [3, 4]] -> 1+4 + 2+3 = 10
```

### Complexity Analysis:
*   **Time Complexity:** $O(n)$, where $n$ is the number of rows (or columns) in the square matrix, as we traverse the matrix exactly once.
*   **Space Complexity:** $O(1)$, as we only use a single integer variable to store the running sum.
```

**gemma4:**

```
To solve this, we iterate through the matrix once. For a square matrix of size $n \times n$, the primary diagonal elements are at indices `[i][i]` and the secondary diagonal elements are at `[i][n - 1 - i]`. 

If the matrix has an odd dimension, the center element will be counted twice if we simply add both diagonals, so we must subtract it once.

```python
def diagonal_sum(matrix: list[list[int]]) -> int:
    n = len(matrix)
    total_sum = 0
    
    for i in range(n):
        # Add element from the primary diagonal
        total_sum += matrix[i][i]
        
        # Add element from the secondary diagonal
        # The column index is (n - 1 - i)
        secondary_col = n - 1 - i
        
        # If the indices are the same, it's the center element of an odd-sized matrix.
        # We only add it if it's not the same as the primary diagonal index.
        if i != secondary_col:
            total_sum += matrix[i][secondary_col]
            
    return total_sum

# Examples
if __name__ == "__main__":
    # 3x3 matrix (Odd size)
    # 1 2 3
    # 4 5 6
    # 7 8 9
    # Diagonals: 1, 5, 9 and 3, 5, 7. Sum: 1+5+9+3+7 = 25
    matrix1 = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    print(f"Sum 1: {diagonal_sum(matrix1)}") # Expected: 25

    # 4x4 matrix (Even size)
    # 1 1 1 1
    # 1 1 1 1
    # 1 1 1 1
    # 1 1 1 1
    # Diagonals: 4 elements + 4 elements = 8
    matrix2 = [[1] * 4 for _
```

## code-048

**prompt:** Implement `def flatten_keys(d: dict, sep: str = '.') -> dict` that flattens a nested dict into dotted keys.

**causal:**

```
To implement this, we can use a recursive approach. We iterate through the dictionary's items: if a value is another dictionary, we recurse; otherwise, we add the key to the result.

Here is the implementation:

```python
def flatten_keys(d: dict, sep: str = '.') -> dict:
    """
    Flattens a nested dictionary into a single-level dictionary 
    with concatenated keys.
    """
    items = {}
    for k, v in d.items():
        if isinstance(v, dict) and v:  # Check if value is a non-empty dict
            # Recursively flatten the sub-dictionary
            flattened_sub = flatten_keys(v, sep=sep)
            for sub_k, sub_v in flattened_sub.items():
                items[f"{k}{sep}{sub_k}"] = sub_v
        else:
            # Base case: value is not a dict or is an empty dict
            items[k] = v
    return items

# --- Example Usage ---
if __name__ == "__main__":
    nested_dict = {
        "user": {
            "id": 1,
            "name": "Alice",
            "address": {
                "city": "New York",
                "zip": "10001"
            }
        },
        "status": "active",
        "tags": []
    }

    flattened = flatten_keys(nested_dict)
    import json
    print(json.dumps(flattened, indent=4))
```

### How it works:
1.  **Iteration**: We loop through every key-value pair in the input dictionary.
2.  **Recursion**: If the value is a dictionary (`isinstance(v, dict)`), we call `flatten_keys` on that sub-dictionary.
3.  **Key Concatenation**: When the recursive call returns, we take its keys and prepend the current parent key followed by the separator (`sep`).
4.  **Base Case**: If the value is not a dictionary (or is an empty dictionary), we simply assign it to the result dictionary with its current key.

### Output of the example:
```json
{
    "user.id": 1,
    "user
```

**gemma4:**

```
To implement this, the most efficient approach is to use a recursive function that traverses the dictionary. We keep track of the "current path" of keys and join them using the provided separator.

Here is the implementation:

```python
def flatten_keys(d: dict, sep: str = '.') -> dict:
    """
    Flattens a nested dictionary into a single-level dictionary 
    with dotted keys.
    
    Args:
        d: The dictionary to flatten.
        sep: The separator to use between nested keys.
        
    Returns:
        A flattened dictionary.
    """
    items = {}

    def _flatten(current_dict: dict, parent_key: str = ""):
        for k, v in current_dict.items():
            # Construct the new key name
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            # If the value is a dict, recurse
            if isinstance(v, dict) and v:
                _flatten(v, new_key)
            else:
                # Otherwise, assign the value to the flattened dict
                items[new_key] = v

    _flatten(d)
    return items

# --- Test Cases ---
if __name__ == "__main__":
    nested = {
        "user": {
            "id": 1,
            "name": "Alice",
            "address": {
                "city": "New York",
                "zip": "10001"
            }
        },
        "active": True,
        "tags": ["admin", "editor"]  # Lists are treated as values, not flattened
    }

    # Test standard dot notation
    flattened = flatten_keys(nested)
    print("Flattened (dot):", flattened)
    # Expected: {'user.id': 1, 'user.name': 'Alice', 'user.address.city': 'New York', ...}

    # Test custom separator
    flattened_underscore = flatten_keys(nested, sep='_')
    print("Flattened (underscore):", flattened_underscore)
    # Expected: {'user_id': 1, 'user_name': 'Alice', ...}

    # Test empty dict
    print
```

## code-049

**prompt:** Write a `memoize` decorator that caches a function's return values by its positional arguments.

**causal:**

```
To create a memoization decorator in Python, we use a dictionary to store the results. The **keys** of the dictionary will be the positional arguments (stored as a `tuple`), and the **values** will be the results of the function calls.

Here is the implementation:

```python
import functools

def memoize(func):
    # The cache is stored in the closure of the decorator
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        # We use the tuple of arguments as the dictionary key
        if args not in cache:
            print(f"Calculating result for {args}...") # Optional: to see when it runs
            cache[args] = func(*args)
        return cache[args]
    
    return wrapper

# --- Example Usage ---

@memoize
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@memoize
def add(a, b):
    return a + b

# Testing the memoization
print(fibonacci(10))  # Calculates all steps
print(fibonacci(10))  # Returns immediately from cache
print(add(5, 5))      # Calculates
print(add(5, 5))      # Returns immediately from cache
```

### Key Features of this Implementation:

1.  **`functools.wraps`**: This is a best practice when writing decorators. It ensures that the decorated function keeps its original metadata (like its name `__name__` and docstring `__doc__`).
2.  **The Cache Dictionary**: We define `cache = {}` inside the `memoize` function but outside the `wrapper`. This creates a **closure**, meaning the cache persists as long as the decorated function exists.
3.  **Tuple Keys**: Since `args` is a tuple (which is immutable), it can be used directly as a dictionary key. 
    *   *Note: This implementation only handles positional arguments. If you pass a list (which is mutable) as an argument, it will raise a `TypeError` because lists cannot be dictionary keys.*

### A Note on Python's Built-in Alternative
If you are using Python 3.9+, you don't need to
```

**gemma4:**

```
To implement a `memoize` decorator that caches results based on positional arguments, the most efficient way is to use a dictionary where the **keys** are a `tuple` of the arguments and the **values** are the function results.

Here is the implementation:

```python
import functools

def memoize(func):
    # The cache dictionary lives in the closure of the decorator
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        # We use the tuple of positional arguments as the dictionary key
        # Tuples are hashable, making them perfect for dictionary keys
        if args in cache:
            print(f"[Cache Hit] Returning cached result for {args}")
            return cache[args]
        
        # If not in cache, call the function and store the result
        print(f"[Cache Miss] Computing result for {args}")
        result = func(*args)
        cache[args] = result
        return result

    return wrapper

# --- Testing the implementation ---

@memoize
def add(a, b):
    return a + b

@memoize
def expensive_calculation(n):
    # Simulating a heavy computation
    return n * n * n

# 1. Test basic addition
print(add(2, 3))   # Miss: computes 5
print(add(2, 3))   # Hit: returns 5
print(add(5, 5))   # Miss: computes 10

# 2. Test expensive calculation
print(expensive_calculation(10)) # Miss
print(expensive_calculation(10)) # Hit
```

### Key Technical Details:

1.  **`functools.wraps(func)`**: This is a best practice when writing decorators. It ensures that the metadata of the original function (like its name `__name__` and docstring `__doc__`) is preserved in the wrapped version.
2.  **The Cache Key (`args`)**: In Python, `*args` is captured as a `tuple`. Since tuples are **immutable** and **hashable**, they can be used directly as keys in a dictionary.
3.  **Complexity**: 
    *   **Time Complexity**: $O(1)$ on average for lookups (dictionary access).
    *   **
```

## code-050

**prompt:** Implement `def top_k_frequent(words: list[str], k: int) -> list[str]` returning the k most frequent words, ties broken alphabetically.

**causal:**

```
To solve this problem efficiently, we can use a **Hash Map** (dictionary) to count the frequencies of each word and a **Min-Heap** to keep track of the top $k$ elements.

### The Logic
1.  **Count Frequencies:** Use a dictionary to store how many times each word appears.
2.  **Heap Strategy:** We use a Min-Heap of size $k$. 
    *   In a Min-Heap, the "smallest" element is at the top.
    *   To get the *most frequent* words, we want to pop the least frequent.
    *   **Tie-breaking:** Since we want the top $k$ to be sorted alphabetically in case of ties, but a Min-Heap pops the "smallest" value, we use a custom wrapper or a specific tuple structure: `(frequency, negative_word)`. By negating the word (or using a custom comparison), we ensure that for the same frequency, the alphabetically "larger" word is treated as "smaller" by the heap, allowing it to be popped first.
3.  **Complexity:** 
    *   **Time:** $O(N \log k)$, where $N$ is the number of words.
    *   **Space:** $O(N)$ to store the frequency map.

### Implementation

```python
import heapq
from collections import Counter

class WordFreq:
    def __init__(self, word, freq):
        self.word = word
        self.freq = freq

    def __lt__(self, other):
        # If frequencies are equal, the alphabetically LARGER word 
        # is considered "smaller" so it stays at the top of the min-heap 
        # and gets removed first.
        if self.freq == other.freq:
            return self.word > other.word
        return self.freq < other.freq

def top_k_frequent(words: list[str], k: int) -> list[str]:
    # 1. Count the frequency of each word
    counts = Counter(words)
    
    # 2. Use a min-heap to keep the top k elements
    heap = []
    
    for word, freq in counts.items():
        heapq.heappush(heap, WordFreq(word, freq))
        if len(
```

**gemma4:**

```
To solve this problem efficiently, we can use a hash map (dictionary) to count the frequencies and then sort the results. 

The key to handling the tie-breaking rule ("most frequent first, then alphabetically") is to use a custom sorting key. In Python, when sorting a list of tuples, the sort is stable and lexicographical. We can negate the frequency to sort it in descending order while keeping the word in its natural ascending alphabetical order.

Here is the implementation:

```python
from collections import Counter

def top_k_frequent(words: list[str], k: int) -> list[str]:
    """
    Returns the k most frequent words. 
    Ties are broken by alphabetical order.
    """
    # Step 1: Count the frequency of each word
    # counts will be something like {'i': 2, 'love': 2, 'leetcode': 1}
    counts = Counter(words)
    
    # Step 2: Get the unique words
    unique_words = list(counts.keys())
    
    # Step 3: Sort the words
    # We want to sort by:
    # 1. Frequency (descending): achieved by -counts[word]
    # 2. Alphabetical (ascending): achieved by word
    unique_words.sort(key=lambda word: (-counts[word], word))
    
    # Step 4: Return the top k elements
    return unique_words[:k]

# --- Test Cases ---
if __name__ == "__main__":
    # Case 1: Standard case with ties
    # 'i' and 'love' both appear twice. 'i' comes before 'love' alphabetically.
    test1 = ["i", "love", "leetcode", "i", "love", "coding"]
    print(f"Test 1: {top_k_frequent(test1, 2)}") 
    # Expected: ['i', 'love']

    # Case 2: Single word
    test2 = ["the", "the", "the", "the"]
    print(f"Test 2: {top_k_frequent(test2, 1)}") 
    # Expected: ['the']

    # Case 3: All words have same frequency
    test3 = ["a",
```

