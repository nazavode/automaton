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

import collections

from .automaton import (
    Event,
    Automaton,
)

from .exceptions import (
    AutomatonError,
    DefinitionError,
    InvalidTransitionError,
)

__author__ = 'Federico Ficarelli'
__copyright__ = 'Copyright (c) 2015 Federico Ficarelli'
__license__ = 'Apache License Version 2.0'

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

VersionInfo = collections.namedtuple('VersionInfo', (
    'major',
    'minor',
    'patch',
))

VERSION_INFO = VersionInfo(major=0, minor=2, patch=0)

VERSION = '.'.join(str(v) for v in VERSION_INFO)
