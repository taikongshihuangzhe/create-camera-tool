#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from collections import OrderedDict

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """Load yaml into a python OrderedDict objet."""
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


class Data(object):
    """Load body and lens yaml files and store into OrderedDict."""
    def __init__(self):
        self.body = OrderedDict()
        self.lens = OrderedDict()
        self.load_yaml()

    def load_yaml(self):
        body_path = os.path.join(os.path.dirname(__file__), 'yaml', 'body.yaml')
        lens_path = os.path.join(os.path.dirname(__file__), 'yaml', 'lenses.yaml')
        if not os.path.isfile(body_path) or not os.path.isfile(lens_path):
            # raise error
            return

        with open(body_path, 'r') as yaml_file:
            self.body = ordered_load(yaml_file, yaml.SafeLoader)
        with open(lens_path, 'r') as yaml_file:
            self.lens = ordered_load(yaml_file, yaml.SafeLoader)
