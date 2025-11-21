import os
from dotenv import load_dotenv

load_dotenv()

prefix = os.getenv("DB_PREFIX")

MONITORING_QUERIES = {
    "table_sizes": f"""
        SELECT
            table_name AS 'Tabela',
            ROUND((data_length + index_length) / 1024 / 1024, 2) AS 'Tamanho (MB)'
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name LIKE '{prefix}%'
        ORDER BY (data_length + index_length) DESC
    """,
    "certificates": f"""
        SELECT
            c.id,
            c.student_id,
            c.course_id,
            s.name as student_name,
            p.post_title as course_name,
            c.status,
            c.created_at
        FROM {prefix}certificates c
        LEFT JOIN {prefix}students s ON c.student_id = s.id
        LEFT JOIN wp_posts p ON c.course_id = p.ID AND p.post_type = 'sfwd-courses'
        ORDER BY c.created_at DESC
    """,
    "recent_certificates": f"""
        SELECT
            c.id,
            c.student_id,
            c.course_id,
            s.name as student_name,
            p.post_title as course_name,
            c.status,
            c.created_at
        FROM {prefix}certificates c
        LEFT JOIN {prefix}students s ON c.student_id = s.id
        LEFT JOIN wp_posts p ON c.course_id = p.ID AND p.post_type = 'sfwd-courses'
        WHERE c.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        ORDER BY c.created_at DESC
    """,
    "failed_queue_tasks": f"""
        SELECT *
        FROM {prefix}tasks_queue
        WHERE status = 'failed'
        ORDER BY updated_at DESC
    """,
    "total_counts": f"""
        SELECT
            (SELECT COUNT(*) FROM {prefix}certificates) as total_certificates,
            (SELECT COUNT(*) FROM {prefix}students) as total_students,
            (SELECT COUNT(*) FROM {prefix}team_members) as total_team_members,
            (SELECT COUNT(*) FROM {prefix}tasks_queue WHERE status = 'failed') as total_failed_tasks
    """,
    "certificates_by_day": f"""
        WITH RECURSIVE dates AS (
            SELECT CONVERT_TZ(NOW(), '+00:00', '-03:00') - INTERVAL 6 DAY as date
            UNION ALL
            SELECT date + INTERVAL 1 DAY
            FROM dates
            WHERE date < DATE(CONVERT_TZ(NOW(), '+00:00', '-03:00'))
        )
        SELECT
            DATE(d.date) as date,
            COALESCE(COUNT(c.id), 0) as count
        FROM dates d
        LEFT JOIN {prefix}certificates c ON DATE(CONVERT_TZ(c.created_at, '+00:00', '-03:00')) = DATE(d.date)
        GROUP BY DATE(d.date)
        ORDER BY DATE(d.date) ASC
    """,
    "certificate_usage": f"""
        SELECT
            status,
            COUNT(*) as count,
            DATE(created_at) as date
        FROM {prefix}certificates
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY status, DATE(created_at)
        ORDER BY date DESC
    """,
    "recent_activity": f"""
        SELECT
            'Certificados' as tipo,
            COUNT(*) as quantidade
        FROM {prefix}certificates
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL %(hours)s HOUR)

        UNION ALL

        SELECT
            'Templates' as tipo,
            COUNT(*) as quantidade
        FROM {prefix}certificate_templates
        WHERE updated_at >= DATE_SUB(NOW(), INTERVAL %(hours)s HOUR)
    """,
    "integrity_checks": {
        "certificados_sem_template": f"""
            SELECT COUNT(*)
            FROM {prefix}certificates c
            LEFT JOIN {prefix}certificate_templates t ON c.template_id = t.id
            WHERE t.id IS NULL
        """,
        "templates_invalidos": f"""
            SELECT COUNT(*)
            FROM {prefix}certificate_templates
            WHERE template_config IS NULL OR template_config = ''
        """,
    },
}
