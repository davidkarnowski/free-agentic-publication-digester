"""Marks the package test directory as a package so its conftest registers
as `tests.conftest`, not top-level `conftest` — which is the name the
repository's rootless tests/conftest.py is imported under (`from conftest
import DATE`). Without this file a full-repo run shadows the repository's
conftest with this one (found 2026-09-13, 15 collection errors).
"""
