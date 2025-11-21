from utils.ssh_client import get_db_connection

class DatabaseModel:
    """Base Class for Database Models"""

    def __init__(self):
        self.connection = get_db_connection()

    def execute_query(self, query, params=None):
        """Executes a query and returns results"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e

    def close(self):
        """Closes the connection"""
        if self.connection:
            self.connection.close()

class CertificateModel(DatabaseModel):
    """Model for certificates table"""

    def get_all_certificates(self, limit=100):
        query = """
            SELECT * FROM wp_ldcds_certificates
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))

    def get_certificate_stats(self):
        query = """
            SELECT
                status,
                COUNT(*) as total,
                DATE(created_at) as date
            FROM wp_ldcds_certificates
            GROUP BY status, DATE(created_at)
            ORDER BY date DESC
        """
        return self.execute_query(query)

    def find_certificates_by_user(self, user_id):
        query = """
            SELECT * FROM wp_ldcds_certificates
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        return self.execute_query(query, (user_id,))

class TemplateModel(DatabaseModel):
    """Model for templates table"""

    def get_active_templates(self):
        query = """
            SELECT * FROM wp_ldcds_templates
            WHERE status = 'active'
            ORDER BY name
        """
        return self.execute_query(query)

    def get_template_usage(self):
        query = """
            SELECT
                t.id,
                t.name,
                COUNT(c.id) as usage_count
            FROM wp_ldcds_templates t
            LEFT JOIN wp_ldcds_certificates c ON t.id = c.template_id
            GROUP BY t.id, t.name
            ORDER BY usage_count DESC
        """
        return self.execute_query(query)

class MonitorModel(DatabaseModel):
    """Model specific for monitoring"""

    def get_database_size(self):
        query = """
            SELECT
                table_schema as database_name,
                SUM(data_length + index_length) / 1024 / 1024 as size_mb
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            GROUP BY table_schema
        """
        return self.execute_query(query)

    def get_table_info(self):
        query = """
            SELECT
                table_name,
                table_rows,
                ROUND((data_length + index_length) / 1024 / 1024, 2) as size_mb,
                UPDATE_TIME as last_update
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name LIKE 'wp_ldcds_%'
            ORDER BY table_rows DESC
        """
        return self.execute_query(query)