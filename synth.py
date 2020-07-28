# Copyright 2018 Google LLC
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

"""This script is used to synthesize generated parts of this library."""

import synthtool as s
import synthtool.gcp as gcp
import synthtool.languages.java as java

AUTOSYNTH_MULTIPLE_COMMITS = True

gapic = gcp.GAPICBazel()

protobuf_header = "// Generated by the protocol buffer compiler.  DO NOT EDIT!"
# License header
license_header = """/*
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""
bad_license_header = """/\\*
 \\* Copyright 2018 Google LLC
 \\*
 \\* Licensed under the Apache License, Version 2.0 \\(the "License"\\); you may not use this file except
 \\* in compliance with the License. You may obtain a copy of the License at
 \\*
 \\* http://www.apache.org/licenses/LICENSE-2.0
 \\*
 \\* Unless required by applicable law or agreed to in writing, software distributed under the License
 \\* is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 \\* or implied. See the License for the specific language governing permissions and limitations under
 \\* the License.
 \\*/
"""


def generate_client(service, version, proto_path=None, bazel_target=None, package=None, include_gapic=True):
  library = gapic.java_library(
      service=service,
      version=version,
      proto_path=proto_path if proto_path else f'google/{service}/{version}',
      bazel_target=bazel_target if bazel_target else f'//google/{service}/{version}:google-cloud-{service}-{version}-java',
  )

  library = library / f"google-cloud-{service}-{version}-java"

  s.replace(
      library / f'proto-google-cloud-{service}-{version}-java/src/**/*.java',
      protobuf_header,
      f'{license_header}{protobuf_header}'
  )

  if service == "firestore-admin":
    s.replace(
        library / f'grpc-google-cloud-{service}-{version}-java/src/**/*.java',
        bad_license_header,
        license_header
    )
    s.replace(
        library / f'proto-google-cloud-{service}-{version}-java/src/**/*.java',
        bad_license_header,
        license_header
    )

  pkg = package if package else f'com.google.{service}.{version}'
  s.replace(
      library / f'grpc-google-cloud-{service}-{version}-java/src/**/*.java',
      f'package {pkg};',
      f'{license_header}package {pkg};'
  )

  s.copy(library / f'grpc-google-cloud-{service}-{version}-java/src', f'grpc-google-cloud-{service}-{version}/src')
  s.copy(library / f'proto-google-cloud-{service}-{version}-java/src', f'proto-google-cloud-{service}-{version}/src')
  java.format_code(f'grpc-google-cloud-{service}-{version}/src')
  java.format_code(f'proto-google-cloud-{service}-{version}/src')

  if include_gapic and service == "firestore-admin":
    s.copy(library / f'gapic-google-cloud-{service}-{version}-java/src', 'google-cloud-firestore-admin/src')
    java.format_code(f'google-cloud-firestore-admin/src')
  else:
    s.copy(library / f'gapic-google-cloud-{service}-{version}-java/src', 'google-cloud-firestore/src')
    java.format_code(f'google-cloud-firestore/src')

  return library

admin_v1 = generate_client(
    service='firestore-admin',
    version='v1',
    proto_path='google/firestore/admin/v1',
    bazel_target='//google/firestore/admin/v1:google-cloud-firestore-admin-v1-java',
    package='com.google.firestore.admin.v1',
    include_gapic=True
)

firestore_v1 = generate_client(
    service='firestore',
    version='v1',
    include_gapic=True
)

java.common_templates(excludes=[
    # firestore uses a different project for its integration tests
    # due to the default project running datastore
    '.kokoro/presubmit/integration.cfg',
    '.kokoro/presubmit/samples.cfg',
    '.kokoro/nightly/integration.cfg',
    '.kokoro/nightly/samples.cfg'
])

