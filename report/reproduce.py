"""Run the lab with the same model limits used in the report."""
import argparse
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from lab.curator import curate_skills
from lab.model import make_model
from lab.runner import CONDITIONS, run_task
from lab.tasks import list_tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", required=True, choices=[*CONDITIONS, "curator"])
    parser.add_argument("--tasks", nargs="+", default=["learn"])
    parser.add_argument("--results", default="results")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--recursion-limit", type=int, default=60)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    model = make_model()
    model.max_tokens = args.max_tokens
    model.max_retries = 1
    model.request_timeout = 60
    if args.condition == "curator":
        for path in curate_skills(results_dir=args.results, model=model):
            print("wrote", path, flush=True)
        return
    if args.tasks in (["learn"], ["eval"], ["all"]):
        tasks = [task.id for task in list_tasks(None if args.tasks == ["all"] else args.tasks[0])]
    else:
        tasks = args.tasks
    def run(task):
        model = make_model()
        model.max_tokens = args.max_tokens
        model.max_retries = 1
        model.request_timeout = 60
        print("START", args.condition, task, flush=True)
        record = run_task(task, args.condition, args.results, model=model, recursion_limit=args.recursion_limit)
        record["run_config"] = {
            "model": model.model_name, "temperature": 0, "max_tokens": args.max_tokens,
            "recursion_limit": args.recursion_limit,
        }
        path = Path(args.results) / args.condition / task / "run.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{args.condition} {task}: {record['passed']}/{record['total']}, "
              f"tokens={record['tokens']['total']}, seconds={record['seconds']}", flush=True)
        if record["error"] and not record["error"].startswith("GraphRecursionError"):
            raise RuntimeError(record["error"])
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(run, tasks):
            pass


if __name__ == "__main__":
    main()
