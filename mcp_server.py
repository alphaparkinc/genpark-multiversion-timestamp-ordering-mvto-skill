import json
import sys
from client import MVTOTimestampStore

store = MVTOTimestampStore()

def handle_rpc(line):
    try:
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        rid = req.get("id")
        
        if method == "tools/list":
            tools = [
                {"name": "write_version", "description": "Write a version with timestamp ordering"},
                {"name": "read_version", "description": "Read highest version with wts <= txn_ts"},
                {"name": "gc", "description": "Garbage collect obsolete versions"}
            ]
            return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
        elif method == "tools/call":
            tname = params.get("name")
            args = params.get("arguments", {})
            if tname == "write_version":
                success = store.write(args["key"], args["value"], args["txn_ts"])
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"success": success}})
            elif tname == "read_version":
                val = store.read(args["key"], args["txn_ts"])
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"value": val}})
            elif tname == "gc":
                count = store.garbage_collect(args["min_active_ts"])
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"purged": count}})
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(handle_rpc(line.strip()), flush=True)
