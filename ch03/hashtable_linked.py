"""
    Hashtable to store (key, value) pairs in a fixed hashtable of linked
    lists, using hash() % N as hash code.  This table can replace values
    associated with a given key.  When two keys attempt to use
    the same location, a linked list is constructed.

    Hashtable will never "run out" of storage, though performance suffers
    as more (key, value) pairs are added.
"""

from ch03.entry import LinkedEntry

def stats_linked_lists(words, table, output=False):
    """Produce statistics on the linked-list implemented table."""
    for w in words:
        table.put(w, 1)
    size = len(table.table)
    sizes = {}                      # record how many chains of given size exist
    total_search = 0
    max_length = 0
    for i in range(size):
        num = 0
        idx = i
        entry = table.table[idx]
        while entry:                # count how many are in this entry
            entry = entry.next
            num += 1
            total_search += num     # each entry in the linked list requires more searches to find
        if num in sizes:            # also counts number with NO entries
            sizes[num] = sizes[num] + 1
        else:
            sizes[num] = 1
        if num > max_length:
            max_length = num

    if output:
        print('nLinked List ({} total entries in base size of {})'.format(words, size))
        for i in range(size):
            if i in sizes:
                print('{} linked lists have size of {}'.format(sizes[i], i))

    return ((1.0*total_search) / len(words), max_length)

def linked_list_entries(ht):
    """Generate all (k, v) tuples for entries in all linked lists table."""
    for entry in ht.table:
        while entry:
            yield (entry.key, entry.value)
            entry = entry.next

class Hashtable:
    """Hashtable using array of M linked lists."""
    def __init__(self, M=10):
        self.table = [None] * M
        if M < 1:
            raise ValueError('Hashtable storage must be at least 1.')
        self.M = M
        self.N = 0

    def get(self, k):
        """Retrieve value associated with key, k."""
        hc = hash(k) % self.M       # First place it could be
        entry = self.table[hc]
        while entry:
            if entry.key == k:
                return entry.value
            entry = entry.next
        return None                 # Couldn't find

    def put(self, k, v):
        """Associate value, v, with the key, k."""
        hc = hash(k) % self.M       # First place it could be
        entry = self.table[hc]
        while entry:
            if entry.key == k:      # Overwrite if already here
                entry.value = v
                return
            entry = entry.next

        self.table[hc] = LinkedEntry(k, v, self.table[hc])
        self.N += 1

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

class DynamicHashtable:
    """Hashtable usingn array of M linked lists that can resize over time."""
    def __init__(self, M=10):
        self.table = [None] * M
        if M < 1:
            raise ValueError('Hashtable storage must be at least 1.')
        self.M = M
        self.N = 0

        self.load_factor = 0.75

        # Ensure resize event happens NO LATER than M-1, to align
        # with open addressing
        self.threshold = min(M * self.load_factor, M-1)

    def get(self, k):
        """Retrieve value associated with key, k."""
        hc = hash(k) % self.M       # First place it could be
        entry = self.table[hc]
        while entry:
            if entry.key == k:
                return entry.value
            entry = entry.next
        return None                 # Couldn't find

    def put(self, k, v):
        """Associate value, v, with the key, k."""
        hc = hash(k) % self.M       # First place it could be
        entry = self.table[hc]
        while entry:
            if entry.key == k:      # Overwrite if already here
                entry.value = v
                return
            entry = entry.next

        # insert, and then trigger resize if hit threshold.
        self.table[hc] = LinkedEntry(k, v, self.table[hc])
        self.N += 1

        if self.N >= self.threshold:
            self.resize(2*self.M + 1)

    def resize(self, new_size):
        """Resize table and rehash existing entries into new table."""
        temp = DynamicHashtable(new_size)
        for n in self.table:
            while n:
                temp.put(n.key, n.value)
                n = n.next
        self.table = temp.table
        temp.table = None     # ensures memory is freed
        self.M = temp.M
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