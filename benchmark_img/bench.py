"""Skeleton of a handler."""

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


def array_to_img_rasterio(
    arr, mask, img_format="png", color_map=None, **creation_options
):
    """Create image buffer from array."""
    # TODO: add check if colormap and multiple bands input

    if color_map is not None:
        # Apply colormap and transpose back to raster band-style
        arr = numpy.transpose(color_map[arr][0], [2, 0, 1]).astype(numpy.uint8)

    # WEBP doesn't support 1band dataset so we must hack to create a RGB dataset
    if img_format == "webp" and arr.shape[0] == 1:
        arr = numpy.repeat(arr, 3, axis=0)

    if mask is not None and img_format != "jpeg":
        nbands = arr.shape[0] + 1
    else:
        nbands = arr.shape[0]

    if img_format == "jp2":
        img_format = "JP2OpenJPEG"

    output_profile = dict(
        driver=img_format,
        dtype=arr.dtype,
        count=nbands,
        height=arr.shape[1],
        width=arr.shape[2]
    )
    output_profile.update(creation_options)

    with MemoryFile() as memfile:
        with memfile.open(**output_profile) as dst:
            dst.write(arr, indexes=list(range(1, arr.shape[0] + 1)))
            # Use Mask as an alpha band
            if mask is not None and img_format != "jpeg":
                dst.write(mask.astype(numpy.uint8), indexes=nbands)

        return memfile.read()


def pil(
    input,
    tile,
    ext="png",
    bidx=(1, 2, 3),
    colormap=None,
    scale=None,
    save=None,
):
    """Handle tile requests."""
    tile_z, tile_x, tile_y = list(map(int, tile.split('-')))
    tile, mask = main.tile(
        input, tile_x, tile_y, tile_z, indexes=bidx, tilesize=512
    )

    if scale:
        nbands = tile.shape[0]
        for bdx in range(nbands):
            tile[bdx] = numpy.where(
                mask,
                utils.linear_rescale(tile[bdx], in_range=scale[bdx], out_range=[0, 255]),
                0,
            )
        tile = tile.astype(numpy.uint8)

    if colormap:
        colormap = utils.get_colormap(name=colormap)

    img = utils.array_to_img(tile, mask=mask, color_map=colormap)
    img_format = "JPEG2000" if ext == "jp2" else ext
    buffer = img_to_buffer(img, img_format)
    if save:
        with open(f"{tile_x}-{tile_y}-{tile_z}_pil.{ext}", "wb") as f:
            f.write(buffer)


def gdal(
    input,
    tile,
    ext="png",
    bidx=(1, 2, 3),
    colormap=None,
    scale=None,
    save=None,
):
    """Handle tile requests."""
    tile_z, tile_x, tile_y = list(map(int, tile.split('-')))
    tile, mask = main.tile(
        input, tile_x, tile_y, tile_z, indexes=bidx, tilesize=512
    )

    if scale:
        nbands = tile.shape[0]
        for bdx in range(nbands):
            tile[bdx] = numpy.where(
                mask,
                utils.linear_rescale(tile[bdx], in_range=scale[bdx], out_range=[0, 255]),
                0,
            )
        tile = tile.astype(numpy.uint8)

    if colormap:
        colormap = numpy.array(list(chunks(utils.get_colormap(name=colormap), 3)))

    buffer = array_to_img_rasterio(tile, mask, img_format=ext, color_map=colormap)
    if save:
        with open(f"{tile_x}-{tile_y}-{tile_z}_gdal.{ext}", "wb") as f:
            f.write(buffer)
