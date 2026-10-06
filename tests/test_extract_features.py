import copy
import unittest
from extract_features import extract_features, parse_request, BASIC_FEATURES, PATTERN_FEATURES


def request(body='', target='/login', content_type='application/x-www-form-urlencoded'):
    return dict(method='POST', request_target=target, body=body,
                headers=[['Content-Type', content_type]] if content_type else [])


class FeatureTests(unittest.TestCase):
    def test_form_plus_and_encoded_delimiters(self):
        p = parse_request(request('name=Ali+Veli&expr=2%2B2&x=a%26b%3Dc'))
        self.assertEqual(p['body_params'], [('name','Ali Veli'),('expr','2+2'),('x','a&b=c')])

    def test_decode_only_once_and_preserve_path_plus(self):
        p = parse_request(request('x=%2527', '/C++/'))
        self.assertEqual(p['body_params'], [('x','%27')])
        self.assertEqual(p['decoded_path'], '/C++/')

    def test_duplicates_empty_values_and_separate_locations(self):
        f = extract_features(request('id=1&id=2&empty=', '/?id=3'))['features']
        self.assertEqual(f['body_param_count'], 3)
        self.assertEqual(f['query_param_count'], 1)
        self.assertEqual(f['duplicate_param_count'], 1)

    def test_empty_body_is_known(self):
        r = extract_features(request('', content_type=None))
        self.assertEqual(r['parse_status']['body'], 'empty')
        self.assertEqual(r['features']['body_param_count'], 0)
        self.assertEqual(r['features']['digit_ratio'], 0)

    def test_json_not_parsed_as_form(self):
        r = extract_features(request('{"x":"2+2"}', content_type='application/json'))
        self.assertEqual(r['parse_status']['body'], 'unsupported')
        self.assertIsNone(r['features']['body_param_count'])
        self.assertIsNone(r['features']['sql_keyword_count'])
        self.assertEqual(r['features']['body_length'], 11)

    def test_missing_body_is_not_empty(self):
        x = request()
        del x['body']
        r = extract_features(x)
        self.assertEqual(r['parse_status']['body'], 'missing')
        self.assertIsNone(r['features']['body_length'])

    def test_unrecorded_body_is_missing(self):
        x = request('id=1'); x['body_recorded'] = False
        self.assertIsNone(extract_features(x)['features']['body_length'])

    def test_invalid_encoding_not_silently_replaced(self):
        x = request('name=Jam%F3n')
        self.assertEqual(extract_features(x)['parse_status']['body'], 'parse_error')
        self.assertEqual(parse_request(x, 'latin-1')['body_params'], [('name','Jamón')])

    def test_charset_and_header_case(self):
        x = request('name=Jam%F3n', content_type='application/x-www-form-urlencoded; charset=iso-8859-1')
        x['headers'][0][0] = 'CONTENT-TYPE'
        self.assertEqual(parse_request(x)['body_params'], [('name','Jamón')])

    def test_invalid_percent(self):
        r = extract_features(request('x=%ZZ'))
        self.assertEqual(r['parse_status']['body'], 'invalid_percent_encoding')
        self.assertIsNone(r['features']['quote_count'])

    def test_pattern_indicators(self):
        x = request('x=%3C%21--%23include+file%3D%22a%22+--%3E')
        f = extract_features(x)['features']
        self.assertEqual(f['ssi_marker_present'], 1)
        self.assertEqual(f['angle_bracket_count'], 2)
        self.assertEqual(f['quote_count'], 2)
        self.assertEqual(f['script_tag_present'], 0)

    def test_no_patterns_created_across_values(self):
        f = extract_features(request('a=SEL&b=ECT&c=selection'))['features']
        self.assertEqual(f['sql_keyword_count'], 0)
        self.assertEqual(extract_features(request('a=SeLeCt'))['features']['sql_keyword_count'], 1)

    def test_path_traversal(self):
        f = extract_features(request('', '/%2e%2e/file'))['features']
        self.assertEqual(f['path_traversal_count'], 1)

    def test_metadata_does_not_change_features_or_mutate_input(self):
        a = request('x=123')
        saved = copy.deepcopy(a)
        b = dict(a, label=1, source_file='attack', sample_id='123', waf_messages='SQLi')
        self.assertEqual(extract_features(a), extract_features(b))
        self.assertEqual(a, saved)
        self.assertEqual(set(extract_features(a)['features']), set(BASIC_FEATURES + PATTERN_FEATURES))


if __name__ == '__main__':
    unittest.main()
