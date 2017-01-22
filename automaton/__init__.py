# -*- coding: utf-8 -*-
#
# Copyright 2013 Federico Ficarelli
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
Minimal finite-state machine.
"""

import re
import collections

from .automaton import (
    Event,
    Automaton,
    AutomatonError,
    DefinitionError,
    InvalidTransitionError,
)


__author__ = 'Federico Ficarelli'
__copyright__ = 'Copyright (c) 2015 Federico Ficarelli'
__license__ = 'Apache License Version 2.0'
__version__ = '1.0.0'

__all__ = (
    # Version
    "VERSION_INFO",
    "VERSION",
    # Automaton API
    "Event",
    "Automaton",
    # Exceptions
    "AutomatonError",
    "DefinitionError",
    "InvalidTransitionError",
)

###################################################
VERSION = __version__
# bumpversion can only search for {current_version}
# so we have to parse the version here.
version_info_t = collections.namedtuple('version_info_t', 'major minor patch')  # pylint: disable=invalid-name
VERSION_INFO = version_info_t(*(int(part) for part in re.match(r'(\d+)\.(\d+).(\d+)', __version__).groups()))
###################################################
