import os


def premier_product_image_path(instance, filename):
    return os.path.join(
        'premier',
        instance.manufacturer.vendor.slug,
        'product',
        'images',
        filename
    )


def premier_manufacturer_image_path(instance, filename):
    return os.path.join(
        'premier',
        instance.vendor.slug,
        'manufacturer',
        'images',
        filename
    )
