import argparse
import json
import random
from pathlib import Path

from aufgaben.core.io import write_manifest, write_tasks
from aufgaben.core.moodle_xml import export_json_to_moodle_xml, export_manifest_to_moodle_xml
from aufgaben.core.models import Task
from aufgaben.core.validation import validate_batch
from aufgaben.generators.registry import REGISTRY, build_generator
from aufgaben.tools.validate_binomial_semantics import main as validate_binomial_semantics_main


def _default_output(generator_key: str) -> str:
    file_name = generator_key.replace(".", "_") + ".json"
    return str(Path("aufgaben") / "exports" / "json" / file_name)


def _derive_xml_output_path(json_output: str) -> Path:
    json_path = Path(json_output)
    parts = list(json_path.parts)

    try:
        json_index = parts.index("json")
        if json_index > 0 and parts[json_index - 1] == "exports":
            xml_parts = parts[:json_index] + ["xml"] + parts[json_index + 1 :]
            return Path(*xml_parts).with_suffix(".xml")
    except ValueError:
        pass

    return json_path.with_suffix(".xml")


def _derive_category_from_json_output(json_output: str) -> str:
    json_path = Path(json_output).with_suffix("")
    parts = list(json_path.parts)

    try:
        json_index = parts.index("json")
        if json_index > 0 and parts[json_index - 1] == "exports":
            relative_parts = parts[json_index + 1 :]
            if relative_parts:
                return "/".join(relative_parts)
    except ValueError:
        pass

    if json_path.stem:
        return json_path.stem
    return "aufgaben"


def _refresh_manifest_for_output(output_path: str) -> None:
    path = Path(output_path)
    for candidate in [path.parent, *path.parents]:
        if candidate.name == "json" and candidate.parent.name == "exports":
            write_manifest(str(candidate))
            return


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


def _resolve_question_order(target: dict, job: dict, defaults: dict) -> str:
    raw = target.get("questionOrder", job.get("questionOrder", defaults.get("questionOrder", "fixed")))
    value = str(raw).strip().lower()
    if value not in {"fixed", "shuffle"}:
        raise ValueError(f"Ungültiger Wert für questionOrder: {raw}. Erlaubt: fixed, shuffle")
    return value


def _apply_question_order(tasks: list[Task], question_order: str, seed: int | None) -> None:
    if question_order == "fixed":
        return

    rng = random.Random(seed)
    for task in tasks:
        if len(task.fragen) <= 1:
            continue
        pairs = list(zip(task.fragen, task.antworten))
        rng.shuffle(pairs)
        task.fragen = [question for question, _ in pairs]
        task.antworten = [answer for _, answer in pairs]


def run_single(
    generator_key: str,
    count: int,
    seed: int | None,
    output: str,
    question_order: str = "fixed",
    export_xml: bool = True,
) -> None:
    generator = build_generator(generator_key)
    tasks = generator.generate(count=count, seed=seed)
    _apply_question_order(tasks, question_order=question_order, seed=seed)
    validate_batch(tasks, expected_count=count)
    write_tasks(output, tasks)
    _refresh_manifest_for_output(output)

    if export_xml:
        xml_output = _derive_xml_output_path(output)
        xml_category = _derive_category_from_json_output(output)
        export_json_to_moodle_xml(
            input_json_path=output,
            output_xml_path=str(xml_output),
            category=xml_category,
            include_answers=True,
        )
        print(
            f"OK: {len(tasks)} Aufgaben geschrieben nach {output} "
            f"und XML nach {xml_output} (questionOrder={question_order})"
        )
        return

    print(
        f"OK: {len(tasks)} Aufgaben geschrieben nach {output} "
        f"(nur JSON, questionOrder={question_order})"
    )


def run_batch(config_path: str) -> None:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    jobs = config.get("jobs", [])
    if not jobs:
        raise ValueError("Batch-Konfiguration enthält keine Jobs.")

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
                question_order = _resolve_question_order(target=target, job=job, defaults=defaults)
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
                    question_order=question_order,
                    export_xml=False,
                )
            continue

        output = job.get("output")
        question_order = _resolve_question_order(target={}, job=job, defaults=defaults)
        if output is None:
            output = str(
                Path(default_output_dir) / f"{generator_key.replace('.', '_')}_{job_index}.json"
            )
        run_single(
            generator_key=generator_key,
            count=count,
            seed=seed,
            output=output,
            question_order=question_order,
            export_xml=False,
        )

    write_manifest(default_output_dir)


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

    moodle_parser = subparsers.add_parser("moodle", help="Eine Aufgaben-JSON nach Moodle-XML exportieren")
    moodle_parser.add_argument("--input", type=str, required=True)
    moodle_parser.add_argument("--output", type=str, required=True)
    moodle_parser.add_argument("--category", type=str, default=None)
    moodle_parser.add_argument("--without-answers", action="store_true")

    moodle_batch_parser = subparsers.add_parser(
        "moodle-batch",
        help="Alle JSONs aus Manifest nach Moodle-XML exportieren",
    )
    moodle_batch_parser.add_argument(
        "--manifest",
        type=str,
        default=str(Path("aufgaben") / "exports" / "json" / "manifest.json"),
    )
    moodle_batch_parser.add_argument(
        "--exports-root",
        type=str,
        default=str(Path("aufgaben") / "exports" / "json"),
    )
    moodle_batch_parser.add_argument(
        "--output-root",
        type=str,
        default=str(Path("aufgaben") / "exports" / "xml"),
    )
    moodle_batch_parser.add_argument("--without-answers", action="store_true")

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
            question_order="fixed",
        )
        return

    if args.command == "batch":
        run_batch(args.config)
        return

    if args.command == "moodle":
        output = export_json_to_moodle_xml(
            input_json_path=args.input,
            output_xml_path=args.output,
            category=args.category,
            include_answers=not args.without_answers,
        )
        print(f"OK: Moodle-XML geschrieben nach {output}")
        return

    if args.command == "moodle-batch":
        outputs = export_manifest_to_moodle_xml(
            manifest_path=args.manifest,
            exports_json_root=args.exports_root,
            output_root=args.output_root,
            include_answers=not args.without_answers,
        )
        print(f"OK: {len(outputs)} Moodle-XML-Dateien geschrieben nach {args.output_root}")
        return

    if args.command == "validate-binomial":
        validate_binomial_semantics_main()
        return


if __name__ == "__main__":
    main()
