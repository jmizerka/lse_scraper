import argparse
import sys
import subprocess


def start_process(cmd):
    return subprocess.Popen(cmd)


def run_all(args):

    processes = [start_process(["python", "-m", "api.entrypoint"])]

    if args.cli_input and args.cli_output:
        processes.append(
            start_process(
                [
                    "python",
                    "-m",
                    "cli.entrypoint",
                    "--input",
                    args.cli_input,
                    "--output",
                    args.cli_output,
                ],
            )
        )

    if args.cron_input and args.cron_output:
        processes.append(
            start_process(
                [
                    "python",
                    "-m",
                    "cron.entrypoint",
                    "--input",
                    args.cron_input,
                    "--output",
                    args.cron_output,
                    "--cron",
                    args.cron_expr,
                ],
            )
        )
    if args.watchdog_input_dir and args.watchdog_output_dir:
        processes.append(
            start_process(
                [
                    "python",
                    "-m",
                    "watchdog.entrypoint",
                    "--input-dir",
                    args.watchdog_input_dir,
                    "--output-dir",
                    args.watchdog_output_dir,
                ],
            )
        )
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
        sys.exit(0)


def run_api():
    subprocess.run(["python", "-m", "api.entrypoint"], check=True)


def run_cli(args):
    subprocess.run(
        ["python", "-m", "cli.entrypoint", "--input", args.input, "--output", args.output],
        check=True,
    )


def run_cron(args):
    subprocess.run(
        [
            "python",
            "-m",
            "cron.entrypoint",
            "--input",
            args.input,
            "--output",
            args.output,
            "--cron",
            args.cron,
        ],
        check=True,
    )


def run_watchdog(args):
    subprocess.run(
        [
            "python",
            "-m",
            "watchdog.entrypoint",
            "--input-dir",
            args.input_dir,
            "--output-dir",
            args.output_dir,
        ],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Run adapters or all concurrently.")
    subparsers = parser.add_subparsers(dest="adapter", required=True)

    subparsers.add_parser("api", help="Run API service")

    cli_parser = subparsers.add_parser("cli", help="Run CLI adapter")
    cli_parser.add_argument("--input", "-i", required=True, help="Input CSV file")
    cli_parser.add_argument("--output", "-o", required=True, help="Output CSV file")

    cron_parser = subparsers.add_parser("cron", help="Run Cron adapter")
    cron_parser.add_argument("--input", "-i", required=True)
    cron_parser.add_argument("--output", "-o", required=True)
    cron_parser.add_argument("--cron", default="*/5 * * * *", help="Cron schedule")

    watch_parser = subparsers.add_parser("watchdog", help="Run Watchdog adapter")
    watch_parser.add_argument("--input-dir", "-i", required=True)
    watch_parser.add_argument("--output-dir", "-o", required=True)

    all_parser = subparsers.add_parser("all", help="Run all adapters concurrently")
    all_parser.add_argument("--cli-input")
    all_parser.add_argument("--cli-output")
    all_parser.add_argument("--cron-input")
    all_parser.add_argument("--cron-output")
    all_parser.add_argument("--cron-expr", default="*/5 * * * *")
    all_parser.add_argument("--watchdog-input-dir")
    all_parser.add_argument("--watchdog-output-dir")

    args = parser.parse_args()

    if args.adapter == "api":
        run_api()
    elif args.adapter == "cli":
        run_cli(args)
    elif args.adapter == "cron":
        run_cron(args)
    elif args.adapter == "watchdog":
        run_watchdog(args)
    elif args.adapter == "all":
        run_all(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
