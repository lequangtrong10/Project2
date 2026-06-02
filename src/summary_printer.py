def print_summary(summary, checkpoint=None, processed_count=None):
    print("\n" + "=" * 40)
    print("JOB SUMMARY")
    print("=" * 40)

    print(f"Input IDs     : {summary.get('input_count', 0)}")
    print(f"Success       : {summary.get('success_count', 0)}")
    print(f"Failed        : {summary.get('failed_count', 0)}")
    print(f"Warnings      : {summary.get('warning_count', 0)}")

    print("\nError Breakdown:")
    error_breakdown = summary.get("error_breakdown", {})

    if error_breakdown:
        for error_type, count in error_breakdown.items():
            print(f"- {error_type}: {count}")
    else:
        print("- None")

    print("\nWarning Breakdown:")
    warning_breakdown = summary.get("warning_breakdown", {})

    if warning_breakdown:
        for warning_type, count in warning_breakdown.items():
            print(f"- {warning_type}: {count}")
    else:
        print("- None")

    if "runtime_seconds" in summary:
        print(f"\nRuntime       : {summary['runtime_seconds']} seconds")

    if "throughput_per_second" in summary:
        print(f"Throughput    : {summary['throughput_per_second']} products/sec")

    if checkpoint:
        print(f"\nCheckpoint    : batch {checkpoint.get('last_completed_batch')}")

    if processed_count is not None:
        print(f"Processed IDs : {processed_count}")

    print("=" * 40)