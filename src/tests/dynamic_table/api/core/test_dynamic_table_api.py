from django.db.models import CharField, IntegerField, BooleanField
from django.test import TestCase
from rest_framework.test import APIClient

from dynamic_table.core.models import DynamicTable, DynamicField, DynamicFieldType
from tests.dynamic_table.api.api_helper import APIHelper


class TestDynamicTableAPI(APIHelper, TestCase):
    def test__create_dynamic_table(self):
        client = APIClient()
        resp = client.post(
            self.table_create_url,
            {
                "title": "TableTestCreate",
                "fields": [
                    {
                        "field_name": "name",
                        "field_type": "string"
                    },
                    {
                        "field_name": "active",
                        "field_type": "boolean"
                    },
                    {
                        "field_name": "likes",
                        "field_type": "number"
                    }
                ]
            },
            format='json'
        )
        self.is_created(resp)
        self.assertEqual(
            DynamicTable.objects.count(),
            1
        )
        self.assertEqual(DynamicTable.objects.first().title, "TableTestCreate")
        self.assertEqual(
            DynamicField.objects.get(table=DynamicTable.objects.first(), field_type=DynamicFieldType.STRING).field_name,
            "name"
        )
        self.assertEqual(
            DynamicField.objects.get(table=DynamicTable.objects.first(), field_type=DynamicFieldType.BOOLEAN).field_name,
            "active"
        )
        self.assertEqual(
            DynamicField.objects.get(table=DynamicTable.objects.first(), field_type=DynamicFieldType.NUMBER).field_name,
            "likes"
        )

        # TEST MODEL CREATED
        from django.apps import apps
        TableTestCreate = apps.get_model(app_label="core", model_name="TableTestCreate")
        self.assertEqual(
            list(map(lambda field: field.name, TableTestCreate._meta.fields)),
            ["id", "name", "active", "likes"]
        )
        self.assertEqual(
            type(TableTestCreate._meta.get_field("name")),
            CharField
        )
        self.assertEqual(
            type(TableTestCreate._meta.get_field("likes")),
            IntegerField,
        )
        self.assertEqual(
            type(TableTestCreate._meta.get_field("active")),
            BooleanField,
        )

    def test__table_retrieve_api(self):
        client = APIClient()
        table_title = "TableTestRetrieve"
        field_name = "name"
        field_type = "string"

        dynamic_table = DynamicTable.objects.create(
            title=table_title
        )
        DynamicField.objects.create(table=dynamic_table, field_name=field_name, field_type=field_type)
        resp = client.get(
            self.get_dynamic_table_detail_url(dynamic_table.pk),
        )
        self.is_success(resp)
        self.assertEqual(
            dynamic_table.title,
            table_title
        )
        self.assertEqual(
            dynamic_table.fields.first().field_name,
            field_name
        )
        self.assertEqual(
            dynamic_table.fields.first().field_type,
            DynamicFieldType.STRING
        )

    def test__update_dynamic_table(self):
        client = APIClient()
        table_title = "TableTestUpdate"
        string_field_name = "name"
        string_field_type = "string"

        number_field_name = "year"
        number_field_type = "number"

        boolean_field_name = "verified"
        boolean_field_type = "boolean"

        resp = client.post(
            self.table_create_url,
            {
                "title": table_title,
                "fields": [
                    {
                        "field_name": string_field_name,
                        "field_type": string_field_type
                    }
                ]
            },
            format='json'
        )
        self.is_created(resp)

        table_id = resp.json().get("id")
        resp = client.put(
            self.get_dynamic_table_detail_url(table_id),
            {
                "fields": [
                    {
                        "field_name": string_field_name,
                        "field_type": string_field_type
                    },
                    {
                        "field_name": number_field_name,
                        "field_type": number_field_type
                    },
                    {
                        "field_name": boolean_field_name,
                        "field_type": boolean_field_type
                    }
                ]
            },
            format='json'
        )
        self.is_success(resp)
        dynamic_table = DynamicTable.objects.get(id=table_id)
        fields = DynamicField.objects.filter(table=dynamic_table)
        self.assertEqual(
            fields.count(),
            3
        )

        # TEST MODEL UPDATED
        from django.apps import apps
        TableTestUpdate = apps.get_model(app_label="core", model_name="TableTestUpdate")

        self.assertEqual(
            list(map(lambda field: field.name, TableTestUpdate._meta.fields)),
            ["id", "name", "year", "verified"]
        )
        self.assertEqual(
            type(TableTestUpdate._meta.get_field(number_field_name)),
            IntegerField
        )
        self.assertEqual(
            type(TableTestUpdate._meta.get_field(boolean_field_name)),
            BooleanField
        )


class TestDynamicTableRowAPI(APIHelper, TestCase):
    def test_table_row(self):
        client = APIClient()

        # Create a table, fields and Model
        table_resp = client.post(
            self.table_create_url,
            {
                "title": "PersonTest",
                "fields": [
                    {
                        "field_name": "name",
                        "field_type": "string"
                    },
                    {
                        "field_name": "DOB",
                        "field_type": "number"
                    },
                    {
                        "field_name": "verified",
                        "field_type": "boolean"
                    }
                ]
            },
            format='json'
        )
        self.is_created(table_resp)
        self.assertEqual(
            DynamicTable.objects.count(),
            1
        )
        self.table_id = table_resp.json().get("id")

        # TEST MODEL CREATED
        from django.apps import apps
        PersonTest = apps.get_model(app_label="core", model_name="PersonTest")
        self.assertEqual(
            list(map(lambda field: field.name, PersonTest._meta.fields)),
            ["id", "name", "DOB", "verified"]
        )
        self.assertEqual(
            type(PersonTest._meta.get_field("name")),
            CharField
        )
        self.assertEqual(
            type(PersonTest._meta.get_field("DOB")),
            IntegerField,
        )
        self.assertEqual(
            type(PersonTest._meta.get_field("verified")),
            BooleanField,
        )

        # Add new row
        resp = client.post(
            self.get_row_create_url(self.table_id),
            {
                "dynamic_fields": {
                    "name": "John",
                    "DOB": 1984,
                    "verified": True,
                }
            },
            format='json'
        )
        self.is_created(resp)

        self.assertEqual(
            PersonTest.objects.count(),
            1
        )
        person = PersonTest.objects.first()
        self.assertEqual(
            person.name,
            "John"
        )
        self.assertEqual(
            person.DOB,
            1984
        )
        self.assertTrue(person.verified)

        # Table rows retrieve
        resp = client.get(
            self.get_rows_url(self.table_id)
        )
        self.is_success(resp)
        self.assertEqual(
            type(resp.json()),
            list
        )
        self.assertEqual(
            len(resp.json()),
            1
        )
