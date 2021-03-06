import json

from pyramid import testing

from daybed.renderers import GeoJSON
from .support import BaseWebTest, force_unicode


class TestGeoJSONRenderer(BaseWebTest):

    def setUp(self):
        super(TestGeoJSONRenderer, self).setUp()
        roles = {'admins': ['group:pirates']}

        self.name = name = 'locations'
        definition = {
            'fields': [{'name': 'location', 'type': 'point'}]
        }
        self.db.put_model(definition, roles, 'admin-only', name)

        name = 'geomodel'
        definition = {
            'fields': [{'name': 'geom', 'type': 'geojson'}]
        }
        self.db.put_model(definition, roles, 'admin-only', name)

        name = 'multigeoms'
        definition = {
            'fields': [{'name': 'point', 'type': 'point'},
                       {'name': 'line', 'type': 'line'}]
        }
        self.db.put_model(definition, roles, 'admin-only', name)

        self.geojson = GeoJSON()
        self.renderer = self.geojson(None)

    def assertJSONEqual(self, a, b):
        self.assertDictEqual(json.loads(a), force_unicode(b))

    def _build_request(self, name=None):
        request = testing.DummyRequest()
        request.matchdict['model_id'] = name or self.name
        request.db = self.db
        return request

    def _rendered(self, data, request=None):
        request = request or self._build_request()
        system = {'request': request}
        return self.renderer(data, system)

    def test_geojson_renderer_with_empty_collection(self):
        geojson = self._rendered({'data': []})
        self.assertJSONEqual(geojson, {'type': 'FeatureCollection',
                                       'features': []})

    def test_geojson_renderer_as_features(self):
        geojson = self._rendered({'data': [{'location': [1, 2]}]})
        self.assertJSONEqual(geojson, {'type': 'FeatureCollection',
                                       'features': [
                                           {'id': None,
                                            'type': 'Feature',
                                            'geometry': {
                                                'type': 'Point',
                                                'coordinates': [1, 2]},
                                            'properties': {}}
                                       ]})

    def test_geojson_renderer_renames_geometry_field(self):
        geojson = self._rendered({'data': [{'location': [0, 0]}]})
        geometry = json.loads(geojson)['features'][0]['geometry']
        self.assertDictEqual(geometry, {'type': 'Point',
                                        'coordinates': [0, 0]})

    def test_geojson_renderer_renames_only_first_geometry_field(self):
        request = self._build_request(name='multigeoms')
        geojson = self._rendered({'data': [{'point': [0, 0],
                                            'line': [[0, 0], [1, 1]]}]},
                                 request)
        record = json.loads(geojson)['features'][0]
        self.assertDictEqual(record['geometry'],
                             {'type': 'Point', 'coordinates': [0, 0]})
        self.assertDictEqual(record['line'],
                             {'type': 'Linestring',
                              'coordinates': [[0, 0], [1, 1]]})

    def test_geojson_renderer_works_with_jsonp(self):
        request = self._build_request()
        request.GET['callback'] = 'func'
        geojsonp = self._rendered({'data': [{'location': [0, 0]}]}, request)
        self.assertIn('func(', geojsonp)

    def test_geojson_renderer_works_with_geojson_field(self):
        request = self._build_request(name='geomodel')
        records = {'data': [{'geom': {'type': 'Linestring',
                                      'coordinates': [[0, 0], [1, 1]]}}]}
        geojson = self._rendered(records, request)
        self.assertJSONEqual(geojson, {
            'type': 'FeatureCollection', 'features': [{
                'id': None,
                'type': 'Feature',
                'geometry': {'type': 'Linestring',
                             'coordinates': [[0, 0], [1, 1]]},
                'properties': {}}
            ]})
