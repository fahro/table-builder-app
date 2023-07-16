from django.db.transaction import atomic
from rest_framework import serializers
from dynamic_table.core.models import DynamicTable, DynamicField, DynamicTableModel


class DynamicFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicField
        fields = ['field_name', 'field_type']


class DynamicTableSerializer(serializers.ModelSerializer):
    fields = DynamicFieldSerializer(many=True, read_only=True)

    class Meta:
        model = DynamicTable
        fields = ['id', 'title', 'fields']


class DynamicTableCreateSerializer(serializers.ModelSerializer):
    fields = DynamicFieldSerializer(many=True)

    class Meta:
        model = DynamicTable
        fields = ['id', 'title', 'fields']

    @atomic
    def create(self, validated_data):
        fields_data = validated_data.pop('fields')
        table = DynamicTable.objects.create(**validated_data)

        for field_data in fields_data:
            DynamicField.objects.create(table=table, **field_data)
        table.create_or_update_model()
        return table


class DynamicTableUpdateSerializer(serializers.ModelSerializer):
    fields = DynamicFieldSerializer(many=True)

    class Meta:
        model = DynamicTable
        fields = ['id', 'fields']

    @atomic
    def update(self, instance, validated_data):
        fields_data = validated_data.get('fields')
        if fields_data:
            instance.fields.all().delete()
            for field_data in fields_data:
                DynamicField.objects.create(table=instance, **field_data)
            instance.create_or_update_model()
        return instance


class DynamicTableRowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicTableModel
        fields = ['dynamic_fields']


class DynamicTableRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = '__all__'
