"""Tests for Vastu."""
from src.core import Vastu
def test_init(): assert Vastu().get_stats()["ops"] == 0
def test_op(): c = Vastu(); c.generate(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Vastu(); [c.generate() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Vastu(); c.generate(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Vastu(); r = c.generate(); assert r["service"] == "vastu"
