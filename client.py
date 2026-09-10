class MVTOTimestampStore:
    """
    Multiversion Timestamp Ordering (MVTO) storage engine.
    Maintains ordered immutable versions for each key with read/write timestamps.
    """
    def __init__(self):
        self.versions = {} # key -> list of [wts, rts, val]

    def write(self, key, val, txn_ts):
        if key not in self.versions:
            self.versions[key] = [[0, 0, None]]
        latest_wts, latest_rts, _ = self.versions[key][-1]
        # If a transaction with newer timestamp has already read a version that this write would supersede:
        if txn_ts < latest_rts:
            return False # Abort write
        # Thomas Write Rule: if txn_ts < latest_wts, write can be ignored/superseded or rejected
        if txn_ts < latest_wts:
            return True # Ignored write succeeds without mutation
        self.versions[key].append([txn_ts, txn_ts, val])
        return True

    def read(self, key, txn_ts):
        if key not in self.versions:
            return None
        # Find version with largest wts <= txn_ts
        target_idx = None
        for i, (wts, rts, val) in enumerate(self.versions[key]):
            if wts <= txn_ts:
                target_idx = i
        if target_idx is not None:
            wts, rts, val = self.versions[key][target_idx]
            self.versions[key][target_idx][1] = max(rts, txn_ts)
            return val
        return None

    def garbage_collect(self, min_active_ts):
        """Purges old versions no longer visible to any active transaction."""
        collected = 0
        for key in list(self.versions.keys()):
            vers = self.versions[key]
            # Keep the newest version with wts <= min_active_ts and all subsequent versions
            cutoff_idx = 0
            for i, (wts, rts, val) in enumerate(vers):
                if wts <= min_active_ts:
                    cutoff_idx = i
            if cutoff_idx > 0:
                collected += cutoff_idx
                self.versions[key] = vers[cutoff_idx:]
        return collected
