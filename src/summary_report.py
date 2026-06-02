from collections import Counter
from datetime import datetime


def build_summary(input_count, products, failed, warnings, start_time=None, end_time=None):
    """
    Tạo báo cáo tổng quan sau khi chạy crawler.
    """

    error_breakdown = Counter(
        item.get("error_type", "UNKNOWN_ERROR")
        for item in failed
    )

    warning_breakdown = Counter()

    for item in warnings:
        for warning in item.get("warnings", []):
            warning_breakdown[warning] += 1

    summary = {
        "input_count": input_count,
        "success_count": len(products),
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "error_breakdown": dict(error_breakdown),
        "warning_breakdown": dict(warning_breakdown),
    }

    if start_time and end_time:
        runtime_seconds = (end_time - start_time).total_seconds()
        summary["runtime_seconds"] = runtime_seconds

        if runtime_seconds > 0:
            summary["throughput_per_second"] = round(input_count / runtime_seconds, 2)

    summary["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return summary