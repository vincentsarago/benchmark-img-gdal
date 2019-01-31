import timeit
from io import BytesIO

import numpy

from rasterio.io import MemoryFile

from rio_tiler import main
from rio_tiler import utils


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def img_to_buffer(img, tileformat):
    if tileformat == "jpeg":
        img = img.convert("RGB")

    sio = BytesIO()
    img.save(sio, tileformat.upper())
    sio.seek(0)
    return sio.getvalue()


def array_to_img_pil(ext):
    img = utils.array_to_img(tile, mask=mask)
    img_format = "JPEG2000" if ext == "jp2" else ext
    return img_to_buffer(img, img_format)


def array_to_img_rio(img_format):
    """Create image buffer from array."""
    img = tile

    # WEBP doesn't support 1band dataset so we must hack to create a RGB dataset
    if img_format == "webp" and img.shape[0] == 1:
        img = numpy.repeat(img, 3, axis=0)

    if mask is not None and img_format != "jpeg":
        nbands = img.shape[0] + 1
    else:
        nbands = img.shape[0]

    if img_format == "jp2":
        img_format = "JP2OpenJPEG"

    output_profile = dict(
        driver=img_format,
        dtype=img.dtype,
        count=nbands,
        height=img.shape[1],
        width=img.shape[2]
    )

    with MemoryFile() as memfile:
        with memfile.open(**output_profile) as dst:
            dst.write(img, indexes=list(range(1, img.shape[0] + 1)))
            # Use Mask as an alpha band
            if mask is not None and img_format != "jpeg":
                dst.write(mask.astype(numpy.uint8), indexes=nbands)

        return memfile.read()


if __name__ == '__main__':
    tile, mask = main.tile(
        "/tmp/RGB_cogeo.tif",
        14824,
        7506,
        14,
        indexes=(1, 2, 3),
        tilesize=512
    )

    def _ti(ty, img_format, number, repeat):
        t = timeit.Timer(
            f"array_to_img_{ty}('{img_format}')",
            setup=f"from __main__ import array_to_img_{ty}"
        )
        times = t.repeat(repeat=repeat, number=number)
        return min(times), max(times), sum(times)

    number = 1
    repeat = 100
    print("Pillow")
    print("png: ", _ti("pil", "png", number, repeat))
    print("jpeg: ", _ti("pil", "jpeg", number, repeat))
    print("jp2: ", _ti("pil", "jp2", number, repeat))
    print("webp: ", _ti("pil", "webp", number, repeat))

    print("Rasterio")
    print("png: ", _ti("rio", "png", number, repeat))
    print("jpeg: ", _ti("rio", "jpeg", number, repeat))
    print("jp2: ", _ti("rio", "jp2", number, repeat))
    print("webp: ", _ti("rio", "webp", number, repeat))
