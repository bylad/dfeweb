# Generated by Django 3.1.3 on 2022-01-20 11:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsHead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news_title', models.CharField(max_length=256)),
                ('href', models.CharField(max_length=256)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('subsidy_period', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SubsidyData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subsidy_name', models.CharField(max_length=256)),
                ('subsidy_value', models.FloatField()),
                ('newshead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subsidies', to='subsidy.newshead')),
            ],
        ),
        migrations.CreateModel(
            name='BenefitData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('benefit_name', models.CharField(max_length=256)),
                ('benefit_value', models.FloatField()),
                ('newshead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='benefits', to='subsidy.newshead')),
            ],
        ),
    ]
