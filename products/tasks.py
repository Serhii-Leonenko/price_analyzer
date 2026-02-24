from celery import shared_task


@shared_task
def import_all_products():
    from products.services import ProductImportService

    return ProductImportService().execute()
