import json
import os

import pymysql
from dotenv import load_dotenv

from config.config import DB_CONFIG
from config.queries import MONITORING_QUERIES
from utils.ssh_client import SSHTunnel

load_dotenv()

prefix = os.getenv("DB_PREFIX")


class MySQLMonitor:
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

    def get_failure_details(self, task_id):
        """Get detailed information about a failed task"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Get task info.
        cursor.execute(f"SELECT * FROM {prefix}tasks_queue WHERE id = %s", (task_id,))
        task = cursor.fetchone()

        if not task:
            cursor.close()
            return {"error": "Task not found"}

        # Parse payload.
        payload = json.loads(task["payload"]) if task["payload"] else {}

        # Extract user_id and course_id from payload.
        user_id = payload.get("signer", {}).get("user_id")
        course_id = payload.get("course", {}).get("course_id")

        result = {"certificate": None, "user_metadata": None, "payload": payload}

        # Get certificate info.
        if user_id and course_id:
            cursor.execute(
                f"""
                SELECT * FROM {prefix}certificates
                WHERE user_id = %s AND course_id = %s
                ORDER BY created_at DESC LIMIT 1
                """,
                (user_id, course_id),
            )
            cert = cursor.fetchone()
            if cert:
                result["certificate"] = {
                    "id": cert["id"],
                    "template_id": cert["template_id"],
                    "student_id": cert["student_id"],
                    "user_id": cert["user_id"],
                    "course_id": cert["course_id"],
                    "completed_on": (
                        cert["completed_on"].strftime("%d/%m/%Y %H:%M")
                        if cert["completed_on"]
                        else None
                    ),
                    "expiration": cert["expiration"],
                    "pdf_url": cert["pdf_url"],
                    "platform_data": cert["platform_data"],
                    "status": cert["status"],
                    "created_at": (
                        cert["created_at"].strftime("%d/%m/%Y %H:%M")
                        if cert["created_at"]
                        else None
                    ),
                    "updated_at": (
                        cert["updated_at"].strftime("%d/%m/%Y %H:%M")
                        if cert["updated_at"]
                        else None
                    ),
                }

                # Parse platform_data if exists.
                if cert["platform_data"]:
                    try:
                        result["certificate"]["platform_data"] = json.loads(
                            cert["platform_data"]
                        )
                    except:
                        result["certificate"]["platform_data"] = cert["platform_data"]

            # Get user metadata.
            cursor.execute(
                f"""
                SELECT meta_value FROM wp_usermeta
                WHERE user_id = %s AND meta_key = %s
                """,
                (user_id, f"_ldcds_certificate_{course_id}"),
            )
            metadata = cursor.fetchone()
            if metadata and metadata["meta_value"]:
                try:
                    result["user_metadata"] = json.loads(metadata["meta_value"])
                except:
                    result["user_metadata"] = metadata["meta_value"]

        cursor.close()
        return result

    def get_certificate_details(self, cert_id):
        """Get detailed information about a certificate"""
        conn = self._get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Get certificate info.
        cursor.execute(
            f"""
            SELECT * FROM {prefix}certificates
            WHERE id = %s
            """,
            (cert_id,),
        )
        cert = cursor.fetchone()

        if not cert:
            cursor.close()
            return {"error": "Certificate not found"}

        result = {"certificate": None, "student": None, "course": None}

        # Format certificate data.
        result["certificate"] = {
            "id": cert["id"],
            "template_id": cert["template_id"],
            "student_id": cert["student_id"],
            "user_id": cert["user_id"],
            "course_id": cert["course_id"],
            "completed_on": (
                cert["completed_on"].strftime("%d/%m/%Y %H:%M")
                if cert["completed_on"]
                else None
            ),
            "expiration": cert["expiration"],
            "pdf_url": cert["pdf_url"],
            "platform_data": cert["platform_data"],
            "status": cert["status"],
            "created_at": (
                cert["created_at"].strftime("%d/%m/%Y %H:%M")
                if cert["created_at"]
                else None
            ),
            "updated_at": (
                cert["updated_at"].strftime("%d/%m/%Y %H:%M")
                if cert["updated_at"]
                else None
            ),
        }

        # Parse platform_data if exists.
        if cert["platform_data"]:
            try:
                result["certificate"]["platform_data"] = json.loads(
                    cert["platform_data"]
                )
            except:
                result["certificate"]["platform_data"] = cert["platform_data"]

        # Get student info.
        cursor.execute(
            f"""
            SELECT * FROM {prefix}students
            WHERE id = %s
            """,
            (cert["student_id"],),
        )
        student = cursor.fetchone()
        if student:
            result["student"] = {
                "id": student["id"],
                "name": student["name"],
                "email": student["email"],
                "cpf": student["cpf"],
                "phone": student["phone"],
                "position": student["position"],
                "sector": student["sector"],
                "created_at": (
                    student["created_at"].strftime("%d/%m/%Y %H:%M")
                    if student["created_at"]
                    else None
                ),
            }

        # Get course info.
        cursor.execute(
            f"""
            SELECT ID, post_title, post_name, post_status
            FROM wp_posts
            WHERE ID = %s AND post_type = 'sfwd-courses'
            """,
            (cert["course_id"],),
        )
        course = cursor.fetchone()
        if course:
            result["course"] = {
                "id": course["ID"],
                "title": course["post_title"],
                "slug": course["post_name"],
                "status": course["post_status"],
            }

        cursor.close()
        return result
