# Generated by Django 2.2.4 on 2019-09-03 13:43

from django.db import migrations, models


def delete_history(apps, schema_editor):
    History = apps.get_model("core", "History")
    HistoryData = apps.get_model("core", "HistoryData")
    History.objects.all().delete()
    HistoryData.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [("core", "0025_projector_color")]

    operations = [
        migrations.RunPython(delete_history),
    ]
