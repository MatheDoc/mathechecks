import argparse
import json
from pathlib import Path

from aufgaben.core.io import write_tasks
from aufgaben.core.validation import validate_batch
from aufgaben.generators.registry import REGISTRY, build_generator
from aufgaben.tools.validate_binomial_semantics import main as validate_binomial_semantics_main


def _default_output(generator_key: str) -> str:
    file_name = generator_key.replace(".", "_") + ".json"
    return str(Path("aufgaben") / "exports" / "json" / file_name)


def _slug(text: str) -> str:
    return text.strip().replace(" ", "_")


def _target_output(
    target: dict,
    generator_key: str,
    output_dir: str,
    default_index: int,
) -> str:
    if "output" in target:
        return target["output"]

    gebiet = _slug(target.get("gebiet", "unsorted"))
    lernbereich = _slug(target.get("lernbereich", "unsorted"))
    file_stem = _slug(target.get("sammlung", f"{generator_key.replace('.', '_')}_{default_index}"))
    return str(Path(output_dir) / gebiet / lernbereich / f"{file_stem}.json")


def run_single(
    generator_key: str,
    count: int,
    seed: int | None,
    output: str,
) -> None:
    generator = build_generator(generator_key)
    tasks = generator.generate(count=count, seed=seed)
    validate_batch(tasks, expected_count=count)
    write_tasks(output, tasks)
    print(f"OK: {len(tasks)} Aufgaben geschrieben nach {output}")


def _collect_expected_outputs(
    jobs: list, defaults: dict, default_output_dir: str, static: list | None = None,
) -> set[Path]:
    expected: set[Path] = set()
    default_count = int(defaults.get("count", 20))
    for job_index, job in enumerate(jobs, start=1):
        generator_key = job["generator"]
        targets = job.get("targets")
        if targets:
            for target_index, target in enumerate(targets, start=1):
                output = _target_output(
                    target=target,
                    generator_key=generator_key,
                    output_dir=default_output_dir,
                    default_index=target_index,
                )
                expected.add(Path(output).resolve())
        else:
            output = job.get("output")
            if output is None:
                output = str(
                    Path(default_output_dir) / f"{generator_key.replace('.', '_')}_{job_index}.json"
                )
            expected.add(Path(output).resolve())

    for entry in static or []:
        gebiet = _slug(entry.get("gebiet", "unsorted"))
        lernbereich = _slug(entry.get("lernbereich", "unsorted"))
        sammlung = _slug(entry.get("sammlung", "unknown"))
        path = Path(default_output_dir) / gebiet / lernbereich / f"{sammlung}.json"
        expected.add(path.resolve())

    return expected


def _report_unlisted_exports(output_dir: str, expected_outputs: set[Path]) -> None:
    root = Path(output_dir)
    unlisted = []
    for json_file in root.rglob("*.json"):
        if json_file.resolve() not in expected_outputs:
            unlisted.append(json_file)

    if unlisted:
        print(f"HINWEIS: {len(unlisted)} JSON(s) in {root} sind nicht in project_config.json gelistet:")
        for f in sorted(unlisted):
            print(f"  - {f}")


def _job_matches_filter(job: dict, filter_text: str) -> bool:
    """Prüft ob ein Job den Filter-Text im Generator-Key oder einer Sammlung enthält."""
    text = filter_text.lower()
    if text in job["generator"].lower():
        return True
    for target in job.get("targets", []):
        if text in target.get("sammlung", "").lower():
            return True
    return False


def run_batch(config_path: str, filter_text: str | None = None) -> None:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    jobs = config.get("jobs", [])
    if not jobs:
        raise ValueError("Batch-Konfiguration enthält keine Jobs.")

    if filter_text:
        jobs = [j for j in jobs if _job_matches_filter(j, filter_text)]
        if not jobs:
            print(f"Keine Jobs gefunden für Filter '{filter_text}'.")
            return
        print(f"Filter '{filter_text}': {len(jobs)} Job(s) ausgewählt.")

    defaults = config.get("defaults", {})
    default_count = int(defaults.get("count", 20))
    default_output_dir = defaults.get("outputDir", str(Path("aufgaben") / "exports" / "json"))

    for job_index, job in enumerate(jobs, start=1):
        generator_key = job["generator"]
        count = int(job.get("count", default_count))
        seed = job.get("seed")

        targets = job.get("targets")
        if targets:
            for target_index, target in enumerate(targets, start=1):
                target_count = int(target.get("count", count))
                target_seed = target.get("seed", seed)
                output = _target_output(
                    target=target,
                    generator_key=generator_key,
                    output_dir=default_output_dir,
                    default_index=target_index,
                )
                run_single(
                    generator_key=generator_key,
                    count=target_count,
                    seed=target_seed,
                    output=output,
                )
            continue

        output = job.get("output")
        if output is None:
            output = str(
                Path(default_output_dir) / f"{generator_key.replace('.', '_')}_{job_index}.json"
            )
        run_single(
            generator_key=generator_key,
            count=count,
            seed=seed,
            output=output,
        )

    if not filter_text:
        static = config.get("static", [])
        expected = _collect_expected_outputs(jobs, defaults, default_output_dir, static=static)
        _report_unlisted_exports(default_output_dir, expected)


def main() -> None:
    parser = argparse.ArgumentParser(description="JSON-Aufgabengenerator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="Verfügbare Generatoren anzeigen")
    list_parser.set_defaults(command="list")

    generate_parser = subparsers.add_parser("generate", help="Einen Generator ausführen")
    generate_parser.add_argument("generator", choices=sorted(REGISTRY.keys()))
    generate_parser.add_argument("--count", type=int, default=20)
    generate_parser.add_argument("--seed", type=int, default=None)
    generate_parser.add_argument("--output", type=str, default=None)

    batch_parser = subparsers.add_parser("batch", help="Mehrere Generator-Jobs aus Config ausführen")
    batch_parser.add_argument("--config", type=str, default=str(Path("aufgaben") / "project_config.json"))
    batch_parser.add_argument("--filter", type=str, default=None,
                              help="Nur Jobs ausführen, deren Generator-Key oder Sammlung diesen Text enthält")

    validate_binomial_parser = subparsers.add_parser(
        "validate-binomial",
        help="Interne Plausibilitätsprüfung für Binomial-Generatoren ausführen",
    )
    validate_binomial_parser.set_defaults(command="validate-binomial")

    args = parser.parse_args()

    if args.command == "list":
        for key in sorted(REGISTRY.keys()):
            print(key)
        return

    if args.command == "generate":
        output = args.output or _default_output(args.generator)
        run_single(
            generator_key=args.generator,
            count=args.count,
            seed=args.seed,
            output=output,
        )
        return

    if args.command == "batch":
        run_batch(args.config, filter_text=args.filter)
        return

    if args.command == "validate-binomial":
        validate_binomial_semantics_main()
        return


if __name__ == "__main__":
    main()
