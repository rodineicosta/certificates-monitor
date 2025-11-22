import atexit
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template

from utils.mysql_monitor import MySQLMonitor

app = Flask(__name__)
monitor = MySQLMonitor()
scheduler = BackgroundScheduler()

# Cache for monitoring data.
monitoring_data = {
    "integrity_checks": {},
    "last_update": "Never",
    "status": "error",
}


def update_monitoring_data():
    """Update monitoring data from the database"""
    global monitoring_data
    print("\n=== STARTING DATA UPDATE... ===")

    try:
        print("[1/9] Getting total counts...")
        total_counts = monitor.get_total_counts()
        print(f"[1/9] OK")

        print("[2/9] Getting table statistics...")
        table_stats = monitor.get_table_stats()
        print(f"[2/9] OK - {len(table_stats)} tables")

        print("[3/9] Getting certificate usage...")
        certificate_usage = monitor.get_certificate_usage()
        print(f"[3/9] OK")

        print("[4/9] Checking data integrity...")
        integrity_checks = monitor.check_data_integrity()
        print(f"[4/9] OK - {len(integrity_checks)} checks")

        print("[5/9] Getting recent activity...")
        recent_activity = monitor.get_recent_activity(1)
        print(f"[5/9] OK")

        print("[6/9] Getting recent certificates...")
        certificates = monitor.get_certificates()
        print(f"[6/9] OK - {len(certificates)} certificates")

        print("[7/9] Getting recent certificates...")
        recent_certificates = monitor.get_recent_certificates(7)
        print(f"[7/9] OK - {len(recent_certificates)} recent certificates")

        print("[8/9] Getting failed tasks...")
        failed_tasks = monitor.get_failed_queue_tasks()
        print(f"[8/9] OK - {len(failed_tasks)} failed tasks")

        print("[9/9] Getting certificates by day...")
        certificates_by_day = monitor.get_certificates_by_day(7)
        print(f"[9/9] OK - {len(certificates_by_day)} days")

        monitoring_data = {
            "total_counts": total_counts,
            "table_stats": table_stats,
            "certificates": certificates,
            "certificates_by_day": certificates_by_day,
            "certificate_usage": certificate_usage,
            "failed_tasks": failed_tasks,
            "integrity_checks": integrity_checks,
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "recent_activity": recent_activity,
            "recent_certificates": recent_certificates,
            "status": "ok",
        }
        print("=== UPDATE COMPLETED SUCCESSFULLY! ===\n")

    except Exception as e:
        print(f"[ERROR] Update failed: {e}")
        print(f"[ERROR] Type: {type(e).__name__}")
        import traceback

        traceback.print_exc()

        monitoring_data = {
            "total_counts": {},
            "table_stats": [],
            "integrity_checks": {},
            "certificates": [],
            "recent_certificates": [],
            "failed_tasks": [],
            "certificates_by_day": [],
            "last_update": "Update error",
            "status": "error",
            "error_message": str(e),
        }


@app.route("/")
def dashboard():
    """Main dashboard"""
    return render_template("dashboard.html", data=monitoring_data)


@app.route("/certificates")
def certificates_page():
    """Certificates page with pagination"""
    from flask import request

    page = request.args.get("page", 1, type=int)
    per_page = 10

    certificates = monitoring_data.get("certificates", [])
    total = len(certificates)
    start = (page - 1) * per_page
    end = start + per_page

    paginated_certs = certificates[start:end]
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "certificates.html",
        certificates=paginated_certs,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@app.route("/failures")
def failures_page():
    """Failures page with pagination"""
    from flask import request

    page = request.args.get("page", 1, type=int)
    per_page = 10

    failures = monitoring_data.get("failed_tasks", [])
    total = len(failures)
    start = (page - 1) * per_page
    end = start + per_page

    paginated_failures = failures[start:end]
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "failures.html",
        failures=paginated_failures,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@app.route("/api/stats")
def api_stats():
    return jsonify(monitoring_data)


@app.route("/api/health")
def health_check():
    integrity = monitor.check_data_integrity()
    return jsonify(
        {
            "status": (
                "healthy" if all(v == 0 for v in integrity.values()) else "issues"
            ),
            "integrity_checks": integrity,
        }
    )


@app.route("/api/failure-details/<int:task_id>")
def failure_details(task_id):
    """Get detailed information about a failed task"""
    try:
        details = monitor.get_failure_details(task_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/certificate-details/<int:cert_id>")
def certificate_details(cert_id):
    """Get detailed information about a certificate"""
    try:
        details = monitor.get_certificate_details(cert_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ensure connections are properly closed.
def cleanup():
    print("[Cleanup] Shutting down application...")
    if scheduler.running:
        scheduler.shutdown()
    monitor.close()


atexit.register(cleanup)

if __name__ == "__main__":
    # Update data on startup.
    update_monitoring_data()

    # Schedule automatic updates every 5 minutes.
    scheduler.add_job(
        func=update_monitoring_data,
        trigger="interval",
        minutes=5,
        id="update_data",
        name="Update monitoring data every 5 minutes",
        replace_existing=True,
    )
    scheduler.start()
    print("[Scheduler] Scheduler started - Updates every 5 minutes.")
    try:
        app.run(host="0.0.0.0", port=5001, debug=False)
    except (KeyboardInterrupt, SystemExit):
        cleanup()
