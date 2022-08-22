# Copyright 2022 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Replacements to apply during testing. See devtools/notebook_test.py for syntax.

n_library_circuits=20->n_library_circuits=1
max_depth = 100->max_depth = 12
n_combinations=10->n_combinations=1
repetitions=10_000->repetitions=10
fatol=1e-2->fatol=10
xatol=1e-2->xatol=10
