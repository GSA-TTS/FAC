from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0018_auditflow_rename_audit_history_event_data_and_more"),
    ]

    operations = [
        # This custom function is needed for the generated columns.
        # Updating it to use jsonb_array_elements_text instead of
        # jsonb_array_elements to fix double quotes issue.
        migrations.RunSQL("""
                    CREATE OR REPLACE FUNCTION json_array_to_text_array (data jsonb)
                        RETURNS text[]
                        AS $CODE$
                    BEGIN
                        RETURN ARRAY (
                            SELECT
                                jsonb_array_elements_text(data));
                    END
                    $CODE$
                    LANGUAGE plpgsql
                    IMMUTABLE;
            """),
    ]
