# Generated by Django 3.1.3 on 2020-11-27 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IndustryNews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('href', models.CharField(max_length=256)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='IndustryProductionHead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cur_year', models.CharField(max_length=50)),
                ('pre_cur', models.CharField(max_length=150)),
                ('industrynews', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_head', to='industry.industrynews')),
            ],
        ),
        migrations.CreateModel(
            name='IndustryProduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry_production', models.CharField(max_length=256)),
                ('cur_year_production', models.FloatField(verbose_name='current')),
                ('pre_cur_production', models.FloatField(verbose_name='preceed-current')),
                ('industrynews', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production', to='industry.industrynews')),
            ],
        ),
        migrations.CreateModel(
            name='IndustryIndexHead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_year', models.CharField(max_length=150)),
                ('pre_year', models.CharField(max_length=50)),
                ('cur_year', models.CharField(max_length=50)),
                ('pre_cur', models.CharField(max_length=150)),
                ('industrynews', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='index_head', to='industry.industrynews')),
            ],
        ),
        migrations.CreateModel(
            name='IndustryIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production_index', models.CharField(max_length=256)),
                ('pre_year_index', models.FloatField(verbose_name='preceed')),
                ('cur_year_index', models.FloatField(verbose_name='current')),
                ('pre_cur_index', models.FloatField(verbose_name='preceed-current')),
                ('industrynews', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news', to='industry.industrynews')),
            ],
        ),
    ]
