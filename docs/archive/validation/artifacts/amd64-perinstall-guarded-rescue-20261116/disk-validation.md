## Installed target QCOW check

Exit: 0

```text
No errors were found on the image.
208009/1048576 = 19.84% allocated, 3.11% fragmented, 0.00% compressed clusters
Image end offset: 13636337664
```

## Installed target QCOW info

Exit: 0

```text
image: /var/tmp/amd64-perinstall-current-20261116/linux.qcow2
file format: qcow2
virtual size: 64 GiB (68719476736 bytes)
disk size: 12.7 GiB
cluster_size: 65536
Format specific information:
    compat: 1.1
    compression type: zlib
    lazy refcounts: false
    refcount bits: 16
    corrupt: false
    extended l2: false
Child node '/file':
    filename: /var/tmp/amd64-perinstall-current-20261116/linux.qcow2
    protocol type: file
    file length: 12.7 GiB (13636337664 bytes)
    disk size: 12.7 GiB
```

## Read-only sentinel QCOW check

Exit: 0

```text
No errors were found on the image.
16/1048576 = 0.00% allocated, 0.00% fragmented, 0.00% compressed clusters
Image end offset: 1376256
```

## Read-only sentinel QCOW info

Exit: 0

```text
image: /var/tmp/amd64-perinstall-current-20261116/other.qcow2
file format: qcow2
virtual size: 64 GiB (68719476736 bytes)
disk size: 1.25 MiB
cluster_size: 65536
Format specific information:
    compat: 1.1
    compression type: zlib
    lazy refcounts: false
    refcount bits: 16
    corrupt: false
    extended l2: false
Child node '/file':
    filename: /var/tmp/amd64-perinstall-current-20261116/other.qcow2
    protocol type: file
    file length: 1.31 MiB (1376256 bytes)
    disk size: 1.25 MiB
```

## Sentinel hash and pattern verification

Exit: 0

```text
other.qcow2: OK
read 1048576/1048576 bytes at offset 0
1 MiB, 1 ops; 00.00 sec (7.221 GiB/sec and 7394.2621 ops/sec)
```
