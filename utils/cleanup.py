import time

from .storage import EvaluationStore


def cleanup_old_evaluations(store: EvaluationStore):
    try:
        if store._use_redis:
            return

        now = time.time()
        to_remove = []
        for key, (expire_at, _) in getattr(store, "_mem", {}).items():
            if expire_at < now:
                to_remove.append(key)

        for key in to_remove:
            del store._mem[key]

        if to_remove:
            print(f"[Cleanup] Removed {len(to_remove)} expired evaluations.")
    except Exception as e:
        print(f"[Cleanup] Error during cleanup: {str(e)}")
