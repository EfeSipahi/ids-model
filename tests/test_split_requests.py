import unittest
from split_requests import make_groups, representation, near


def record(i, target='/login', body='', method='GET', label=0):
    return dict(sample_id=str(i),request_target=target,body=body,method=method,label=label,
                headers=[['Content-Type','application/x-www-form-urlencoded']])


class SplitTests(unittest.TestCase):
    def test_transport_duplicates_group_together(self):
        a=record(1,'/login?a=Ali+Veli&b=2%2B2')
        b=record(2,'/login','b=2%2B2&a=Ali+Veli','POST',1)
        groups,*_=make_groups([a,b])
        self.assertEqual(groups[0],groups[1])

    def test_repeated_parameters_preserved(self):
        self.assertNotEqual(representation(record(1,'/login?a=1&a=2'))[3],
                            representation(record(2,'/login?a=2'))[3])

    def test_same_endpoint_not_sufficient(self):
        groups,*_=make_groups([record(1,'/login?a=alice'),record(2,'/login?a=bob')])
        self.assertNotEqual(groups[0],groups[1])

    def test_near_values(self):
        a='x'*100+'a'
        b='x'*100+'b'
        self.assertTrue(near(a,b))
        self.assertFalse(near('short1','short2'))

    def test_near_group_label_independent(self):
        rs=[record(1,'/login?a='+'x'*100+'a'),record(2,'/login?a='+'x'*100+'b',label=1)]
        g,*_=make_groups(rs)
        self.assertEqual(g[0],g[1])
        rs[0]['label']=1
        self.assertEqual(g,make_groups(rs)[0])

    def test_different_endpoints_stay_separate(self):
        groups,*_=make_groups([record(1,'/a?x=1'),record(2,'/b?x=1')])
        self.assertNotEqual(groups[0],groups[1])

    def test_decode_once(self):
        self.assertNotEqual(representation(record(1,'/a?x=%252B'))[3],
                            representation(record(2,'/a?x=%2B'))[3])

    def test_reused_long_value_across_endpoints(self):
        v='a'*40
        groups,*_=make_groups([record(1,'/a?x='+v),record(2,'/b?y='+v,label=1)])
        self.assertEqual(groups[0],groups[1])


if __name__=='__main__': unittest.main()
