import unittest
from group_requests import endpoint_template, group_identity


class GroupTests(unittest.TestCase):
    def test_get_post_values_names_and_labels_do_not_split_group(self):
        a=dict(request_target='/login?id=1',method='GET',body='',label=0)
        b=dict(request_target='/login',method='POST',body='other=malicious',label=1)
        self.assertEqual(group_identity(a),group_identity(b))

    def test_encoded_path_and_numeric_variants(self):
        a={'request_target':'/shop12/%6cogin;jsessionid=abc?q=x'}
        b={'request_target':'/shop33/login'}
        self.assertEqual(group_identity(a),group_identity(b))

    def test_distinct_pages(self):
        self.assertNotEqual(group_identity({'request_target':'/login'}),group_identity({'request_target':'/register'}))

    def test_case_and_plus_preserved(self):
        self.assertEqual(endpoint_template({'request_target':'/C++/Login'}),'/C++/Login')

    def test_decode_once(self):
        self.assertEqual(endpoint_template({'request_target':'/%252e'}),'/%{number}e')

    def test_invalid_percent_rejected(self):
        with self.assertRaises(ValueError):
            endpoint_template({'request_target':'/%ZZ'})


if __name__=='__main__':
    unittest.main()
