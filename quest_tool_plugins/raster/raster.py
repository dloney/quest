import param

from .rst_base import RstBase
from quest.util import unit_list, unit_registry


class RstUnitConversion(RstBase):
    _name = 'raster-unit-conversion'
    to_units = param.ObjectSelector(default=None,
                                    doc="""Units of the resulting dataset.""",
                                    objects=unit_list()
                                    )

    def _run(self, df, orig_metadata):
        if self.to_units is None:
            raise ValueError('to_units cannot be None')

        metadata = orig_metadata
        if 'file_path' in metadata:
            del metadata['file_path']

        reg = unit_registry()
        from_units = metadata['unit']
        if '/' in from_units and '/' not in self.to_units:
            beg = from_units.find('/')
            end = len(from_units)
            default_time = from_units[beg:end]
            to_units = self.to_units + default_time
        else:
            to_units = self.to_units
        conversion = reg.convert(1, src=from_units, dst=to_units)
        result = df.read()
        result = result * conversion
        metadata.update({'unit': to_units})
        df.metadata = metadata
        df = result
        return df


#     class RstMerge(RstBase):
#         def register(self, name='raster-merge-datasets'):
#             RstBase.register(self, name=name)
#
#         def _run(self, df, options):
#             df = df.read()
#             unitsMap = {
#                 "ft3/s": "cu_ft/s",
#
#             }
#             metadata = options.get('orig_meta')
#             if 'file_path' in metadata:
#                 del metadata['file_path']
#
#             reg = UnitRegistry()
#             from_units = metadata['unit']
#             if from_units is None:
#                 raise NotImplementedError('This dataset does not contain units')
#             if from_units not in dir(reg):
#                 from_units = unitsMap[from_units]
#             if '/' in from_units and '/' not in options.get('to_units'):
#                 beg = from_units.find('/')
#                 end = len(from_units)
#                 default_time = from_units[beg:end]
#                 to_units = options.get('to_units') + default_time
#             conversion = reg.convert(1, src=from_units, dst=options.get('to_units'))
#             df[df.columns[0]] = df[df.columns[0]] * conversion
#             metadata.update({'units': options.get('to_units')})
#             df.metadata = metadata
#
#             return from_units
#
#         def apply_filter_options(self, fmt, **kwargs):
#             raise NotImplementedError
#
#
# class RstClipPolygon(RstBase):
#     def register(self, name='raster-clip-polygon'):
#         RstBase.register(self, name=name)
#
#     def _run(self, df, options):
#         # the polygon GeoJSON geometry
#         bbox = options.get('bbox')
#         poly = [util.bbox2poly(*util.listify(bbox))]
#         geoms = [{'type': 'Polygon', 'coordinates': poly}]
#
#         # load the raster, mask it by the polygon and crop it
#         with rasterio.open(src_path) as src:
#             out_image, out_transform = mask(src, geoms, crop=True)
#
#         out_meta = src.meta.copy()
#         nodata = options.get('nodata', 0)
#         out_meta.update({'nodata': nodata})
#         return df
#
#     def apply_filter_options(self, fmt, **kwargs):
#         raise NotImplementedError
