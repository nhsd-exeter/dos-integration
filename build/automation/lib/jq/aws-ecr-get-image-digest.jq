.imageIds[] | select(.imageTag != null) | select(.imageTag | contains("TAG_TO_REPLACE")) | .imageDigest
