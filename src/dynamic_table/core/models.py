from typing import Iterator, List, Set

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from django.db.models import TextChoices


class DynamicTable(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        db_table = "dynamic_table"

    def get_model_class(self):
        attrs = {'__module__': self.__module__}
        for field_data in self.fields.all():
            field_class = DynamicField.get_field_type_map().get(field_data.field_type)
            attrs[field_data.field_name] = field_class
        dynamic_model = type(self.title, (models.Model,), attrs)
        app_label = self._meta.app_label
        dynamic_model._meta.app_label = app_label

        app_config = apps.get_app_config(app_label)
        app_config.models[self.title] = dynamic_model
        app_config.models_module.__setattr__(self.title, dynamic_model)
        return dynamic_model

    def update_model(self, app_config):
        model: models.base.ModelBase = app_config.models.get(self.title.lower())
        model_field_names: Set[str] = set(map(lambda field: field.name, model._meta.fields))

        for field_data in self.fields.all():
            field_class: models.Field = DynamicField.get_field_type_map().get(field_data. field_type)
            field_class.column = field_data.field_name
            with connection.schema_editor() as schema_editor:
                if field_data.field_name not in model_field_names:
                    schema_editor.add_field(model, field_class)
                    model.add_to_class(field_data.field_name, field_class)
                else:
                    schema_editor.alter_field(model, model._meta.get_field(field_data.field_name), field_class)

    def create_model(self):
        model_class = self.get_model_class()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model_class)
            ContentType.objects.create(app_label=self._meta.app_label, model=model_class._meta.model_name)

    def create_or_update_model(self):
        app_label = self._meta.app_label
        app_config = apps.get_app_config(app_label)
        if self.title.lower() in app_config.models:
            self.update_model(app_config)
        else:
            self.create_model()


class DynamicFieldType(TextChoices):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


class DynamicField(models.Model):
    table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name="fields")
    field_name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=255, choices=DynamicFieldType.choices)

    class Meta:
        db_table = "dynamic_field"

    @staticmethod
    def get_field_type_map():
        return {
            'string': models.CharField(max_length=255, blank=True, null=True),
            'number': models.IntegerField(blank=True, null=True),
            'boolean': models.BooleanField(blank=True, null=True),
        }


class DynamicTableModel(models.Model):
    dynamic_table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name='dynamic_rows')
    dynamic_fields = models.JSONField(default=dict)

    def create_dynamic_model_instance(self, row_data):
        model_class = self.dynamic_table.get_model_class()
        instance = model_class()
        for field_name, value in row_data.items():
            setattr(instance, field_name, value)
        instance.save()
        return instance

    class Meta:
        db_table = "dynamic_model"
