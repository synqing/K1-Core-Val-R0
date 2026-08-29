#!/usr/bin/env python3
from __future__ import annotations

import unittest

from schematic_domains import (
    adjacency_from_membership,
    classify_net,
    domain_for_designator,
    net_placement_weight,
)


class WeightingTests(unittest.TestCase):
    def test_gnd_excluded(self):
        self.assertEqual(classify_net("GND"), "gnd")
        self.assertEqual(net_placement_weight("GND"), 0.0)

    def test_power_downweighted(self):
        self.assertLess(net_placement_weight("5V_SYS"), 0.2)
        self.assertLess(net_placement_weight("3V3"), 0.2)

    def test_gnd_does_not_glue_all_domains(self):
        membership = {
            "U6-RTC": {"GND", "SAI1_BCLK"},
            "U10-AUD": {"GND", "SAI1_BCLK"},
            "U8-ESP": {"GND", "K1BR_SCK"},
            "C1-PWR1": {"GND", "5V_SYS"},
        }
        adj = adjacency_from_membership(membership)
        keys = adj["weights"]
        self.assertIn("audio|rt1062", keys)
        # GND must not create a strong power_entry–s3 seam by itself
        self.assertNotIn("power_entry|s3", keys)

    def test_reading_order_declared(self):
        adj = adjacency_from_membership({"U6-RTC": {"SAI1_BCLK"}, "U10-AUD": {"SAI1_BCLK"}})
        self.assertEqual(adj["reading_order"][0], "power_entry")
        self.assertEqual(adj["reading_order"][1], "usb_hub")
        self.assertEqual(adj["rule"], "reading_order_overrides_residual_weight")

    def test_hub_suffix_and_validity_rail(self):
        self.assertEqual(domain_for_designator("U20-USB"), "usb_hub")
        self.assertEqual(classify_net("5V0_USB_VALID"), "power")
        self.assertEqual(classify_net("USB_DP_UP"), "si")
        self.assertEqual(classify_net("USB_DP_DN1"), "si")


if __name__ == "__main__":
    unittest.main()
