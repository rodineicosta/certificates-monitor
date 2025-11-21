import time
import pymysql
import sshtunnel

from config.config import DB_CONFIG, SSH_CONFIG


class SSHTunnel:
    def __init__(self):
        self.tunnel = None

    def __enter__(self):
        print(f"[SSH] Connecting to {SSH_CONFIG['hostname']}:{SSH_CONFIG['port']}")
        print(f"[SSH] User: {SSH_CONFIG['username']}")

        self.tunnel = sshtunnel.SSHTunnelForwarder(
            (SSH_CONFIG["hostname"], SSH_CONFIG["port"]),
            ssh_username=SSH_CONFIG["username"],
            ssh_password=SSH_CONFIG["password"],
            allow_agent=False,
            host_pkey_directories=[],
            remote_bind_address=("127.0.0.1", 3306),
        )

        self.tunnel.start()
        time.sleep(2)

        if self.tunnel.is_active:
            print(f"[SSH] Tunnel active! Local port: {self.tunnel.local_bind_port}")
        else:
            print("[SSH] ERROR: Tunnel is not active!")
            raise Exception("SSH Tunnel is not active!")

        return self.tunnel

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tunnel:
            print("[SSH] Closing tunnel...")
            self.tunnel.stop()


    def get_db_connection():
        print("[DB] Starting database connection...")

        with SSHTunnel() as tunnel:
            print(f"[DB] Connecting to localhost:{tunnel.local_bind_port}")
            print(f"[DB] Database: {DB_CONFIG['database']}")
            print(f"[DB] User: {DB_CONFIG['username']}")

            connection = pymysql.connect(
                host=DB_CONFIG["host"],
                port=tunnel.local_bind_port,
                user=DB_CONFIG["username"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                charset="utf8mb4",
                connect_timeout=10,
            )

            print("[DB] Connection established successfully!")
            return connection

    def read_log_file(self, log_path, lines=200, filter_text=None):
        """
        Reads log file via SSH

        Args:
            log_path: Path to the file on the server
            lines: Number of lines to read (from the end of the file)
            filter_text: Text to filter (optional)

        Returns:
            List of log lines
        """
        try:
            if filter_text:
                # Command to filter and get the last N lines.
                command = f"grep '{filter_text}' {log_path} | tail -n {lines}"
            else:
                # Just the last N lines.
                command = f"tail -n {lines} {log_path}"

            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            if error:
                print(f"[SSH] Error reading log: {error}.")
                return []

            return output.splitlines() if output else []

        except Exception as e:
            print(f"[SSH] Error executing command: {e}")
            return []

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connections"""
        if self.tunnel:
            self.tunnel.stop()
        if self.ssh:
            self.ssh.close()
        print("[SSH] Connection closed.")
