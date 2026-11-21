# Linux 7.3.5 patch/config contract review — working decision record

**Review state: Gate 1 remains BLOCKED.** This is a source/config review, not
approval to build a successor, alter the selected C configs, publish the
private candidates, or begin physical-test planning. Acceptance criteria below
are required future tests, not claims that those tests passed. Existing C,
package inputs, and private firmware/support remain preserved.

## Candidate identity and manifest reconciliation

The common kernel source is CachyOS `cachyos-7.3.5-2`, archive SHA-256
`bb22ad99e1042fae883bab71366f8339367b74c045004fe92ad4923339092e07`.
The source tag is `cachyos-7.3.5-2`, tag object
`b1eff1002eb0e44f24294aabcab623fc95293413`, pointing to commit
`1ac42d4fa557ecd640dd7283d1be49e1ad526492`. Patch digests below bind the exact
local patch bytes. Original vendor/overlay/mail provenance and its limitations
are recorded in
the private patch inventory,
[`targets/sp121-arm64/PATCH-PROVENANCE.md`](../targets/sp121-arm64/PATCH-PROVENANCE.md),
and `targets/sp121-arm64/provenance/r2-overlay/`. “Rebased from” and a matching
hash do not establish authorship, DCO, license compatibility, or redistribution
rights. Keep derived kernel packages and ISOs private.

| Target/candidate | Exact reviewed input | Config identity | Interpretation |
|---|---|---|---|
| SP12 selected C | `targets/sp121-arm64/inputs.camera-lanes-candidate.json`, SHA-256 `d2ce07e0741649f36bcfb207fb560710a3cfb283c366dd25d1dd7371e5967d3c`, 52 ordered platform entries | `config/kernel/sp12-C.config`, SHA-256 `8fe3d35a7c714f5249c507a7ee600396f0a6cbb16d729d4d6e17fd03eba327c6` | This is the owner-selected SP12 C baseline. The 52-entry series includes CSI-2 PHY lane normalization and the 7.3.5-rebased Iris context-bank patch. |
| SP12 older r2 record | `targets/sp121-arm64/inputs.json`, SHA-256 `6040fc283d5afe04ddfa69d1bc418ead62b5de2984b73f42c22e144a6ca74e14`, 51 entries | Older r2 `config.seed`, SHA-256 `cd5027943acfa23b4fc9798cc71f6f3d88996b54a3d25ec2b873762dc39e01a0` | Historical source-coverage record, **not** the selected C manifest. Do not substitute it for the 52-entry C manifest. `inputs.r2-candidate.json` is an even earlier 34-entry candidate and is also not C. |
| SP12 private diagnostic build | Private diagnostic manifest `inputs.production-csid-iris-candidate.json`, SHA-256 `59a95ec7fb8b051ad3aa5de5c8fc1efc6107e9028b6002eccadad5c083a2a17d`, 54 entries | `configs/sp12-csid-iris.config`, SHA-256 `10920142b1ab9387fd6a23cd4fedfb5ef83e16714adaf55bd84c66eda5ff4f33`; resolved config SHA-256 `50e5c6dba499ffe3a60b868eba7a4daaec6b69e33288d171140a2c1ffe60759f` | Diff against selected C is exactly two additions: the separate Purwa CSID lane-map candidate and the Iris firmware-name candidate. The full candidate config differs from `sp12-C.config` only in `CONFIG_LOCALVERSION`; package build metadata is not a replacement for an owner-approved final pin. |
| B550I selected C | `targets/b550i-amd64/inputs.json`, SHA-256 `79502913cb87fbb1f88ad8e8888b2b9b01f3b63e6c1d4b719f45faebb178e8bf` | `output/prestable-20261118/configs/b550i-C.config`, SHA-256 `3e6665aab949a1a7ac68d7d4620c339ff69abf7af5d0fe97fde46d3e98d79cb1`; resolved config SHA-256 `ebf93896558751f14c3e7fcf91500ed74e364ad689105f418497c0f40d5e746e` | Two shared kernel patches followed by three AMD64 packaging patches. No SP12-only patch belongs here. |

The SP12 selected C apply contract is its 52 manifest entries below, then shared
BORE, shared SLUB canary, and the three ARM64 package patches below (57 patch
operations total). The diagnostic 54-entry manifest inserts its two separate
candidate patches after the 52 C platform entries; BORE, SLUB canary, and
packaging remain separate build inputs. The corresponding build metadata
records the exact source tree and resolved config, but the diagnostic candidate
is not the selected or qualified release.

The 52-entry source manifest still records the earlier platform `config.seed`
hash `cd5027943acfa23b4fc9798cc71f6f3d88996b54a3d25ec2b873762dc39e01a0`.
The selected package build used the approved full C config separately; the
diagnostic build's `config_input=approved-file` is pinned by
`configs/sp12-csid-iris.config` and its resolved-config hash. Keep these as
distinct identities rather than treating the manifest seed as the package
config.

## Source signer identity assessment

The source-signature/identity sub-review is now **corroborated**, rather than
blocked solely for lack of an identity binding:

- The official [CachyOS About/team page](https://www.cachyos.org/about)
  identifies Peter Jung (`ptr1337`) as a CachyOS founder/developer and links
  his GitHub account.
- The official
  [7.3.5-2 release API](https://api.github.com/repos/CachyOS/linux/releases/tags/cachyos-7.3.5-2)
  names `ptr1337` as release author/uploader and publishes the archive digest
  matching the local source archive. The release's annotated tag signature
  is marked verified by GitHub; its tag object and signature also verify
  locally with the pinned key.
- The archive detached signature verifies locally. Both signatures identify
  primary fingerprint
  `E8B9AA39F054E30E8290D492C3C4820857F654FE`.
- The public [GitHub profile key export](https://github.com/ptr1337.gpg)
  contains that same primary fingerprint, but its older self-certification
  says the primary key expired 2026-04-01. This initially appeared inconsistent
  with the local key.
- A fresh Ubuntu keyserver response for the same fingerprint is byte-identical
  to the retained local signer file (SHA-256
  `33fe90b5188545e7013fab56573419755ac35b7b50f50680c256b4927aac4fe9`).
  It contains a renewed, cryptographically valid self-certification for that
  unchanged primary key through 2028-03-31. The detached archive signature was
  made 2026-11-17 directly by the primary key; the expired encryption-only
  subkey is not the signing key. The profile export is therefore stale, not a
  different signing identity.

Assessment scope: this is a cross-source identity link from the official
CachyOS team page and GitHub release/tag to the same signing key and pinned
archive. It is not a Web-of-Trust or in-person fingerprint ceremony, and it
does not resolve downstream patch authorship/licensing or firmware rights.
Retain the URL/date and key-file hash if the trust review is carried forward.
The candidate pins record build-time trust state; do not rewrite historical
package metadata to imply this later assessment happened before those builds.

## SP12 selected C: ordered platform series

All 52 entries apply to the pinned CachyOS 7.3.5-2 tree. “Config” gives the
relevant C-resolved switches where there is a Kconfig switch; DTS/schema-only
rows do not invent one. Each row names its main dependency and a discriminating
acceptance test. **None of the listed runtime/hardware acceptance tests is
claimed passed by this review.**

| # | Patch ID — SHA-256 | Purpose / dependency / C config | Acceptance and rejection test |
|---:|---|---|---|
| 1 | `volume-gpio-correction` — `f55b28fddb3ba849d13984f1742e3894ea12440c7519cd6b92ae52aabaebff77` | Correct SP12 Purwa regulator/GPIO descriptions; depends on the board PMIC and regulator nodes. DTS only. | Compile and validate the final SP12 DTB; confirm the addressed rail/GPIO behavior on the target without unrelated power-state regressions. |
| 2 | `surface-rtc-driver` — `2e8c5b1bfe1bd305d395b5a6309e9ae99727e0f06f311dfe16fd0cbc71468348` | Surface Aggregator RTC driver; requires the Surface Aggregator core. `CONFIG_SURFACE_AGGREGATOR=m`, `CONFIG_RTC_DRV_SURFACE=m`. | Build/load the module; verify the SP12 RTC registers and read/alarms behave across reboot/resume. Reject duplicate or wrong RTC registration. |
| 3 | `sp12-rtc-registration` — `e4fe9aa0e60dd410afb67eca5d6296d8abb1b6c1a2e8e97ce82ded9331ed0af2` | Registers the SP12 instance for patch 2; depends on the Surface Aggregator driver and SP12 match data. No additional switch. | Verify exactly one expected RTC binds on SP12 and no unrelated Surface model is claimed. |
| 4 | `sp12-suspend-quirk` — `47ba490df51449fc08376257cab855e63be3c0fe6ddd1b5bfdd1c00bafeac214` | Narrows the Surface Aggregator suspend workaround to SP12; depends on platform matching. `CONFIG_SURFACE_AGGREGATOR=m`. | Repeated deep suspend/resume on SP12; verify affected devices recover and the quirk does not alter other systems. |
| 5 | `surface-usb-eusb2-binding` — `27614db572139fe5a0fbfdfcef6a246fa13eda57d64324f3f4ce21cbfdc2315c` | Adds the EUSB2 PHY binding constant consumed by rows 8, 10, and 39–42. No Kconfig switch. | Run binding/schema checks and compile all consumers; reject duplicate or conflicting PHY enum values. |
| 6 | `surface-phy-attribute-type` — `4a8217907e9913a71194645e7c9082e2353127b93f10cc3ea7b198c5455ed2ff` | Adds the common PHY type/helper API; prerequisite for rows 7–9. No Kconfig switch. | Compile all affected PHY providers/consumers and check type mapping; reject an API mismatch or changed numeric ABI. |
| 7 | `qcom-uniphy-pcie-type-enum-namespace` — `8cc4a29e2e2840f1bbed7060793f26e3ee4bc63b66423e1d2f292bdbefea3fcf` | Local compile-compatibility rename after row 6 exposes a macro collision; depends on row 6. No runtime/config change. | Build the UniPHY PCIe object and verify its local enum values/uses are unchanged apart from names. |
| 8 | `surface-snps-eusb2-type` — `df804fea8c2c4e21052b74a06cc54c4e367b11dff21d3357c3a9bcc2d2e117bb` | Tags the Synopsys provider as EUSB2; depends on row 5 and the type API in row 6. `CONFIG_PHY_SNPS_EUSB2=m`. | Build/probe the provider and verify the SP12 DWC3 consumer resolves the EUSB2 PHY, not a different PHY type. |
| 9 | `qmp-combo-dp-only-runtime-pm` — `5a3f0ae80bb66214abf229b755cbc4d7dab083387a37125cbcd3442f63230551` | Restricts the QMP Combo Type-C runtime-PM reference to the relevant mode; depends on row 6 and the Type-C/QMP code. `CONFIG_PHY_QCOM_QMP_COMBO=m`, `CONFIG_TYPEC=m`. | Exercise USB-only, DP-only, and role/mode transitions; verify no leaked PM reference, unpowered access, or loss of USB/DP after resume. |
| 10 | `sp12-platform-dts-prerequisites` — `0b103645a046931a72bde4c492f348df52a2327ab71862fcfb6578afa6a83912` | Board DTS prerequisites for USB, regulators, Iris and audio; precedes rows 11, 21, 31, 32, 43, and 50. DTS only. | Compile and schema-validate the final DTB; check each prerequisite node/property remains present in the packed DTB. |
| 11 | `displayport-audio` — `4f0f995982af689c51e49c8c677ac500e6b2ad4cd2b0802dc8cab89240a6bd86` | Adds the SP12 DP-audio graph; depends on row 10 and the existing Qualcomm ASoC/codec stack. No patch-defined switch. | With a real DP audio sink, verify the intended PCM route and audible output; reject a device-tree-only “present” result without playback. |
| 12 | `charge-limit-nvmem` — `bdbf1db73128888efd80904a6b1cd8180df84392d9e28dd8bad8e2d22559ce87` | Describes the SP12 charge-limit NVMEM cell; depends on the board NVMEM provider. `CONFIG_NVMEM=y`, `CONFIG_NVMEM_QCOM_QFPROM=m`. | Validate DT/schema and read-only discovery. Any write/change to NVMEM, firmware, or charge limit remains prohibited absent separate approval. |
| 13 | `camera-csi2-dphy-provider` — `b859073c5a94b71afc6af3011db9e90209a3359d65302e7aeffab37646c3ac4b` | Adds Qualcomm CSI-2 D-PHY support; prerequisite for rows 14–25. `CONFIG_PHY_QCOM_MIPI_CSI2=m`. | Build/probe and validate the PHY graph; final camera acceptance is both integrated SP12 sensors streaming, not just provider registration. |
| 14 | `camera-csi2-dt-lane-normalization` — `cc1202c2089b6e65069c1c2ae87199bfb2c96d3a7dbf85e894fdfe7238826da3` | Converts DT lane IDs 1–4 to PHY positions 0–3 at the generic CSI-2 PHY boundary; depends on row 13. Same PHY config. This is already in C and is **not** the later CSID candidate. | Unit/static check 1→0 through 4→3 and reject 0/5; then verify no lane-4 error and capture from both physical sensors. A TPG-only pass is insufficient. |
| 15 | `camera-camss-phy-api` — `75f41b52769b42c370b1f4423b6bffbccce94150b51b1e4ffcc6bbc7da4de5b7` | Adds CAMSS PHY API/subdevice population; depends on row 13 and supports row 16. `CONFIG_VIDEO_QCOM_CAMSS=m`, `CONFIG_PHY_QCOM_MIPI_CSI2=m`. | Build CAMSS and validate the media graph/subdevice population on the target; reject missing or duplicate links. |
| 16 | `camera-x1p-camss-driver` — `ceebdd4af7facb71c3788e046fb071ec6ce603936b8e05f0ee1847aa69fe94dc` | Adds X1P42100 CAMSS support; depends on row 15 and matching platform data. `CONFIG_VIDEO_QCOM_CAMSS=m`. | Probe the SP12 CAMSS blocks, enumerate CSIPHY/CSID/VFE entities, and capture through the intended route. |
| 17 | `camera-cci-hamoa-purwa-phy-wiring` — `eb2cb81a0c73ad0cf893688db41ce98f7a393da8fea184cfaab08c8bc3e73f8d` | Adds CCI/controller DTS wiring and CAMSS PHY connections; depends on rows 10, 15, and 16. DTS plus the CCI driver config in C. | Validate DT/schema and sensor I²C access; capture from each sensor and reject probe-only or one-sensor success. |
| 18 | `camss-unused-local-variable-cleanup` — `2a883fc612bb6eae5f2855923a3060531e06404a2c672619b055e51814d75e4e` | Removes two unread locals from CAMSS; follows row 17. No Kconfig or runtime-policy change. | Build the touched objects with the pinned compiler and confirm only the two unused declarations disappear. |
| 19 | `camera-ov13858-ov02c10-drivers` — `42fe77078300db5d854b3bee9172e7eeaf5f87ecbe50be192cb45c42477de7f3` | Adds OV13858/OV02C10 sensor drivers, power sequencing and controls; depends on rows 15–17. `CONFIG_VIDEO_OV13858=m`, `CONFIG_VIDEO_OV02C10=m`. | Probe both sensors, verify rails/clock/reset and control readback, then capture changing frames from each. |
| 20 | `ov02c10-selection-callback-api-rebase` — `46c822a422eddb40398cc4b0fe18b03ad82e2ee2fd851dae1aaadbc47b3d5556` | Drops an unused callback parameter to match the pinned V4L2 API; follows row 19. No config/runtime change. | Build the sensor object; verify crop/default/bounds rectangles are unchanged and sensor capture still works. |
| 21 | `camera-sp12-sensor-csi-endpoints` — `fc4a78a6f10ac217c4851b7b919f799b805c1bd0bbe1238386478a3a82d1793a` | Adds SP12 sensor/CSI endpoints; depends on rows 10, 17, and 19. DTS only. | Validate endpoint graph and lane count/order against the board; then capture front and rear independently. |
| 22 | `camera-sp12-afvdd-clock-fix` — `501a79b96b2e19bd196a93f8da21945892a839edfdf2ddc7866d5048b3f1bda7` | Corrects OV13858 AFVDD handling and OV02C10 MCLK; depends on rows 19 and 21. `CONFIG_VIDEO_OV13858=m`, `CONFIG_VIDEO_OV02C10=m`. | Scope/measure the declared clock/rail if available, verify sensor power-up sequencing, and require stable captures from both sensors. |
| 23 | `camera-bindings-kconfig` — `722d97fe09b98f1a65de9a33441aaad0fcdec19f24d4e55af13e7cc900587f18` | Supplies camera binding and Kconfig closure for rows 13–22. C enables the PHY, CAMSS, and both sensor drivers as modules. | Run targeted `dt_binding_check`, Kconfig resolution, and final DT validation; reject undocumented schema/Kconfig gaps. |
| 24 | `camera-assigned-clock-parents-binding` — `165137e70208a44249b411c034c9e1269d71e4e2c9877dfb25e12a108060ea58` | Allows assigned clock parents used by the OV02E10/OV02C10 examples; depends on row 23. Schema only. | Run the schema against the existing valid examples and reject unrelated permissive widening. |
| 25 | `camera-csi2-provider-output-endpoint-schema` — `f152788e306d8cf21df0cb2e352ab502ed3b0b3569b00f627790091f203c7855` | Allows the provider output link to CAMSS without a `data-lanes` property; depends on row 23. Schema only. | Validate provider output and sensor input endpoints; ensure lane checks remain enforced on sensor inputs. |
| 26 | `soundwire-irq-clock-order` — `b9096e5b7cb9883d1f76fd271dd24729117b42d1020c65977c880dee9e881347` | Waits for the Qualcomm SoundWire interrupt thread before gating its clock; prerequisite to row 27. `CONFIG_SOUNDWIRE=m`, `CONFIG_SOUNDWIRE_QCOM=m`. | Build and exercise codec IRQ/clock activity; verify no lost interrupt or clock-off race during suspend/resume. |
| 27 | `soundwire-suspend-error-unwind` — `066e43af8fca58482755ce255ca621a524ce13b12024098d17775b3be05d14c0` | Restores controller IRQ state on both runtime-suspend error exits; follows row 26. Same SoundWire config. | Exercise both error exits (fault-injected where safe); verify IRQ state is balanced and audio returns after resume. |
| 28 | `pci-force-enable-link-state` — `5630cfce4228d61c1d51721a901ab3de92509750876cf6d5ff171d29ac87f996` | Adds a PCI API capable of overriding disabled ASPM states; prerequisite to rows 29 and 33. `CONFIG_PCI=y`, `CONFIG_PCIEASPM=y`. | API test must prove callers pass only supported/cached states; inspect and test the sole intended ath12k restore path. This row is subject to the owner-policy clarification below. |
| 29 | `pci-aspm-enabled-state-mask` — `dc14df10c68234c58c989bef6b0a6064d2ca56ce743da794bd219d5950e90f40` | Returns a state mask rather than a boolean, for row 33; depends on row 28. Same PCI config. | Verify reported state mask against hardware/core state and ensure restore cannot enable a state absent from the captured mask. |
| 30 | `wcn7850-disable-ltr` — `85e9fee5ca4e2f2e34e5f78f9340fad45c77b4898cbd7f0dcd9f29d831eddc36` | WCN7850-only LTR quirk intended to permit L1.2; applies only to PCI ID `17cb:1107`. `CONFIG_PCI=y`, `CONFIG_PCIEASPM=y`. | Confirm exact-ID scope, LTR state, link power state, Wi-Fi stability, and cold-resume behavior. Reject any effect on other Qualcomm PCI devices. |
| 31 | `sp12-pcie4-t-power-on` — `c909ee1fbc26e33e668fa6d18f6cec51982a5754bada5904251637144798e604` | Adds SP12 PCIe root-port power-on timing; depends on the Hamoa platform DTS in row 10. DTS only. | Compile/schema-validate DTB and verify the relevant link trains repeatedly without delaying or breaking unrelated ports. |
| 32 | `hamoa-pcie-opp-tables` — `fa4109ca8cce5690767dded3d6ff16b4c1de14768026eacbd57292adeac7d6ae` | Adds Hamoa PCIe operating points; depends on row 10 and OPP/regulator providers. DTS only. | Validate OPP tables against provider names/rates and measure link behavior/power on the target; reject unreviewed voltage/frequency changes. |
| 33 | `ath12k-aspm-api-adaptation` — `619d3da2c931f3bc18530db685be8653a8ba4a423045c215cdb914c6f7ddbb43` | Moves ath12k off direct LNKCTL writes and restores the previously captured ASPM mask through rows 28–29. `CONFIG_ATH12K=m`, `CONFIG_PCIEASPM=y`. | Verify disable/capture/restore around driver lifecycle and resume; prove no additional ASPM state is enabled. Owner must confirm this bounded restoration is allowed under the “no forced ASPM” instruction. |
| 34 | `ath12k-sp12-rfkill` — `9c7518b30be80933ac635a17c2dadbb6409f42542bc964a08648b7a2ac967755` | Skips the nonfunctional hardware-rfkill setup only for the SP12 compatible; depends on ath12k. `CONFIG_ATH12K=m`. | Verify Wi-Fi initializes and reconnects on SP12, rfkill remains effective through software controls, and other machines retain normal hardware rfkill. |
| 35 | `arm64-kexec-signature-force` — `b5d362252fc7c8d7ed4962f709dbc1f3709d5133bd0635ae84256e1cd35a69f1` | Local ARM64 signature-enforcement policy patch. `CONFIG_KEXEC_FILE=y`, `CONFIG_KEXEC_SIG_FORCE=y` in C. | In a disposable guest, verify the approved signed-kernel path and rejection of unsigned/invalid signatures; do not weaken lockdown or enroll keys. |
| 36 | `rpmb-core-serialize-teardown` — `f557cb4ab5b83eabd2a67f4c190be66a8d62b70b68c5ffcbc08b5c278bcc77ae` | Serializes RPMB requests and blocks new work during unregister; prerequisite to rows 37–38. `CONFIG_RPMB=m`. | Build and exercise provider register/unregister/request lifetime with non-writing test traffic. RPMB key provisioning and data writes are not authorized. |
| 37 | `ufs-rpmb-lifetime` — `c93d0f2ecfb870eb1f1a6f71da03357dd380afb6d2e32f2a73274e7f0071b28a` | Pins UFS RPMB WLUN/device references; depends on row 36 and UFS. `CONFIG_SCSI_UFSHCD=m`, `CONFIG_SCSI_UFSHCD_PLATFORM=m`, `CONFIG_RPMB=m`. | Exercise reference/unbind/error paths and confirm no use-after-free; do not write RPMB data or keys. |
| 38 | `ufs-rpmb-drop-unregistered-bus` — `3684292933c426ab616eb25846571ae95786a668dda746fe7b1c52036986f938` | Removes an unused bus that the pinned UFS source never registered; follows rows 36–37. Same UFS/RPMB config. | Verify no remaining consumer expects the bus and provider teardown still completes; no RPMB writes. |
| 39 | `usb-dwc3-skip-phy-management` — `3bb43b70da13e8d0de91bffafd21f3ace35d162ad679ef83eba8f9706ba479f8` | Lets USB core manage the QCOM DWC3 PHY where required; prerequisite to rows 40–42. `CONFIG_USB_DWC3=m`, `CONFIG_USB_DWC3_QCOM=m`. | Verify USB host/device role and PHY ownership across boot, role switch, and resume; reject double management or missing power transitions. |
| 40 | `usb-dwc3-eusb2-wake-irq-map` — `617bdca1b9429809b61104f10419b274407ea7866b90b57d8711a4000c5d858f` | Maps EUSB2 wake IRQ behavior in DWC3-QCOM; depends on rows 5, 8, and 39. `CONFIG_PHY_SNPS_EUSB2=m`, `CONFIG_USB_DWC3_QCOM=m`. | Validate wake IRQ mapping and USB resume from the relevant low-power state; reject spurious or unbalanced IRQs. |
| 41 | `usb-dwc3-wake-irq-failed-resume` — `020c77eb566572ef2b70b18aea11a94e063f180da6511f7fda93c0b799d60bdf` | Keeps wake-IRQ enable/disable balanced on failed resume; depends on rows 39–40. `CONFIG_USB_DWC3_QCOM=m`. | Inject/trigger the failed-resume path safely; verify IRQ depth is restored and a later successful resume works. |
| 42 | `usb-dwc3-wake-irq-runtime-pm` — `21fd94a37f22c9f46c57462db18d8a4f320e16c3a1177b8cbcc3c46e336c1045` | Balances wake IRQ handling in runtime-PM callbacks; depends on rows 39–41. `CONFIG_USB_DWC3_QCOM=m`. | Exercise repeated runtime suspend/resume and wake; reject IRQ-depth drift, lost wake, or USB failure. |
| 43 | `usb-hamoa-usb1-ss0-noc-clocks` — `81e98508745ac57f1ddc476844b7f312f479681bcd9757a6227629ddb333e112` | Adds required USB1 SS0 NoC clocks; depends on row 10 and clock providers. DTS only. | Validate DT and USB1 enumeration/transfer/resume on the target; reject a clock reference that remains unresolved or overbroad. |
| 44 | `video-iommu-ranges` — `09167da47080bac348e1b896a7ca4acb34e16697183da8a38f437b4fb6b1393a` | Adds `iommu-ranges` parsing used by Iris context-bank routing; prerequisite to rows 47–50. `CONFIG_IOMMU_SUPPORT=y`, `CONFIG_IOMMU_DMA=y`. | Validate range parsing, DMA/IOMMU attach, and failure handling; reject overlap, overflow, or changed mappings for unrelated devices. |
| 45 | `iris-context-bank-venus-common-schema` — `b05a6c29b8bb0cedc25e267c66a34209908da08875e6d115d4f118ec140f416f` | Defines common context-bank binding properties; prerequisite to rows 46–50. Schema only. | Run targeted binding checks and validate the Hamoa/SP12 DTB; reject undocumented schema relaxation. |
| 46 | `iris-context-bank-sm8550-schema` — `adb11a24eb8086a83aa4d1a21d917f86973366cbc60c6aca29ca0d12e76bfbfc` | Extends Iris context-bank binding for the applicable device family; follows row 45. Schema only. | Run `dt_binding_check`, `yamllint`, and DT validation against in-scope examples. |
| 47 | `iris-context-bank-devices` — `be32a134065c3a1c6abea5489806dfbecab265a51aa51650680560cc69f2b052` | 7.3.5 rebase that creates Iris pixel/non-pixel context-bank devices; depends on rows 44–46. `CONFIG_VIDEO_QCOM_IRIS=m`, `CONFIG_IOMMU_DMA=y`. | Build/probe and verify both child devices, cleanup on partial failure, and correct IOMMU attachment; hardware decode is still required for feature acceptance. |
| 48 | `iris-buffer-context-bank-routing` — `6767b9761ba036b26476cdef2542549571534067e1a527bc7758fe74eadb5659` | Routes pixel/non-pixel buffers to their matching context bank; depends on row 47. `CONFIG_VIDEO_QCOM_IRIS=m`. | Verify allocation/map/unmap routes for both classes and no cross-bank use; require decoded output with software fallback excluded. |
| 49 | `iris-parent-dma-mask-no-iommu` — `7b1eae848eb485769613a2319b23fe1d8390f49a87727c10d319836280ac18be` | Avoids configuring a parent DMA mask when the Iris core has no IOMMU; depends on row 47. `CONFIG_VIDEO_QCOM_IRIS=m`, `CONFIG_IOMMU_DMA=y`. | Exercise IOMMU-present and absent/error paths without corrupting the device DMA mask; require hardware probe/decode on the real target. |
| 50 | `hamoa-iris-context-bank-dts` — `2831956d97d92bf5781f04edb03318accf2bfb525ce800df0001645011e885b7` | Adds Hamoa Iris context-bank child nodes; depends on rows 10 and 44–49. DTS only. | Compile/schema-validate the DTB and verify the running device tree exposes exactly the expected child nodes. |
| 51 | `wcn7850-hci-qca-drop-unused-event` — `e4ca052e5046370ce92e3a4532b4e750cc04268c39c39a3dd1130fbf1d1d34fb` | Drops an unused WCN7850 HCI event; depends on the QCA Bluetooth path. `CONFIG_BT=m`; C enables ath12k/WCN support. | Pair, reconnect, and sustain Bluetooth traffic; reject missing required events or regressions to Wi-Fi coexistence. |
| 52 | `arm-arch-timer-park-stopped` — `601f591f755cd0bc4fc6a5ae4e5b4b0d58ccbb522b94a9123516668f8237b663` | Parks stopped ARM architected timers; applies to the ARM arch timer. `CONFIG_ARM_ARCH_TIMER=y`. | Validate timer progression, wake sources, and repeated SP12 deep resume; reject timekeeping drift or lost wake. |

## Shared and packaging patches

| Apply order | Patch — SHA-256 | Purpose / dependency / config | Acceptance and rejection test |
|---|---|---|---|
| SP12 53; B550I 1 | `shared-bore-scheduler` — `d2eaa8e8dbf1f56bfb304f8b437a7dc30a65408f90a93701367baf8adc2173b4` | Shared BORE scheduler implementation; owner requires BORE on both targets. `CONFIG_SCHED_BORE=y` in both C configs. | Build and run matched, multi-process scheduler/audio-workload tests; check responsiveness, fairness, and regressions. Do not run a BORE-vs-EEVDF comparison or claim performance benefit without measurements. |
| SP12 54; B550I 2 | `shared-slub-canary` — `ef912876e259d95321778268f3ec448932f2f76778b3092d38b694e75aa51f17` | SLUB canaries; depends on SLUB and disabled default slab merging. Both C configs have `CONFIG_SLUB=y`, `CONFIG_SLAB_CANARY=y`, and `CONFIG_SLAB_MERGE_DEFAULT` unset. | Build/config audit, allocator selftests and controlled non-destructive canary checks; measure overhead. Do not deliberately corrupt a production/physical kernel. |
| SP12 55; B550I 5 | `ubuntu-package-dependencies.patch` — `d938c88ddd54d285b44b0b0a7c352e0d77f568343edde9bd5b6708edbc842b55` | Adds explicit kernel image/header/initramfs and toolchain package dependencies; follows kernel patching. No kernel Kconfig. On B550I this is packaging patch 3 and follows DKMS/header-config patches 1–2. | Inspect generated `DEBIAN/control`; resolve the full offline package closure and test install/remove in a disposable root. |
| SP12 56 | `07-ubuntu-2610-debhelper-compat.patch` — `c266d89141be66eafc8b24d72362a173dfffc19bd613df5751ef49764bc581ca` | Keeps Debian packaging compatible with Ubuntu 26.10 debhelper while preserving compat level 12. No kernel Kconfig. | Build binary packages with the pinned debhelper; inspect generated control/compat metadata and repeat package audits. |
| SP12 57 | `08-cross-build-header-tools.patch` — `3e9f522ec06ad7e0ecba25e237189cc5575028e5720ec399511e329383f7e63b` | Makes external-module header packages usable for cross builds (host tools, `sign-file`, BTF resolver, host linker/config). No runtime Kconfig. | Install headers in an isolated ARM64 root and build/sign a minimal out-of-tree module with the pinned cross toolchain; verify config, vermagic, symbols, and BTF tool behavior. |
| B550I 3 | `dkms-clang.patch` — `1e543f84690f7935c7dcd927d785b032561e7caa789d5d114e91b3798b1b1663` | Relaxes several Clang `-Werror` checks for kernel/DKMS builds. No Kconfig. Risk: also weakens compile diagnostics outside NVIDIA DKMS; it is not a runtime patch. | Preserve full warnings and review newly nonfatal diagnostics; rebuild the signed NVIDIA DKMS modules against the exact headers, verify signatures/load, then test actual RTX 4070 acceleration. |
| B550I 4 | `headers-config.patch` — `3fbfe37888f961f1cc3cd8278600851b56047b791270fc66f0b3d8fab33d60d9` | Copies the effective `.config` into packaged headers for external modules; follows DKMS compiler support. No Kconfig. | Compare packaged header `.config` byte-for-byte to the pinned resolved config and rebuild NVIDIA DKMS from that package. |

The B550I manifest intentionally excludes all Surface/ARM64/Qualcomm/camera/
SoundWire/USB/PCIe/Iris platform entries. Its effective config is AMD64
`znver3`; `CONFIG_RUST` is disabled. The SP12 config retains BORE, SLUB
canaries, stack erasure, init-on-free, 4 KiB pages, forced module-signature
policy, and the selected ARM64 kexec signature policy. These are config
observations, not proof of every runtime enforcement path.

## Separate SP12 fixes and support candidates

These are not additions to the selected 52-entry C manifest. The private
diagnostic manifest described above carries two kernel candidates; the
libcamera and audio support are separate userspace layers.

| Candidate | Exact identity | Dependency/config | Required acceptance / current limit |
|---|---|---|---|
| Purwa CSID lane-map | `targets/sp121-arm64/patches/r2/camera/11-purwa-csid-dt-lane-normalization-candidate.patch`, SHA-256 `9fdd246557106016f5753172df15b1dfbacba7156af7141e86b81969d71fcf2d` | Depends on the C CSI-2 PHY/CAMSS/sensor graph, especially C rows 13–25. `CONFIG_VIDEO_QCOM_CAMSS=m`. | `camss-csid.o` compiled in isolation; not hardware-proven. Test alone against C with unchanged userspace and DT lane graph; require both real sensors to produce 30 consecutive buffers through the intended application after cold boot and resume. It is distinct from C row 14. |
| Iris firmware-name | `iris-firmware-name.patch (private evidence)`, SHA-256 `57431896e63d17f43325d21c9bddff6ed8d8275e61f3b9073791f822cab32b17` (candidate input path is retained in the private SP12 build context) | Depends on Iris rows 47–50 and a legal, trusted firmware file at the requested path. `CONFIG_VIDEO_QCOM_IRIS=m`. | The DTB compiled; no successful Iris initialization or hardware decode is established. Verify firmware hash, issuer/use terms, exact request path, successful initialization and hardware decode with software fallback excluded. Keep the owner-supplied MSI-derived payload private; do not include it in a distributable image without rights review. |
| OV02C10 libcamera helper | Patch SHA-256 `4a39b15e302728c7d5b90c9229b6528f8495152ea7672b5f12d56a96d91b9244`; package version `0.7.0-1ubuntu2+sp12.1` | Userspace package layer; independent of both lane-map kernel fixes. | Helper-creation failure disappeared in the recorded A/B, but neither sensor delivered frames. Keep as a separate candidate; repeat same-userspace capture A/B and require both sensors to stream through the supported camera application. |
| SP12 audio support | Existing pinned UCM/topology in `config/sp121-live-support.json`, SHA-256 `74f2ec3de0e43c3c438c95f02ac4b919883d9e0d83fc791fe60ce62a411d66c1` | Retain unchanged alongside the SoundWire C patches. No verified corrective kernel patch identified. | Diagnose explicit ALSA versus PipeWire routes; prove audible left/right output and changing built-in mic signal, then repeat after resume. Prior `auto_null`/zero-byte observations are not a fix. |

## Enhancement leads, exclusions, and unresolved owner decisions

The owner handoff moves selected enhancements before stable but explicitly does
not approve every lead. The following are **not silently declared rejected or
already present**:

| Lead outside current C | Current contract treatment | What is still needed before inclusion/exclusion can be closed |
|---|---|---|
| SP12 panel `0007`, PCIe PHY reset `0011` / `910b828b22b7`, ath12k restart `0012` | Exact-source checks below find the panel and PCIe PHY changes already in the pinned CachyOS tree; the ath12k restart-accounting fix is absent. None is an entry in the 52-row C manifest. | Record the owner's per-lead disposition. For any change selected, pin the exact candidate and provenance/license, then run its discriminating target test. Keep the PCIe PHY reset check separate from C's ASPM rows 28–34. |
| Shared allocator additions (wrong-cache/non-slab checks, sanitization, constructor behavior) and memory-layout/metadata leads | No additional patch is pinned. Existing C already has SLUB canary, stack erasure, init-on-free, and related selected config; that does not establish every proposed mitigation. | Do not import a broad hardened tree. Pin each exact candidate, map config/runtime coverage and dependency family, assess DMA/cache/tagging effects, and obtain a per-change decision/test. |
| B550I CPPC/P-state, futex/reclaim/block/locking, AutoFDO/Propeller | Not in current C; no concrete patch revision selected. | Establish exact upstream status and B550 workload benefit/risk. AutoFDO/Propeller need representative profiles. Exclude dual-CCD/Zen4+ tuning on the znver3 target. |
| SP12 SCMI MEMLAT, ICC/BWMON, devfreq/CPUFreq, RPMh/PSCI idle, energy model | No exact candidate pinned; not assumed present from generic config. | Verify Purwa firmware and driver maturity, Oryon compiler targeting, thermal safeguards, and measured AC/battery effect before owner selection. No Hamoa-only assumptions, SS1 reopening, arbitrary voltage changes, or new forced ASPM. |
| Runtime/userspace policy changes (BPF/perf, ptrace, dmesg, namespace, service isolation, USBGuard, integrity) | Not part of these kernel patch manifests. | Review Ubuntu defaults and preserve profiling, AppArmor, rootless/container and sandbox compatibility; make installed-system policy separate from live-only policy. |
| KCFI/FineIBT, RANDSTRUCT, fail-stop policy, broad PGO/compiler/page-size changes, LKRG, EL2/slbounce/qebspil, production sanitizers, wholesale scripts, installer/encryption redesign | Explicitly outside this C contract unless the owner opens a separate review. | No addition by implication; any proposed exception requires a separate risk, compatibility, fallback, and test decision. |
| Existing ath12k ASPM restoration | C rows 28–29 add an API that can override disabled states; row 33 caches and restores the previously active mask after ath12k disables ASPM. It calls `pci_force_enable_link_state()`. | Owner permits restoration of previously active states only. Verify the restored mask adds no states and test Wi-Fi and resume. No broader forced ASPM. |
| B550I Clang warning relaxation | Already present in B550I C packaging, not a new runtime feature. | Review warning output and NVIDIA DKMS compatibility together; if a safer narrower change exists, record a superseding candidate rather than weakening the policy invisibly. |

### Exact-source checks for the three SP12 reliability leads

Checked the source files at the pinned CachyOS commit
`1ac42d4fa557ecd640dd7283d1be49e1ad526492` (the 7.3.5-2 source identity above).
These checks establish source presence only; they do not establish module
packaging, runtime activation, or hardware behavior.

| Lead | Pinned-source result | Scope and remaining evidence |
|---|---|---|
| Panel `0007` | `drivers/gpu/drm/panel/panel-edp.c`, blob `2b455369ed7005d4fd5bb4f71f01b51bfd3c06b6`, contains `SHP 0x15a7` / `LQ120P1JX51` with `delay_200_500_e200`. This is the entry from upstream commit [`6ed8d820cea9`](https://github.com/torvalds/linux/commit/6ed8d820cea9cae226f500d3af86e156eede27f6). | C has `CONFIG_DRM_PANEL_EDP=m`. Do not add the reference `0007` entry as though it were missing; its older local hunk uses a different delay. Still verify the module is in the final initramfs/package and that the SP12 EDID binds to this entry without the unknown-panel fallback. |
| PCIe PHY reset `0011` | `drivers/phy/qualcomm/phy-qcom-qmp-pcie.c`, blob `da83358c97ead1ebe91d5051303b49745e8727dc`, has the upstream [`910b828b22b7`](https://github.com/torvalds/linux/commit/910b828b22b7b91054b3bd4be676a017444b0e00) `skip_reset` logic in both `qmp_pcie_init()` and `qmp_pcie_power_on()`, including guards around no-CSR reset assert/deassert. | C has `CONFIG_PHY_QCOM_QMP_PCIE=m`. This is present in source and distinct from ASPM policy. It is conditional on `skip_init` and PHY status; verify the target reaches that condition and retains a working link over repeated cold boots/resumes before calling the SP12 reliability issue closed. |
| ath12k restart `0012` | `drivers/net/wireless/ath/ath12k/mac.c`, blob `a997e888feb5656d912384af46befc8239717297`, still unconditionally increments `ar->num_started_vdevs` in `ath12k_mac_vdev_start_restart()`. The `if (!restart)` elsewhere in that function guards MLO argument setup, not this counter. The proposed fix is Birk Skyum's [20 October 2026 mailing-list patch](https://lkml.rescloud.iu.edu/2610.2/11945.html), which increments only when `restart` is false and reports a WCN7850 test. | The counter fix is absent from this pinned source; C has `CONFIG_ATH12K=m`. The mailing-list submission is a candidate, not a merged/pinned C change. Owner disposition, exact candidate-byte/provenance and license review, and an actual WCN7850 channel-switch/statistics test remain required. Do not treat source inspection or the reported external test as SP12 qualification. |

## Gate 1 disposition

**BLOCKED for both targets.** Exact selected C manifests/configs and the
private diagnostic delta are reconciled, patch digests are pinned, and the
source-signer identity evidence is now assessed. Gate 1 is not closed because:

1. Restore-only ASPM is permitted; its scope and target behavior still need verification.
2. The owner selected an isolated trial of the absent ath12k restart fix,
   not release inclusion. Pin/review bytes and provenance, then compare channel
   switches and counters on SP12. Prepare one bounded shortlist for the wider
   groups; defer speculative leads and record final membership after review.
3. The CSID fix, Iris firmware-name fix, and libcamera helper remain distinct
   unproven candidates; the firmware rights gate remains open.
4. Patch authorship/license/DCO/redistribution review remains open for private
   inputs; public redistribution stays prohibited.

Do not start package/ISO successor work from this review alone. Once the owner
resolves the outstanding selection/policy items, freeze a reviewed manifest,
config, dependencies, and acceptance tests for each target; preserve the
current C inputs and use a new candidate identity for any changed bytes.
