import sys
from client import MVTOTimestampStore

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def run():
    print(">>> Demonstrating MVTO Concurrency Control...")
    store = MVTOTimestampStore()
    
    # Txn 10 writes account A
    assert store.write("acc_A", 1000, txn_ts=10) is True
    # Txn 15 reads account A
    val = store.read("acc_A", txn_ts=15)
    print(f"Txn 15 read acc_A: {val}")
    assert val == 1000
    
    # Txn 12 attempts to write acc_A (conflict: txn 15 already read a newer version)
    res = store.write("acc_A", 1200, txn_ts=12)
    print(f"Txn 12 write acc_A (ts=12 < rts=15): aborted = {not res}")
    assert res is False
    
    # Txn 20 writes acc_A
    assert store.write("acc_A", 2000, txn_ts=20) is True
    # Txn 18 reads acc_A (should read version from ts=10)
    val_18 = store.read("acc_A", txn_ts=18)
    print(f"Txn 18 read acc_A: {val_18}")
    assert val_18 == 1000
    
    # GC test
    gc_count = store.garbage_collect(min_active_ts=20)
    print(f"Garbage collected {gc_count} obsolete versions.")
    print("[PASS] MVTO Concurrency Control verified.")

if __name__ == "__main__":
    run()
