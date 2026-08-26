"""import_characters_anilist.gql 的 HTTP 稳定性单元测试（mock，不请求真实 AniList）。

运行:
  .venv/Scripts/python -m scripts._test_importer_http
"""
import http.client
import json
import sys
import os
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))          # scripts/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))  # backend/
import import_characters_anilist as mod


class FakeResp:
    def __init__(self, data):
        self._d = json.dumps(data).encode('utf-8')

    def read(self):
        return self._d


def make_http_error(code, retry_after=None):
    hdrs = http.client.HTTPMessage()
    if retry_after is not None:
        hdrs['Retry-After'] = str(retry_after)
    return urllib.error.HTTPError('https://graphql.anilist.co', code, 'err', hdrs, None)


class FakeOpener:
    """按序列返回结果的 opener。序列元素: FakeResp | HTTPError | 异常。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def open(self, req, timeout=None):
        r = self.responses[self.calls]
        self.calls += 1
        if isinstance(r, Exception):
            raise r
        return r


class GqlRetryTest(unittest.TestCase):
    def setUp(self):
        mod.REQUEST_STATS.update({'count': 0, 'http_429': 0, 'http_5xx': 0, 'http_other': 0})
        mod._last_request_at = 0.0

    def test_429_retry_after(self):
        """429 + Retry-After=2 → 等待 2s 后成功。"""
        opener = FakeOpener([make_http_error(429, retry_after=2), FakeResp({'data': {'ok': 1}})])
        sleeps = []
        with mock.patch.object(mod, 'OPENER', opener), \
                mock.patch.object(mod.time, 'sleep', side_effect=lambda s: sleeps.append(s)):
            out = mod.gql('q', delay=0, retries=4, timeout=10)
        self.assertEqual(out['data']['ok'], 1)
        self.assertEqual(opener.calls, 2)
        self.assertEqual(mod.REQUEST_STATS['http_429'], 1)
        self.assertIn(2.0, sleeps)  # Retry-After 被遵守

    def test_429_backoff_no_retry_after(self):
        """429 无 Retry-After → 指数退避 2/4，第 3 次成功。"""
        opener = FakeOpener([make_http_error(429), make_http_error(429),
                             make_http_error(429), FakeResp({'data': {'ok': 1}})])
        sleeps = []
        with mock.patch.object(mod, 'OPENER', opener), \
                mock.patch.object(mod.time, 'sleep', side_effect=lambda s: sleeps.append(s)):
            out = mod.gql('q', delay=0, retries=4, timeout=10)
        self.assertEqual(opener.calls, 4)
        self.assertEqual(mod.REQUEST_STATS['http_429'], 3)
        self.assertEqual(sleeps, [2.0, 4.0, 8.0])

    def test_429_exhausted(self):
        """429 超过 retries → 最终抛出 429。"""
        opener = FakeOpener([make_http_error(429)] * 6)
        with mock.patch.object(mod, 'OPENER', opener), \
                mock.patch.object(mod.time, 'sleep', return_value=None):
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                mod.gql('q', delay=0, retries=4, timeout=10)
        self.assertEqual(ctx.exception.code, 429)
        self.assertEqual(opener.calls, 5)  # 初始 + 4 次重试

    def test_500_limited_retries(self):
        """5xx 最多重试 2 次后放弃。"""
        opener = FakeOpener([make_http_error(500), make_http_error(500), make_http_error(500)])
        sleeps = []
        with mock.patch.object(mod, 'OPENER', opener), \
                mock.patch.object(mod.time, 'sleep', side_effect=lambda s: sleeps.append(s)):
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                mod.gql('q', delay=0, retries=4, timeout=10)
        self.assertEqual(ctx.exception.code, 500)
        self.assertEqual(opener.calls, 3)
        self.assertEqual(mod.REQUEST_STATS['http_5xx'], 3)
        self.assertEqual(sleeps, [2.0, 4.0])

    def test_4xx_no_retry(self):
        """4xx 非 429 不重试。"""
        opener = FakeOpener([make_http_error(404)])
        with mock.patch.object(mod, 'OPENER', opener), \
                mock.patch.object(mod.time, 'sleep', return_value=None):
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                mod.gql('q', delay=0, retries=4, timeout=10)
        self.assertEqual(ctx.exception.code, 404)
        self.assertEqual(opener.calls, 1)
        self.assertEqual(mod.REQUEST_STATS['http_other'], 1)

    def test_network_error_retry(self):
        """网络/超时错误 → 重试后成功。"""
        opener = FakeOpener([urllib.error.URLError('boom'), urllib.error.URLError('boom'),
                             FakeResp({'data': {'ok': 1}})])
        with mock.patch.object(mod, 'OPENER', opener), \
                mock.patch.object(mod.time, 'sleep', return_value=None):
            out = mod.gql('q', delay=0, retries=4, timeout=10)
        self.assertEqual(out['data']['ok'], 1)
        self.assertEqual(opener.calls, 3)
        self.assertEqual(mod.REQUEST_STATS['http_other'], 2)

    def test_delay_throttle(self):
        """成功请求之间保证最小间隔：第二次请求前 sleep delay。"""
        opener = FakeOpener([FakeResp({'data': {'a': 1}}), FakeResp({'data': {'b': 2}})])
        sleeps = []
        with mock.patch.object(mod, 'OPENER', opener), \
                mock.patch.object(mod.time, 'sleep', side_effect=lambda s: sleeps.append(s)), \
                mock.patch.object(mod.time, 'time', side_effect=[10.0, 10.0, 12.0, 12.0]):
            mod.gql('q', delay=5, retries=1, timeout=10)   # 距上次(0) 10s，不 sleep
            mod.gql('q', delay=5, retries=1, timeout=10)   # 距上次 2s < 5s，sleep 3
        self.assertEqual(sleeps, [3.0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
