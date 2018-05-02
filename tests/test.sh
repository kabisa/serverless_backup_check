#!/bin/sh

pytest -n auto --cov=backup --cov-report html .
