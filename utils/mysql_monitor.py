import json
import pymysql

from config.config import DB_CONFIG
from config.queries import MONITORING_QUERIES
from utils.ssh_client import SSHTunnel


class LDCDSMonitor:
    def __init__(self):
        self.ssh_tunnel = None
        self.connection = None

    def _get_connection(self):
        """Create or get a database connection"""
        if (
            not self.ssh_tunnel
            or not self.ssh_tunnel.tunnel
            or not self.ssh_tunnel.tunnel.is_active
        ):
            self.ssh_tunnel = SSHTunnel()
            self.ssh_tunnel.__enter__()

        if not self.connection or not self.connection.open:
            self.connection = pymysql.connect(
                host="127.0.0.1",
                port=self.ssh_tunnel.tunnel.local_bind_port,
                user=DB_CONFIG["username"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                charset="utf8mb4",
                connect_timeout=10,
            )
            print("[DB] Database connection established!")

        return self.connection

    def close(self):
        """Close connection and tunnel"""
        print("[Monitor] Closing connections...")
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        if self.ssh_tunnel:
            try:
                self.ssh_tunnel.__exit__(None, None, None)
            except:
                pass

    def get_total_counts(self):
        """Get total counts"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(MONITORING_QUERIES["total_counts"])
        result = cursor.fetchone()

        cursor.close()
        return result

    def get_certificates_by_day(self, days=7):
        """Get certificates grouped by day"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(MONITORING_QUERIES["certificates_by_day"])
        results = cursor.fetchall()

        # Format dates to strings in Brazilian format.
        formatted_results = []
        for row in results:
            formatted_results.append(
                {
                    "date": (
                        row["date"].strftime("%d/%m")
                        if hasattr(row["date"], "strftime")
                        else str(row["date"])
                    ),
                    "date_full": (
                        row["date"].strftime("%Y-%m-%d")
                        if hasattr(row["date"], "strftime")
                        else str(row["date"])
                    ),
                    "count": row["count"],
                }
            )

        cursor.close()
        return formatted_results

    def get_table_stats(self):
        """Get table statistics"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Fetch table information.
        cursor.execute(MONITORING_QUERIES["table_sizes"])
        tables_info = cursor.fetchall()

        # For each table, count exact records.
        results = []
        for table in tables_info:
            table_name = table["Tabela"]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()["count"]

            results.append(
                {
                    "Tabela": table_name,
                    "Registros": count,
                    "Tamanho (MB)": table["Tamanho (MB)"],
                }
            )

        cursor.close()
        return results

    def get_certificates(self):
        """Get all certificates"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(MONITORING_QUERIES["certificates"])
        results = cursor.fetchall()

        cursor.close()
        return results

    def get_recent_certificates(self, days=7):
        """Get recent certificates"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(MONITORING_QUERIES["recent_certificates"])
        results = cursor.fetchall()

        cursor.close()
        return results

    def get_failed_queue_tasks(self):
        """Get failed tasks in the queue"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute(MONITORING_QUERIES["failed_queue_tasks"])
        results = cursor.fetchall()

        # Process JSON payload.
        processed_results = []
        for task in results:
            try:
                payload = json.loads(task["payload"])

                # Extract information from JSON.
                student_name = payload.get("signer", {}).get("user_name", "N/A")
                course_name = payload.get("course", {}).get("course_title", "N/A")
                cert_filename = payload.get("certificate", {}).get("filename", "")
                has_certificate = "Sim" if cert_filename else "Não"

                processed_results.append(
                    {
                        "id": task["id"],
                        "student_name": student_name,
                        "course_name": course_name,
                        "has_certificate": has_certificate,
                        "cert_filename": cert_filename,
                        "payload": task["payload"],
                        "attempts": task["attempts"],
                        "updated_at": task["updated_at"],
                    }
                )
            except (json.JSONDecodeError, KeyError) as e:
                # If JSON processing fails, keep original data.
                print(f"[Queue] Error processing payload for task {task['id']}: {e}")
                processed_results.append(
                    {
                        "id": task["id"],
                        "student_name": "Proccess Error",
                        "course_name": "Proccess Error",
                        "has_certificate": "N/A",
                        "cert_filename": "",
                        "payload": task["payload"],
                        "attempts": task["attempts"],
                        "updated_at": task["updated_at"],
                    }
                )

        print(f"[Queue] Found {len(results)} failed tasks.")

        cursor.close()
        return processed_results

    def get_certificate_usage(self):
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(MONITORING_QUERIES["certificate_usage"])
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_recent_activity(self, days=24):
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        hours = days * 24
        cursor.execute(MONITORING_QUERIES["recent_activity"], {"hours": hours})
        results = cursor.fetchall()
        cursor.close()
        return results

    def check_data_integrity(self):
        """Check data integrity"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        integrity_checks = {}

        for check_name, query in MONITORING_QUERIES["integrity_checks"].items():
            cursor.execute(query)
            result = cursor.fetchone()

            # Get the first value from the returned dictionary.
            if result:
                integrity_checks[check_name] = list(result.values())[0]
            else:
                integrity_checks[check_name] = 0

        cursor.close()
        return integrity_checks
