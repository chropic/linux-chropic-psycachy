# Ordered replay reconciliation: CachyOS 7.3.4

**Source:** authenticated `/var/tmp/sp12-cachyos-7.3.4-compat/cachyos-7.3.4-1.tar.gz`; SHA-256 `695c641edd5df9848f931c06bf97a30734e5f28910367937d5fea235cfd39535`. GPG verification reports `VALIDSIG E8B9AA39F054E30E8290D492C3C4820857F654FE` (Peter Jung); kernelversion is 7.3.4.
**Method:** fresh extraction to `/var/tmp/sp12-cachyos-7.3.4-replay-reconcile/fresh/cachyos-7.3.4-1`; read `targets/sp121-arm64/inputs.json` in array order; for each entry verify its file SHA-256 against the manifest, run `git apply --check --no-index` against the evolving scratch tree, then apply on successful check. A failed check is recorded and not applied; processing continues for diagnostic classification. No repo source/config/patch files were changed. No compile/build.

## Ordered log

`PASS` means both check and apply succeeded on the evolving tree. `FAIL_CHECK` means the check failed and no apply was attempted for that entry.

```text
01 PASS f55b28fddb3ba849d13984f1742e3894ea12440c7519cd6b92ae52aabaebff77 patches/01-0008-arm64-dts-qcom-purwa-Microsoft-Surface-Pro-12in-correct-gpios-vol.patch
02 PASS 2e8c5b1bfe1bd305d395b5a6309e9ae99727e0f06f311dfe16fd0cbc71468348 patches/02-0002-rtc-surface-port-reference-driver.patch
03 PASS e4fe9aa0e60dd410afb67eca5d6296d8abb1b6c1a2e8e97ce82ded9331ed0af2 patches/03-0003-surface-register-sp12-rtc.patch
04 PASS 47ba490df51449fc08376257cab855e63be3c0fe6ddd1b5bfdd1c00bafeac214 patches/04-0004-surface-scope-sp12-suspend-workaround.patch
05 PASS 27614db572139fe5a0fbfdfcef6a246fa13eda57d64324f3f4ce21cbfdc2315c patches/r2/usb-phy/01-dt-bindings-phy-eusb2.patch
06 PASS 4a8217907e9913a71194645e7c9082e2353127b93f10cc3ea7b198c5455ed2ff patches/r2/usb-phy/02-phy-attributes-type.patch
07 PASS 8cc4a29e2e2840f1bbed7060793f26e3ee4bc63b66423e1d2f292bdbefea3fcf patches/r2/usb-phy/02a-phy-qcom-uniphy-enum-collision-fix.patch
08 PASS df804fea8c2c4e21052b74a06cc54c4e367b11dff21d3357c3a9bcc2d2e117bb patches/r2/usb-phy/03-phy-snps-eusb2-type.patch
09 PASS 5a3f0ae80bb66214abf229b755cbc4d7dab083387a37125cbcd3442f63230551 patches/r2/usb-phy/04-qmp-combo-dp-only-pm-guard.patch
10 PASS 0b103645a046931a72bde4c492f348df52a2327ab71862fcfb6578afa6a83912 patches/r2/platform/05-sp12-platform-dts-prerequisites.patch
11 PASS 4f0f995982af689c51e49c8c677ac500e6b2ad4cd2b0802dc8cab89240a6bd86 patches/05-0010-arm64-dts-qcom-purwa-Microsoft-Surface-Pro-12in-add-displayport-audio.patch
12 PASS bdbf1db73128888efd80904a6b1cd8180df84392d9e28dd8bad8e2d22559ce87 patches/06-0011-arm64-dts-qcom-purwa-Microsoft-Surface-Pro-12in-add-charge-limit-nvmem.patch
13 PASS b859073c5a94b71afc6af3011db9e90209a3359d65302e7aeffab37646c3ac4b patches/r2/camera/01-csi2-dphy-provider.patch
14 PASS 75f41b52769b42c370b1f4423b6bffbccce94150b51b1e4ffcc6bbc7da4de5b7 patches/r2/camera/02-camss-phy-api-and-subdevice-population.patch
15 PASS ceebdd4af7facb71c3788e046fb071ec6ce603936b8e05f0ee1847aa69fe94dc patches/r2/camera/03-x1p-camss-driver.patch
16 PASS eb2cb81a0c73ad0cf893688db41ce98f7a393da8fea184cfaab08c8bc3e73f8d patches/r2/camera/04-cci-hamoa-purwa-camss-phy-wiring.patch
17 PASS 2a883fc612bb6eae5f2855923a3060531e06404a2c672619b055e51814d75e4e patches/r2/camera/04a-camss-unused-locals-cleanup.patch
18 PASS 42fe77078300db5d854b3bee9172e7eeaf5f87ecbe50be192cb45c42477de7f3 patches/r2/camera/05-ov13858-ov02c10-sensor-drivers.patch
19 PASS 46c822a422eddb40398cc4b0fe18b03ad82e2ee2fd851dae1aaadbc47b3d5556 patches/r2/camera/05a-ov02c10-get-selection-api.patch
20 PASS fc4a78a6f10ac217c4851b7b919f799b805c1bd0bbe1238386478a3a82d1793a patches/r2/camera/06-sp12-sensor-and-csi-endpoints.patch
21 PASS 501a79b96b2e19bd196a93f8da21945892a839edfdf2ddc7866d5048b3f1bda7 patches/r2/camera/07-sp12-afvdd-clock-correction.patch
22 PASS 722d97fe09b98f1a65de9a33441aaad0fcdec19f24d4e55af13e7cc900587f18 patches/r2/camera/08-local-camera-bindings-kconfig.patch
23 PASS 165137e70208a44249b411c034c9e1269d71e4e2c9877dfb25e12a108060ea58 patches/r2/camera/09-ov02e10-assigned-clock-parents-schema.patch
24 PASS f152788e306d8cf21df0cb2e352ab502ed3b0b3569b00f627790091f203c7855 patches/r2/camera/10-csi2-provider-output-endpoint-schema.patch
25 PASS b9096e5b7cb9883d1f76fd271dd24729117b42d1020c65977c880dee9e881347 patches/r2/audio/01-soundwire-irq-clock-order.patch
26 PASS 066e43af8fca58482755ce255ca621a524ce13b12024098d17775b3be05d14c0 patches/r2/audio/02-soundwire-suspend-error-unwind.patch
27 PASS 5630cfce4228d61c1d51721a901ab3de92509750876cf6d5ff171d29ac87f996 patches/r2/pci/01-force-enable-link-state.patch
28 PASS dc14df10c68234c58c989bef6b0a6064d2ca56ce743da794bd219d5950e90f40 patches/r2/pci/02-aspm-enabled-state-mask.patch
29 PASS 85e9fee5ca4e2f2e34e5f78f9340fad45c77b4898cbd7f0dcd9f29d831eddc36 patches/r2/pci/03-wcn7850-disable-ltr.patch
30 PASS c909ee1fbc26e33e668fa6d18f6cec51982a5754bada5904251637144798e604 patches/r2/pci/04-sp12-pcie4-t-power-on.patch
31 PASS fa4109ca8cce5690767dded3d6ff16b4c1de14768026eacbd57292adeac7d6ae patches/r2/pci/05-hamoa-pcie-opp-tables.patch
32 PASS 619d3da2c931f3bc18530db685be8653a8ba4a423045c215cdb914c6f7ddbb43 patches/r2/pci/06-ath12k-aspm-api.patch
33 PASS 9c7518b30be80933ac635a17c2dadbb6409f42542bc964a08648b7a2ac967755 patches/r2/pci/07-ath12k-skip-sp12-rfkill.patch
34 PASS b5d362252fc7c8d7ed4962f709dbc1f3709d5133bd0635ae84256e1cd35a69f1 patches/07-kexec-signature-force-arm64.patch
35 PASS f557cb4ab5b83eabd2a67f4c190be66a8d62b70b68c5ffcbc08b5c278bcc77ae patches/08-rpmb-core-serialize-teardown.patch
36 PASS c93d0f2ecfb870eb1f1a6f71da03357dd380afb6d2e32f2a73274e7f0071b28a patches/09-ufs-rpmb-lifetime.patch
37 PASS 3684292933c426ab616eb25846571ae95786a668dda746fe7b1c52036986f938 patches/10-ufs-rpmb-drop-unregistered-bus.patch
38 PASS 3bb43b70da13e8d0de91bffafd21f3ace35d162ad679ef83eba8f9706ba479f8 patches/r2/usb/0001-usb-dwc3-qcom-skip-phy-management.patch
39 PASS 617bdca1b9429809b61104f10419b274407ea7866b90b57d8711a4000c5d858f patches/r2/usb/0002-usb-dwc3-qcom-eusb2-wake-irq-map.patch
40 PASS 020c77eb566572ef2b70b18aea11a94e063f180da6511f7fda93c0b799d60bdf patches/r2/usb/0004-usb-dwc3-qcom-balance-wake-irq-on-failed-resume.patch
41 PASS 21fd94a37f22c9f46c57462db18d8a4f320e16c3a1177b8cbcc3c46e336c1045 patches/r2/usb/0005-usb-dwc3-qcom-balance-runtime-pm-wake-irq.patch
42 PASS 81e98508745ac57f1ddc476844b7f312f479681bcd9757a6227629ddb333e112 patches/r2/usb/0006-arm64-dts-hamoa-usb1-ss0-noc-clocks.patch
43 PASS 09167da47080bac348e1b896a7ca4acb34e16697183da8a38f437b4fb6b1393a patches/r2/video/01-iommu-of_iommu-ranges.patch
44 PASS b05a6c29b8bb0cedc25e267c66a34209908da08875e6d115d4f118ec140f416f patches/r2/video/01a-venus-common-context-banks.patch
45 PASS adb11a24eb8086a83aa4d1a21d917f86973366cbc60c6aca29ca0d12e76bfbfc patches/r2/video/01b-sm8550-iris-context-banks.patch
46 FAIL_CHECK 0e45ebcfc581b543dba325afebf39402b4bccfcfaa67c838580147070da3da64 patches/r2/video/02-iris-context-bank-devices.patch :: error: patch failed: drivers/media/platform/qcom/iris/iris_probe.c:150 | error: drivers/media/platform/qcom/iris/iris_probe.c: patch does not apply
47 PASS 6767b9761ba036b26476cdef2542549571534067e1a527bc7758fe74eadb5659 patches/r2/video/03-iris-route-buffers-context-bank.patch
48 PASS 7b1eae848eb485769613a2319b23fe1d8390f49a87727c10d319836280ac18be patches/r2/video/04-iris-skip-parent-dma-mask-without-iommu.patch
49 PASS 2831956d97d92bf5781f04edb03318accf2bfb525ce800df0001645011e885b7 patches/r2/video/05-hamoa-iris-context-bank-dts.patch
50 PASS e4ca052e5046370ce92e3a4532b4e750cc04268c39c39a3dd1130fbf1d1d34fb patches/r2/bluetooth/01-wcn7850-drop-unused-event.patch
51 PASS 601f591f755cd0bc4fc6a5ae4e5b4b0d58ccbb522b94a9123516668f8237b663 patches/r2/suspend/01-arm-arch-timer-park-stopped.patch
COUNT entries=51 pass=50 fail=1
```

## Result and discrepancy resolution

The strict ordered replay reaches one blocker: entry 46, `patches/r2/video/02-iris-context-bank-devices.patch` (SHA-256 `0e45ebcfc581b543dba325afebf39402b4bccfcfaa67c838580147070da3da64`), fails its `iris_probe.c` hunk at line 150. Entries 1–45 were actually applied first. Entries 47–49 each pass when checked/applied after those predecessors with entry 46 omitted, and entries 50–51 also pass; therefore the compatibility worker’s statement about later entries is reproducible under its continue-after-failure diagnostic method. A strict “complete series replay” still fails at 46 because the series is not complete, and downstream passes cannot cure that missing child-device setup.

This also explains my earlier pristine-source spot checks: testing entries 47–49 individually against unpatched upstream was the wrong comparison. Their ordered contexts depend on prior patches, so those spot-check failures are withdrawn as evidence of additional series incompatibilities. The ordered replay does not support the earlier claim that 03/04/05 are independent blockers. The remaining concern is the actual entry-46 rebase plus its interaction with 7.3.4’s parent IOVA reservation; this log alone does not establish runtime safety or authorize a build.
