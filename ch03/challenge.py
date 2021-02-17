"""Challenge questions for Chapter 03."""
class ValueBadHash:
    """Class with horrendous hash() method to ensure clashes."""
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return f"ValueBadHash({self.v})"

    def __hash__(self):
        """only four different values."""
        return hash(self.v) % 4

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.v == other.v)

def bad_timing(words):
    """Statistics on hashtables."""
    from ch03.hashtable_linked import Hashtable, stats_linked_lists

    size = 50000
    good_ht = Hashtable(size)
    bad_ht = Hashtable(size)

    for w in words:
        good_ht.put(w, True)
        bad_ht.put(ValueBadHash(w), True)

    print(stats_linked_lists(words, good_ht))
    print(stats_linked_lists(words, bad_ht))

def prime_number_difference(words):
    """Identify sensitivity of M to being prime or not."""

    from ch03.hashtable_linked import Hashtable as Linked_Hashtable, stats_linked_lists
    from ch03.hashtable_open import Hashtable as Open_Hashtable, stats_open_addressing
    from ch03.base26 import base26
    from algs.table import DataTable

    # these are prime numbers between 428880 and 428980
    lo = 428880
    primes = [428899, 428951, 428957, 428977]
    hi = 428980

    keys = [base26(w) for w in words]
    tbl = DataTable([12,6,8,8,8,8], ['M', 'Prime', 'Avg. LL', 'Max LL', 'Avg. OA', 'Max OA'],
                    decimals=2)
    tbl.format('Prime', 's')
    tbl.format('Max LL', 'd')
    tbl.format('Max OA', 'd')
    worst = 0
    worst_m = 0
    for m in range(lo, hi+1):
        is_p = 'Prime' if m in primes else ''
        ht_linked = Linked_Hashtable(m)
        ht_open = Open_Hashtable(m)

        (avg_length_linked, max_length_linked) = stats_linked_lists(keys, ht_linked, False)
        if max_length_linked > worst:
            worst_m = m
            worst = max_length_linked
        (avg_length_open, max_length_open) = stats_open_addressing(keys, ht_open, False)
        tbl.row([m, is_p, avg_length_linked, max_length_linked, avg_length_open, max_length_open])

    # Now try to find any more that exceed this maximum amount
    print('Worst was {} for M={}'.format(worst, worst_m))
    for m in range(worst_m, worst_m + 10000, 13):
        ht_linked = Linked_Hashtable(m)

        (avg_length_linked, max_length_linked) = stats_linked_lists(keys, ht_linked, False)
        if max_length_linked > worst:
            worst_m = m
            worst = max_length_linked
            print('Worst of {} for M={}'.format(worst, worst_m))
    print('Done')

def measure_performance_resize():
    """Generate table of statistics for table resizing."""
    from ch03.hashtable_linked import DynamicHashtable
    from time import time_ns

    print('Dynamic Resizing Hashtable')
    ht = DynamicHashtable(1023)
    idx = 1
    last = None
    average = 0
    words = english_words()
    for w in words:
        before = time_ns()
        old_size = len(ht.table)
        ht.put(w,w)
        new_size = len(ht.table)
        after = time_ns()
        average += (after-before)
        if last:
            if after - before > last:
                last = after-before
                print(idx,w,last,"old-size:",old_size,"new-size:",new_size)
        else:
            last = after-before
        idx += 1

    average /= len(words)
    print('Average was ', average)
    ht = None

    print('Incremental Resizing Hashtable')
    ht = DynamicHashtableIncrementalResizing(1023,10)
    idx = 1
    last = None
    average = 0
    words = english_words()
    for w in words:
        before = time_ns()
        old_size = len(ht.table)
        ht.put(w,w)
        new_size = len(ht.table)
        after = time_ns()
        average += (after-before)
        if last:
            if after - before > last:
                last = after-before
                print (idx,w,last,"old-size:",old_size,"new-size:",new_size)
        else:
            last = after-before
        idx += 1

    average /= len(words)
    print('Average was ', average)
    ht = None

    print('Incremental Resizing dependent on Delta')
    for delta in range(1,50):
        ht = DynamicHashtableIncrementalResizing(1023, delta)
        average = 0
        words = english_words()
        for w in words:
            before = time_ns()
            ht.put(w,w)
            after = time_ns()
            average += (after-before)

        average /= len(words)
        print (delta,'Average is', average)

class DynamicHashtableIncrementalResizing:
    """
    Hashtable that supports incremental resizing.

    Performance is still limiting because of (a) costs when allocating
    very large array; and (b) when rehashing existing values, you will
    eventually have to search through very large array for next
    non-empty bucket.
    """
    def __init__(self, M=10, delta=1):
        self.table = [None] * M
        self.old_table = None
        if M < 1:
            raise ValueError('Hashtable storage must be at least 1.')
        if delta < 1:
            raise ValueError('delta must be at least 1 since growth factor is 2*M+1')
        self.M = M
        self.N = 0
        self.delta = delta
        self.last_idx = 0
        self.old_M = 0

        self.load_factor = 0.75

        # Ensure resize event happens NO LATER than M-1, to align
        # with open addressing
        self.threshold = min(M * self.load_factor, M-1)

    def get(self, k):
        """
        Retrieve value associated with key, k. Must check old table
        if not present in the new table.
        """
        h = hash(k)
        hc = h % self.M       # First place it could be
        entry = self.table[hc]
        while entry:
            if entry.key == k:
                return entry.value
            entry = entry.next

        # if old table, might be there
        if self.old_table:
            hc_old = h % self.old_M
            entry = self.old_table[hc_old]
            while entry:
                if entry.key == k:
                    return entry.value
                entry = entry.next

        return None                 # Couldn't find

    def put(self, k, v):
        """Associate value, v, with the key, k."""
        h = hash(k)
        hc = h % self.M       # First place it could be
        entry = self.table[hc]
        while entry:
            if entry.key == k:      # Overwrite if already here
                entry.value = v
                return
            entry = entry.next

        if self.old_table:
            hc_old = h % self.old_M
            entry = self.old_table[hc_old]
            while entry:
                if entry.key == k:  # Overwrite if already here
                    entry.value = v
                    return
                entry = entry.next

        # insert, and then trigger resize if hit threshold.
        from ch03.entry import LinkedEntry
        self.table[hc] = LinkedEntry(k, v, self.table[hc])
        self.N += 1

        if self.N >= self.threshold:
            self.resize(2*self.M + 1)
        else:
            # after every put() move over delta values as well.
            if self.old_table:
                self.move_r()

    def move_r(self):
        """
        Incrementally move self.delta entries from old to new table. Should the old
        table become empty of entries, set self.old_table to None.
        """
        num_to_move = self.delta
        while num_to_move > 0 and self.last_idx < self.old_M:
            moving_entry = self.old_table[self.last_idx]
            if moving_entry is None:
                self.last_idx += 1
            else:
                while moving_entry and num_to_move > 0:
                    idx = hash(moving_entry.key) % self.M
                    self.old_table[self.last_idx] = moving_entry.next
                    moving_entry.next = self.table[idx]
                    self.table[idx] = moving_entry

                    moving_entry = self.old_table[self.last_idx]
                    num_to_move -= 1

        if self.last_idx == self.old_M:
            self.old_table = None

    def resize(self, new_size):
        """Resize table to prepare for new entries, but none are moved."""
        # prepare for incremental resizing by recording old_M
        # and recording where we will be sweeping entries from.
        self.last_idx = 0
        self.old_M = self.M
        self.M = new_size

        self.old_table = self.table
        self.table = [None] * self.M

        self.threshold = self.load_factor * self.M

    def remove(self, k):
        """Remove (k,v) entry associated with k."""
        hc = hash(k) % self.M       # First place it could be
        entry = self.table[hc]
        prev = None
        while entry:
            if entry.key == k:
                if prev:
                    prev.next = entry.next
                else:
                    self.table[hc] = entry.next
                self.N -= 1
                return entry.value

            prev, entry = entry, entry.next

        return None                 # Nothing was removed

def most_duplicated(A):
    """
    Return element most duplicated in A. In the case of a tie,
    any value that is repeated that many times can be returned.

    most_duplicated([1,2,3,4]) can return 1, 2, 3, or 4
    most_duplicated([1,2,1,3]) must return 1
    """
    counts = {}
    most = None
    count = 0

    for v in A:
        if v in counts:
            counts[v] += 1
        else:
            counts[v] = 1

        if counts[v] > count:
            count = counts[v]
            most = v

    return most

#######################################################################
if __name__ == '__main__':
    from resources.english import english_words
    measure_performance_resize()

    prime_number_difference(english_words())

    # This takes quite a while to execute because of poor
    # hashing. Be patient!
    bad_timing(english_words()[:20000])