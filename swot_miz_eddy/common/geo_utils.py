from typing import List
from osgeo import ogr
ogr.UseExceptions()


def build_polygon(shapefile_path) -> List:
    driver = ogr.GetDriverByName('ESRI Shapefile')
    with driver.Open(shapefile_path) as file:
        # read metadata
        layer = file.GetLayer()
        feat = layer.GetFeature(0)
        geom = feat.GetGeometryRef()
        logging.info(f'{geom = }')
        logging.info(f'Geometry type: {geom.GetGeometryName()}')

        # handle different geometry type
        polygon_list = []

        if geom.GetGeometryName() == 'POLYGON':
            ring = geom.GetGeometryRef(0)  # outer ring
            polygon_list = [[ring.GetX(i), ring.GetY(i)] for i in range(ring.GetPointCount())]

        elif geom.GetGeometryName() == 'MULTIPOLYGON':
            # for MULTIPOLYGON, get the first polygon
            multipolygon = geom
            if multipolygon.GetGeometryCount() > 0:
                polygon = multipolygon.GetGeometryRef(0)
                ring = polygon.GetGeometryRef(0)  # outer ring
                polygon_list = [[ring.GetX(i), ring.GetY(i)] for i in range(ring.GetPointCount())]

        if not polygon_list:
            raise ValueError(f"Unable to extract coordinate points from the geometry. Geometry type: {geom.GetGeometryName()}")
    return polygon_list


if __name__ == "__main__":
    import logging
    from pathlib import Path
    # root of repo (parent of scripts/)
    REPO_ROOT = Path(__file__).resolve().parents[2]
    roi_shp_path = REPO_ROOT / "data" / "mask" / "research_area_enclosing" / "research_area_enclosing.shp"
    roi_polygon = build_polygon(roi_shp_path)
    print(f'{roi_polygon = }')
