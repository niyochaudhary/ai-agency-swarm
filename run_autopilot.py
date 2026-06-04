import argparse
import signal
import sys
import time

from core.swarm_master import SwarmMaster

running = True


def signal_handler(signum, frame):
    global running
    print("\n[Autopilot] Shutdown signal received. Stopping autopilot...")
    running = False


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(
        description="Run the AI Agency autopilot lead hunt.")
    parser.add_argument("--niche", default="Dentist",
                        help="Niche to hunt leads for")
    parser.add_argument("--location", default="New York",
                        help="Location to hunt leads in")
    parser.add_argument("--count", type=int, default=5,
                        help="Number of leads to process per run")
    parser.add_argument("--runs", type=int, default=1,
                        help="Number of hunts to execute. Set 0 for continuous mode.")
    parser.add_argument("--interval", type=int, default=0,
                        help="Minutes to wait between runs")
    parser.add_argument("--live", action="store_true",
                        help="Enable live email sending instead of dry run")
    args = parser.parse_args()

    master = SwarmMaster(sender_dry_run=not args.live)
    print(f"[Autopilot] Starting autopilot: niche={args.niche}, location={args.location}, count={args.count}, runs={args.runs}, live={args.live}")

    if args.runs == 0:
        print("[Autopilot] Continuous mode enabled. Use Ctrl+C to stop.")
        run_index = 0
        while running:
            run_index += 1
            print(f"[Autopilot] Run {run_index} (continuous)")
            master.orchestrate_hunt(args.niche, args.location, count=args.count)
            if args.interval > 0 and running:
                print(f"[Autopilot] Waiting {args.interval} minutes before next hunt...")
                time.sleep(args.interval * 60)
    else:
        for run_index in range(args.runs):
            if not running:
                break

            print(f"[Autopilot] Run {run_index + 1}/{args.runs}")
            master.orchestrate_hunt(args.niche, args.location, count=args.count)

            if run_index + 1 < args.runs and args.interval > 0 and running:
                print(f"[Autopilot] Waiting {args.interval} minutes before next hunt...")
                time.sleep(args.interval * 60)

    print("[Autopilot] Completed autopilot execution.")


if __name__ == "__main__":
    main()
