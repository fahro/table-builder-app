from django.urls import reverse


class ReversedUrl:
    table_create_url = reverse('dynamic-table-list')

    @classmethod
    def get_dynamic_table_detail_url(cls, pk):
        return reverse('dynamic-table-detail', kwargs={'pk': pk})

    @classmethod
    def get_row_create_url(cls, pk):
        return reverse('dynamic-table-row-list', kwargs={'id': pk})

    @classmethod
    def get_rows_url(cls, pk):
        return reverse('dynamic-table-rows-list', kwargs={'id': pk})
