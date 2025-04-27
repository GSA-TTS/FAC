import json
import os
from backend.config.vcap import GET, FIND, get_vcap_services

vcap_1 = {"key": "value"}
vcap_2 = {"key": "value", "key2": "value2"}
vcap_3 = {
    "key": [
        {"name": "alice", "a": {"k1": "v1"}, "b": {"k2": "v2"}},
        {"name": "bob", "c": {"k3": "v3"}, "d": {"k4": "v4"}},
    ]
}
vcap_4 = {
    "key": [
        {"name": "alice", "a": {"k1": "v1"}, "b": {"k2": "v2"}},
        {"name": "bob"},
        {
            "name": "clarice",
            "c": {
                "k3": {
                    "nk1": "nv1",
                    "nk2": "nv2",
                }
            },
            "d": {"k4": "v4"},
        },
        {"name": "daryl", "c": {"k3": {"nk1": "nv5"}}},
    ]
}


def _simple(vcap, cmds, result):
    os.environ["VCAP_SERVICES"] = json.dumps(vcap)
    assert get_vcap_services(cmds) == result  # nosec


def test_simple_vcap1():
    cmds = [GET("key")]
    _simple(vcap_1, cmds, "value")


def test_simple_vcap2():
    cmds = [GET("key2")]
    _simple(vcap_2, cmds, "value2")


def test_list_3a():
    cmds = [GET("key"), FIND("name", "alice"), GET("a"), GET("k1")]
    _simple(vcap_3, cmds, "v1")


def test_list_3b():
    cmds = [GET("key"), FIND("name", "bob"), GET("c"), GET("k3")]
    _simple(vcap_3, cmds, "v3")


def test_list_3c():
    cmds = [GET("key"), FIND("name", "alice"), GET("b"), GET("k2")]
    _simple(vcap_3, cmds, "v2")


def test_list_4_1():
    cmds = [GET("key"), FIND("name", "clarice"), GET("c"), GET("k3"), GET("nk1")]
    _simple(vcap_4, cmds, "nv1")


def test_list_4_2():
    cmds = [GET("key"), FIND("name", "daryl"), GET("c"), GET("k3"), GET("nk1")]
    _simple(vcap_4, cmds, "nv5")
