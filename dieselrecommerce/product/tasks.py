from .models import *


def retrieve_sema_api_data():
    models = [
        SemaBrand,
        SemaDataset,
        SemaYear,
        SemaMake,
        SemaModel,
        SemaSubmodel,
        SemaMakeYear,
        SemaBaseVehicle,
        SemaVehicle,
        SemaCategory,
        SemaProduct
    ]

    data = {}
    errors = []
    for index, model in enumerate(models, start=1):
        print(f'{index}. Retrieving {model._meta.verbose_name.title()}...')
        try:
            _data = model.objects.get_api_data()
            data[model._meta.verbose_name] = _data
        except Exception as err:
            errors.append(f'Internal Error: {err}')
            print('   errored')
            continue
        print('   complete')

    return data, errors


def perform_sema_api_import_unauthorize_and_update():
    models = [
        SemaBrand,
        SemaDataset,
        SemaYear,
        SemaMake,
        SemaModel,
        SemaSubmodel,
        SemaMakeYear,
        SemaBaseVehicle,
        SemaVehicle,
        SemaCategory,
        SemaProduct
    ]

    msgs = []
    for index, model in enumerate(models, start=1):
        print(f'{index}. Syncing {model._meta.verbose_name.title()}...')
        try:
            _msgs = model.objects.import_and_unauthorize_from_api()
            msgs += _msgs
        except Exception as err:
            msgs.append(f'Internal Error: {err}')
            print('   errored')
            continue
        print('   complete')

    print('A. Updating product categories...')
    categories = SemaCategory.objects.filter(is_authorized=True)
    msgs += categories.perform_product_category_update()
    print('   complete')

    print('B. Updating product vehicles...')
    brands = SemaBrand.objects.filter(is_authorized=True)
    msgs += brands.perform_product_vehicle_update()
    print('   complete')

    info = [msg for msg in msgs if msg[:4] == 'Info']
    success = [msg for msg in msgs if msg[:7] == 'Success']
    error = [
        msg for msg in msgs
        if not msg[:4] == 'Info'
        and not msg[:7] == 'Success'
    ]
    return msgs, info, success, error


sema_sync = perform_sema_api_import_unauthorize_and_update
sema_data = retrieve_sema_api_data
