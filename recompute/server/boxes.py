UBUNTU_TRUSTY64 = "ubuntu/trusty64"
UBUNTU_TRUSTY32 = "ubuntu/trusty32"
HASHICORP_PRECISE64 = "hashicorp/precise64"
HASHICORP_PRECISE32 = "hashicorp/precise32"

BASE_BOXES = [
    (UBUNTU_TRUSTY64, UBUNTU_TRUSTY64),
    (UBUNTU_TRUSTY32, UBUNTU_TRUSTY32),
    (HASHICORP_PRECISE64, HASHICORP_PRECISE64),
    (HASHICORP_PRECISE32, HASHICORP_PRECISE32)
]

BASE_BOXES_URL = {
    UBUNTU_TRUSTY64: "https://atlas.hashicorp.com/ubuntu/boxes/trusty64",
    UBUNTU_TRUSTY32: "https://atlas.hashicorp.com/ubuntu/boxes/trusty32",
    HASHICORP_PRECISE64: "https://atlas.hashicorp.com/hashicorp/boxes/precise64",
    HASHICORP_PRECISE32: "https://atlas.hashicorp.com/hashicorp/boxes/precise32"
}
