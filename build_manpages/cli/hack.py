# Copyright (C) 2017 Red Hat, Inc.
# Darn, this needs to go away!

import argparse


class _FixMap(object):
    opt_to_conf = {}
    conf_to_opt = {}
    def set(self, opt, conf):
        self.conf_to_opt[conf] = opt
        self.opt_to_conf[opt] = conf
    def __init__(self):
        self.set('project-name', 'name')
    def opt(self, conf):
        return self.conf_to_opt.get(conf, conf)
    def conf(self, opt):
        return self.opt_to_conf.get(opt, opt)

_fix_map = _FixMap()

class FakeDistribution:
    values = {}
    def __getattr__(self, key):
        key = key.lstrip('get_')
        key = key.replace('-', '_')
        if not key in self.values:
            return lambda : '<<UNSET --' + _fix_map.opt(key) + ' OPTION>>'

        return lambda : self.values[key]

class FakeCommand():
    def __init__(self):
        self.distribution = FakeDistribution()

    def getAction(self):
        parent = self
        class A(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                option_string = option_string.lstrip('--')
                option_string = _fix_map.conf(option_string)
                option_string = option_string.replace('-', '_')
                parent.distribution.values[option_string] = values
        return A
