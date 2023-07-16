from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import atomic
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from dynamic_table.core.models import DynamicTable, DynamicTableModel
from dynamic_table.api.core.serializers import DynamicTableSerializer, DynamicTableRowSerializer, \
    DynamicTableCreateSerializer, DynamicTableUpdateSerializer, DynamicTableRowCreateSerializer


class DynamicTableViewSet(mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          GenericViewSet):
    queryset = DynamicTable.objects.all()
    serializer_class = DynamicTableSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return DynamicTableCreateSerializer
        elif self.action == 'update':
            return DynamicTableUpdateSerializer
        else:
            return self.serializer_class


class DynamicTableRowCreateViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = DynamicTableModel.objects.all()
    serializer_class = DynamicTableRowCreateSerializer

    @atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dynamic_table = DynamicTable.objects.get(pk=kwargs['id'])
        instance = serializer.save(dynamic_table=dynamic_table)
        model = instance.create_dynamic_model_instance(serializer.validated_data['dynamic_fields'])
        DynamicTableRowSerializer.Meta.model = model
        instance_serializer = DynamicTableRowSerializer(model)
        return Response(instance_serializer.data, status=status.HTTP_201_CREATED)


class DynamicTableRowListViewSet(mixins.ListModelMixin, GenericViewSet):
    @property
    def model(self):
        model_title = DynamicTable.objects.get(pk=self.kwargs['id']).title
        app_label = ContentType.objects.get(model=model_title.lower()).app_label
        return apps.get_model(app_label=app_label, model_name=model_title)

    def get_queryset(self):
        return self.model.objects.all()

    def get_serializer_class(self):
        DynamicTableRowSerializer.Meta.model = self.model
        return DynamicTableRowSerializer
