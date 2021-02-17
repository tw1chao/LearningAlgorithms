"""Chapter 1 Challenge Questions."""

import random
import timeit

from algs.table import DataTable
from algs.counting import RecordedItem

def partition(A, lo, hi, idx):
    """
    Partition using A[idx] as value. Note lo and hi are INCLUSIVE on both
    ends and idx must be valid index.
    """
    A[idx],A[lo] = A[lo],A[idx]    # swap into position
    i = lo
    j = hi + 1

    while True:
        while True:
            i += 1
            if A[lo] < A[i]: break
            if i == hi: break

        while True:
            j -= 1
            if A[j] < A[lo]: break
            if j == lo: break

        if i >= j: break

        A[i],A[j] = A[j],A[i]

    A[lo],A[j] = A[j],A[lo]
    return j

def linear_median(A):
    """
    Efficient implementation that returns median value in arbitrary list,
    assuming A has an odd number of values. Note this algorithm will
    rearrange values in A.
    """
    lo = 0
    hi = len(A) - 1
    mid = hi // 2
    while lo <= hi:
        #idx = random.randrange(hi-lo+1)     # select valid index randomly
        j = partition(A, lo, hi, lo)  #  +idx)

        if j == mid:
            return A[j]
        if j < mid:
            lo = j+1
        else:
            hi = j-1

def counting_sort(A, M):
    """
    Update A in place to be sorted in ascending order if all elements
    are guaranteed to be in the range 0 to and not including M.
    """
    counts = [0] * M
    for val in A:
        counts[val] += 1

    pos = 0
    val = 0
    while pos < len(A):
        for idx in range(counts[val]):
            A[pos+idx] = val
        pos += counts[val]
        val += 1

def counting_sort_improved(A,M):
    """
    Update A in place to be sorted in ascending order if all elements
    are guaranteed to be in the range 0 to and not including M.
    """
    counts = [0] * M
    for val in A:
        counts[val] += 1

    pos = 0
    val = 0
    while pos < len(A):
        if counts[val] > 0:
            A[pos:pos+counts[val]] = [val] * counts[val]
            pos += counts[val]
        val += 1

def run_counting_sort_trials():
    """Generate table for counting sort."""
    tbl = DataTable([8,15,15],
                    ['N', 'counting_sort', 'counting_sort_improved'])

    M = 20 # arbitrary value, and results are dependent on this value.
    trials = [2**k for k in range(8,21)]
    for n in trials:
        t_cs = min(timeit.repeat(stmt=f'counting_sort(a,{M})\nis_sorted(a)', setup=f'''
import random
from ch01.challenge import counting_sort
from algs.sorting import is_sorted
w = [{M}-1] * {n}
b = [0] * {n} 
a = list(range({M})) * {n}
random.shuffle(a)''', repeat=100, number=1))
        t_csi = min(timeit.repeat(stmt=f'counting_sort_improved(a,{M})\nis_sorted(a)', setup=f'''
import random
from ch01.challenge import counting_sort_improved
from algs.sorting import is_sorted
w = [{M}-1] * {n}
b = [0] * {n} 
a = list(range({M})) * {n}
random.shuffle(a)''', repeat=100, number=1))

        tbl.row([n, t_cs, t_csi])

def run_median_trial():
    """Generate table for Median Trial."""
    tbl = DataTable([10,15,15],['N', 'median_time', 'sort_median'])

    trials = [2**k+1 for k in range(8,20)]
    for n in trials:
        t_med = 1000*min(timeit.repeat(stmt=f'assert(linear_median(a) == {n}//2)', setup=f'''
import random
from ch01.challenge import linear_median
a = list(range({n}))
random.shuffle(a)
''', repeat=10, number=5))/5

        t_sort = 1000*min(timeit.repeat(stmt=f'assert(sorted(a)[{n}//2] == {n}//2)', setup=f'''
import random
from ch01.challenge import linear_median
a = list(range({n}))
random.shuffle(a)
''', repeat=10, number=5))/5

        tbl.row([n, t_med, t_sort])

def run_median_less_than_trial():
    """Use RecordedItem to count # of times Less-than invoked."""
    tbl = DataTable([10,15,15],['N', 'median_time', 'sort_median'])
    tbl.format('median_time', ',d')
    tbl.format('sort_median', ',d')

    trials = [2**k+1 for k in range(8,20)]
    for n in trials:
        A = list([RecordedItem(i) for i in range(n)])
        random.shuffle(A)

        # Generated external sorted to reuse list
        RecordedItem.clear()
        med2 = sorted(A)[n//2]
        sort_lt = RecordedItem.report()[1]

        RecordedItem.clear()
        med1 = linear_median(A)
        lin_lt = RecordedItem.report()[1]

        assert med1 == med2

        tbl.row([n, lin_lt, sort_lt])

def is_palindrome1(s):
    """Create slice with negative step and confirm equality with s."""
    return s[::-1] == s

def is_palindrome2(s):
    """Strip outermost characters if same, return false when mismatch."""
    while len(s) > 1:
        if s[0] != s[-1]:     # if mismatch, return False
            return False
        s = s[1:-1]           # strip characters on either end; repeat

    return True               # must have been a Palindrome

def is_palindrome_letters_only(s):
    """
    Confirm Palindrome, even when string contains non-alphabet letters
    and ignore capitalization.
    """
    i = 0
    j = hi = len(s) - 1
    while i < j:
        # This type of logic appears in partition.
        # Find alpha characters and compare
        while not s[i].isalpha():
            i += 1
            if i == hi: break
        while not s[j].isalpha():
            j -= 1
            if j == 0: break

        # safe way to compare characters while ignoring their case
        if s[i].casefold() != s[j].casefold(): return False
        i += 1
        j -= 1

    return True

#######################################################################
if __name__ == '__main__':
    print('is Palindrome should be True: ',
          is_palindrome_letters_only('A man, a plan, a canal... Panama!'))

    print('Median Counting\n')
    run_median_less_than_trial()

    print('Median Questions\n')
    run_median_trial()

    print('Challenge Questions\n')
    run_counting_sort_trials()