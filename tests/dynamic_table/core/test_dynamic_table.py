from django.apps import apps
from django.db.models import base
from django.test import TestCase

from dynamic_table.core.models import DynamicTable, DynamicField, DynamicFieldType


class TestDynamicTable(TestCase):
    def test_get_model_class(self):
        app_label = "core"
        model_name = "TableSample"
        table = DynamicTable.objects.create(title=model_name)
        model_class = table.get_model_class()
        self.assertEqual(type(model_class), base.ModelBase)

        model = apps.get_model(app_label=app_label, model_name=model_name)

        expected_table_name = f'{app_label}_{model_name.lower()}'
        self.assertEqual(model._meta.db_table, expected_table_name)
        fields = map(lambda field: field.name, model._meta.fields)
        self.assertTrue("id" in fields)

    def test_create_model(self):
        app_label = "core"
        model_name = "Person"
        name = "John"

        table = DynamicTable.objects.create(title=model_name)
        DynamicField.objects.create(table=table, field_name="name", field_type=DynamicFieldType.STRING)
        table.create_model()

        Person = apps.get_model(app_label=app_label, model_name=model_name)
        person = Person.objects.create(name=name)
        self.assertEqual(
            Person.objects.count(),
            1
        )
        self.assertEqual(person.name, name)

    def test_update_model(self):
        app_label = "core"
        model_name = "Car"
        fuel = "diesel"
        year = 2023

        table = DynamicTable.objects.create(title=model_name)
        DynamicField.objects.create(table=table, field_name="fuel", field_type=DynamicFieldType.STRING)
        table.create_model()

        Car = apps.get_model(app_label=app_label, model_name=model_name)
        car = Car.objects.create(fuel=fuel)
        self.assertEqual(
            Car.objects.count(),
            1
        )
        self.assertEqual(car.fuel, fuel)

        DynamicField.objects.create(table=table, field_name="year", field_type=DynamicFieldType.NUMBER)
        app_config = apps.get_app_config(app_label)
        table.update_model(app_config)

        UpdatedCar = apps.get_model(app_label=app_label, model_name=model_name)
        car = UpdatedCar.objects.first()
        car.year = year
        car.save()

        self.assertEqual(
            UpdatedCar.objects.first().fuel,
            fuel
        )
        self.assertEqual(
            UpdatedCar.objects.first().year,
            year
        )
