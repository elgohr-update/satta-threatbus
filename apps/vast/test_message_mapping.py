from datetime import datetime, timedelta, timezone
import unittest
import json

from threatbus.data import (
    Intel,
    IntelData,
    IntelType,
    Operation,
    Sighting,
)
from .message_mapping import (
    get_vast_intel_type,
    get_ioc,
    to_vast_ioc,
    to_vast_query,
    query_result_to_threatbus_sighting,
    matcher_result_to_threatbus_sighting,
)


class TestMessageMapping(unittest.TestCase):
    def setUp(self):
        self.ts = datetime.now(timezone.utc).astimezone()
        self.id = "42"
        self.operation = Operation.REMOVE
        self.indicator = ("6.6.6.6",)
        self.intel_type = IntelType.IPSRC
        self.valid_intel_data = IntelData(self.indicator, self.intel_type, foo=23)
        self.valid_intel = Intel(
            self.ts, self.id, self.valid_intel_data, self.operation
        )
        self.valid_query_result = f'{{"ts": "{self.ts}", "uid": "CArLTF3OEJAsF1A41h", "id.orig_h": "{self.indicator[0]}", "id.orig_p": "20004/tcp", "id.resp_h": "172.31.129.37", "id.resp_p": "40731/tcp", "proto": "tcp", "service": null, "duration": "10.75ms", "orig_bytes": 260, "resp_bytes": 352, "conn_state": "SF", "local_orig": null, "local_resp": null, "missed_bytes": 0, "history": "DadAFf", "orig_pkts": 5, "orig_ip_bytes": 520, "resp_pkts": 5, "resp_ip_bytes": 612, "tunnel_parents": []}}'
        self.valid_vast_sighting = f'{{"ts": "{self.ts}", "data_id": 8, "indicator_id": 5, "matcher": "threatbus-syeocdkfcy", "ioc": "{self.indicator[0]}", "reference": "threatbus__{self.id}"}}'
        self.invalid_intel_1 = {
            "ts": self.ts,
            "id": self.id,
            "operation": self.operation,
        }
        self.invalid_intel_2 = {
            "ts": self.ts,
            "id": self.id,
            "operation": self.operation,
            "data": {},
        }
        self.invalid_intel_3 = {
            "ts": self.ts,
            "id": self.id,
            "operation": self.operation,
            "data": {"intel_type": "FOO"},
        }

    def test_invalid_threatbus_intel_get_ioc(self):
        self.assertIsNone(get_ioc(None))
        self.assertIsNone(get_ioc(42))
        self.assertIsNone(get_ioc(object))
        self.assertIsNone(get_ioc(self.invalid_intel_1))
        self.assertIsNone(get_ioc(self.invalid_intel_2))
        self.assertIsNone(get_ioc(self.invalid_intel_3))

    def test_invalid_threatbus_intel_get_vast_intel_type(self):
        self.assertIsNone(get_vast_intel_type(None))
        self.assertIsNone(get_vast_intel_type(42))
        self.assertIsNone(get_vast_intel_type(object))
        self.assertIsNone(get_vast_intel_type(self.invalid_intel_1))
        self.assertIsNone(get_vast_intel_type(self.invalid_intel_2))
        self.assertIsNone(get_vast_intel_type(self.invalid_intel_3))

    def test_invalid_threatbus_intel_to_vast_ioc(self):
        self.assertIsNone(to_vast_ioc(None))
        self.assertIsNone(to_vast_ioc(42))
        self.assertIsNone(to_vast_ioc(object))
        self.assertIsNone(to_vast_ioc(self.invalid_intel_1))
        self.assertIsNone(to_vast_ioc(self.invalid_intel_2))
        self.assertIsNone(to_vast_ioc(self.invalid_intel_3))

    def test_invalid_threatbus_intel_to_vast_query(self):
        self.assertIsNone(to_vast_query(None))
        self.assertIsNone(to_vast_query(42))
        self.assertIsNone(to_vast_query(object))
        self.assertIsNone(to_vast_query(self.invalid_intel_1))
        self.assertIsNone(to_vast_query(self.invalid_intel_2))
        self.assertIsNone(to_vast_query(self.invalid_intel_3))

    def test_invalid_query_result_to_threatbus_sighting(self):
        # valid query result, invalid intel
        self.assertIsNone(
            query_result_to_threatbus_sighting(self.valid_query_result, None)
        )
        self.assertIsNone(
            query_result_to_threatbus_sighting(self.valid_query_result, 42)
        )
        self.assertIsNone(
            query_result_to_threatbus_sighting(self.valid_query_result, object)
        )
        self.assertIsNone(
            query_result_to_threatbus_sighting(
                self.valid_query_result, self.invalid_intel_1
            )
        )
        self.assertIsNone(
            query_result_to_threatbus_sighting(
                self.valid_query_result, self.invalid_intel_2
            )
        )
        self.assertIsNone(
            query_result_to_threatbus_sighting(
                self.valid_query_result, self.invalid_intel_3
            )
        )

        # invalid query result, valid intel
        self.assertIsNone(query_result_to_threatbus_sighting(None, self.valid_intel))
        self.assertIsNone(query_result_to_threatbus_sighting(42, self.valid_intel))
        self.assertIsNone(query_result_to_threatbus_sighting(object, self.valid_intel))
        self.assertIsNone(
            query_result_to_threatbus_sighting("some non-json string", self.valid_intel)
        )
        self.assertIsNone(
            query_result_to_threatbus_sighting(self.invalid_intel_1, self.valid_intel)
        )
        self.assertIsNone(
            query_result_to_threatbus_sighting(self.valid_intel, self.invalid_intel_2)
        )

    def test_invalid_matcher_result_to_threatbus_sighting(self):
        self.assertIsNone(matcher_result_to_threatbus_sighting(None))
        self.assertIsNone(matcher_result_to_threatbus_sighting(42))
        self.assertIsNone(matcher_result_to_threatbus_sighting(object))
        self.assertIsNone(matcher_result_to_threatbus_sighting("some non-json string"))
        sighting_without_ioc = (
            '{"ts": "2020-09-24T08:43:43.654072335", "reference": "threatbus__86"}'
        )
        self.assertIsNone(matcher_result_to_threatbus_sighting(sighting_without_ioc))
        sighting_with_malformed_reference = (
            '{"ts": "2020-09-24T08:43:43.654072335", "ioc": "foo", "reference": "86"}'
        )
        self.assertIsNone(
            matcher_result_to_threatbus_sighting(sighting_with_malformed_reference)
        )
        sighting_with_malformed_timestamp = '{"ts": "2020 T08 :43.654072335", "ioc": "foo", "reference": "threatbus__86"}'
        self.assertIsNone(
            matcher_result_to_threatbus_sighting(sighting_with_malformed_timestamp)
        )

    def test_valid_intel_get_ioc(self):
        self.assertEqual(get_ioc(self.valid_intel), self.indicator[0])

    def test_valid_intel_get_vast_intel_type(self):
        self.assertEqual(get_vast_intel_type(self.valid_intel), "ip")

    def test_valid_intel_to_vast_ioc(self):
        expected_vast_msg = {
            "ioc": self.indicator[0],
            "type": "ip",
            "reference": "threatbus__" + str(self.id),
        }
        vast_msg = to_vast_ioc(self.valid_intel)
        self.assertEqual(json.loads(vast_msg), expected_vast_msg)

    def test_valid_intel_to_vast_query(self):
        # IP type
        self.assertEqual(to_vast_query(self.valid_intel), "6.6.6.6")

        # URL type
        url = "https://example.com/foo/bar"
        intel_data = IntelData(url, IntelType.URL)
        intel = Intel(self.ts, self.id, intel_data, self.operation)
        self.assertEqual(to_vast_query(intel), f'"{url}" in url')

        # Domain type
        domain = "example.com"
        intel_data = IntelData(domain, IntelType.DOMAIN)
        intel = Intel(self.ts, self.id, intel_data, self.operation)
        self.assertEqual(
            to_vast_query(intel),
            f'"{domain}" in domain || "{domain}" in host || "{domain}" in hostname',
        )

    def test_valid_query_result_to_threatbus_sighting(self):
        parsed_sighting = query_result_to_threatbus_sighting(
            self.valid_query_result, self.valid_intel
        )
        self.assertIsNotNone(parsed_sighting)
        self.assertEqual(type(parsed_sighting), Sighting)
        self.assertEqual(parsed_sighting.ts, self.ts)
        self.assertEqual(parsed_sighting.ioc, self.indicator[0])
        expected_context = json.loads(self.valid_query_result)
        expected_context["source"] = "VAST"
        self.assertEqual(parsed_sighting.context, expected_context)
        self.assertEqual(parsed_sighting.intel, self.id)

    def test_valid_matcher_result_to_threatbus_sighting(self):
        parsed_sighting = matcher_result_to_threatbus_sighting(self.valid_vast_sighting)
        self.assertIsNotNone(parsed_sighting)
        self.assertEqual(type(parsed_sighting), Sighting)
        self.assertEqual(parsed_sighting.ts, self.ts)
        self.assertEqual(parsed_sighting.ioc, self.indicator[0])
        self.assertEqual(parsed_sighting.context, {"source": "VAST"})
        self.assertEqual(parsed_sighting.intel, self.id)
