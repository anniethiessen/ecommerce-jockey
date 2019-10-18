from .models import *


def perform_sema_api_import_and_unauthorize():
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

    info = [msg for msg in msgs if msg[:4] == 'Info']
    success = [msg for msg in msgs if msg[:7] == 'Success']
    error = [
        msg for msg in msgs
        if not msg[:4] == 'Info'
        and not msg[:7] == 'Success'
    ]
    return msgs, info, success, error


sema_sync = perform_sema_api_import_and_unauthorize
