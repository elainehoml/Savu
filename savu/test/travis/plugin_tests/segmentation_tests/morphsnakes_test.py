# -*- coding: utf-8 -*-
# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
.. module:: plugins_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>

"""

import unittest
import savu.test.test_utils as tu
from savu.test.travis.framework_tests.plugin_runner_test import \
        run_protected_plugin_runner

class MorphsnakesTest(unittest.TestCase):
    def setUp(self):
        self.data_file = 'tomo_standard.nxs'
        self.experiment = 'tomo'

    def test_Morphsnakes2d(self):
        process_list = 'segmentation/morphsnakes/morphsnakes2d_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

    def test_Morphsnakes3d(self):
        process_list = 'segmentation/morphsnakes/morphsnakes3d_test.nxs'
        options = tu.initialise_options(self.data_file, self.experiment, process_list)
        run_protected_plugin_runner(options)
        tu.cleanup(options)

if __name__ == "__main__":
    unittest.main()
