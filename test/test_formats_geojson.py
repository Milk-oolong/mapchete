#!/usr/bin/env python
"""Test GeoJSON as process output."""

import os
import shutil
import yaml

import mapchete
from mapchete import formats
from mapchete.tile import BufferedTile


def test_input_data_read(mp_tmpdir, geojson, landpoly_3857):
    """Check GeoJSON as input data."""
    with mapchete.open(geojson.path) as mp:
        for tile in mp.get_process_tiles():
            assert isinstance(tile, BufferedTile)
            input_tile = formats.default.geojson.InputTile(tile, mp)
            assert isinstance(input_tile.read(), list)
            for feature in input_tile.read():
                assert isinstance(feature, dict)

    # reprojected GeoJSON
    config = geojson.dict
    config["input"].update(file1=landpoly_3857)
    # first, write tiles
    with mapchete.open(config, mode="overwrite") as mp:
        for tile in mp.get_process_tiles(4):
            assert isinstance(tile, BufferedTile)
            output = mp.get_raw_output(tile)
            mp.write(tile, output)
    # then, read output
    with mapchete.open(config, mode="readonly") as mp:
        any_data = False
        for tile in mp.get_process_tiles(4):
            with mp.config.output.open(tile, mp) as input_tile:
                if input_tile.is_empty():
                    continue
                any_data = True
                assert isinstance(input_tile.read(), list)
                for feature in input_tile.read():
                    assert isinstance(feature, dict)
        assert any_data


def test_output_data(mp_tmpdir, geojson):
    """Check GeoJSON as output data."""
    output_params = dict(
        type="geodetic",
        format="GeoJSON",
        path=mp_tmpdir,
        schema=dict(properties=dict(id="int"), geometry="Polygon"),
        pixelbuffer=0,
        metatiling=1
    )
    output = formats.default.geojson.OutputData(output_params)
    assert output.path == mp_tmpdir
    assert output.file_extension == ".geojson"
    assert isinstance(output_params, dict)

    with mapchete.open(geojson.path) as mp:
        for tile in mp.get_process_tiles(4):
            # write empty
            # mp.write(tile, None)
            # write data
            raw_output = mp.get_raw_output(tile)
            mp.write(tile, raw_output)
            # read data
            read_output = mp.config.output.read(tile)
            assert isinstance(read_output, list)
            # TODO
            # if raw_output:
            #     assert read_output
