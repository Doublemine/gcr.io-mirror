#!/bin/bash
git  add   .
git  commit -am "travis automated commit update at: $(TZ=UTC-8 date "+%Y-%m-%d %H:%M:%S")"
git  status
git  pull origin master
git  status
git  branch
git  push -u origin master