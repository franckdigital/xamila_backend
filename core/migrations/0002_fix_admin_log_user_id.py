# Generated migration to fix django_admin_log user_id column type
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('admin', '0003_logentry_add_action_flag_choices'),
    ]

    operations = [
        # 1. Supprimer la contrainte de clé étrangère
        migrations.RunSQL(
            "ALTER TABLE django_admin_log DROP FOREIGN KEY django_admin_log_user_id_c564eba6_fk_auth_user_id;",
            reverse_sql="ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user (id);"
        ),
        
        # 2. Modifier le type de colonne user_id pour accepter les UUID
        migrations.RunSQL(
            "ALTER TABLE django_admin_log MODIFY COLUMN user_id CHAR(36);",
            reverse_sql="ALTER TABLE django_admin_log MODIFY COLUMN user_id INT(11);"
        ),
        
        # 3. Recréer la contrainte de clé étrangère avec la table core_user
        migrations.RunSQL(
            "ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fk_core_user FOREIGN KEY (user_id) REFERENCES core_user (id);",
            reverse_sql="ALTER TABLE django_admin_log DROP FOREIGN KEY django_admin_log_user_id_fk_core_user;"
        ),
    ]
