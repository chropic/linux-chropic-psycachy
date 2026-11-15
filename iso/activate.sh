#!/usr/bin/env bash
# Interactive front end for the retained candidate-trial state machine.
set -Eeuo pipefail
IFS=$'\n\t'
export LC_ALL=C
die() { echo "PsyCachy activation: $*" >&2; exit 1; }
(( EUID == 0 )) || die 'run as root in an interactive terminal'
[[ -t 0 && -t 1 ]] || die 'an interactive terminal is required'
[[ -f /var/lib/psycachy/installer-packages-ready ]] || die 'installer package setup is incomplete'
helper=/usr/local/lib/psycachy/psycachy-secureboot.sh
trial=/usr/local/sbin/phase2-kernel-trial
keydir=/var/lib/psycachy/secureboot
[[ -f $helper && -x $trial && -f $keydir/kernel.pem && -f $keydir/module.der ]] || die 'activation helpers or local signing certificates are missing'
state_file=/var/lib/psycachy/kernel-trial.json

state=$(mokutil --sb-state) || die 'could not determine Secure Boot state'
case $state in
  'SecureBoot enabled') secure=true ;;
  'SecureBoot disabled'|$'SecureBoot disabled\nPlatform is in Setup Mode') secure=false ;;
  *) die "unexpected Secure Boot state: $state" ;;
esac
if $secure; then
  if ! bash "$helper" check; then
    pending=$(mokutil --list-new) || die 'could not inspect pending MOK enrollments'
    [[ -z $pending ]] || die 'a MOK enrollment is already pending; complete it at reboot before retrying'
    echo 'Enroll the two local PsyCachy certificates. MOK Manager will ask for the password at reboot.'
    read -r -p 'Type ENROLL to request enrollment: ' answer
    [[ $answer == ENROLL ]] || die 'enrollment was not requested'
    bash "$helper" enroll
    echo 'Restart and complete enrollment in MOK Manager, then run activation again.'
    exit 0
  fi
  trust=/sys/firmware/efi/efivars/MokListTrustedRT-605dab50-e046-4300-abb6-3dd810dd8b23
  if [[ ! -e $trust ]]; then
    echo 'PsyCachy requires the kernel to trust all enrolled MOKs. Review the list first:'
    mokutil --list-enrolled --short
    read -r -p 'Type TRUST to request trust for all enrolled MOKs: ' answer
    [[ $answer == TRUST ]] || die 'MOK trust was not requested'
    bash "$helper" trust-mok
    echo 'Restart and complete the trust request in MOK Manager, then run activation again.'
    exit 0
  fi
fi

if [[ ! -e $state_file ]]; then
  echo 'This begins the one-boot trial. Ubuntu remains the saved default until explicit promotion.'
  read -r -p 'Type PREPARE to schedule the pinned candidate once: ' answer
  [[ $answer == PREPARE ]] || die 'candidate trial was not prepared'
  machine_id=$(cat /etc/machine-id)
  fallback=$(cat /var/lib/psycachy/fallback-release)
  mode=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["mode"])' /var/lib/psycachy/activation-mode.json)
  args=(prepare --pin /var/lib/psycachy/amd64-kernel-pin.json \
    --packages /var/lib/psycachy/candidate-packages \
    --expected-machine-id "$machine_id" --fallback-release "$fallback")
  case $mode in
    first-install) args+=(--first-install) ;;
    replacement)
      mode_json=/var/lib/psycachy/activation-mode.json
      args+=(--backup-manifest "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["backup"]["manifest_path"])' "$mode_json")" \
        --backup-manifest-sha256 "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["backup"]["manifest_sha256"])' "$mode_json")" \
        --approved-backup-volume-id "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["backup"]["volume_id"])' "$mode_json")") ;;
    *) die 'installer activation mode is missing or unknown' ;;
  esac
  "$trial" "${args[@]}"
  echo 'Restart to run the candidate once. Ubuntu remains the saved fallback.'
  exit 0
fi

trial_state=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["state"])' "$state_file")
case $trial_state in
  pending)
    if [[ $(uname -r) != "$(cat /var/lib/psycachy/pending-kernel)" ]]; then
      echo 'The candidate has not booted yet. Restart to run its one-time trial.'
      exit 0
    fi
    echo 'Run your physical health checks before acknowledging this candidate.'
    read -r -p 'Type ACKNOWLEDGE after the candidate checks pass: ' answer
    [[ $answer == ACKNOWLEDGE ]] || die 'candidate was not acknowledged'
    "$trial" acknowledge
    trial_state=acknowledged
    ;;
  acknowledged)
    echo 'The candidate is acknowledged; the Ubuntu fallback remains the saved default.'
    read -r -p 'Type ROLLBACK to restore Ubuntu, or TEMPLATE to prepare promotion review: ' action
    if [[ $action == ROLLBACK ]]; then
      "$trial" rollback
      exit 0
    fi
    [[ $action == TEMPLATE ]] || die 'choose rollback or promotion review'
    "$trial" attestation-template
    read -r -p 'Reviewed health attestation path (blank to stop): ' attestation
    [[ -n $attestation ]] || attestation=/var/lib/psycachy/attestations/health-attestation.json
    "$trial" promote --attestation "$attestation"
    echo 'Candidate promoted. The fallback remains available; rollback is still supported.'
    ;;
  promoted)
    echo 'Candidate is promoted; Ubuntu remains available as the verified fallback.'
    read -r -p 'Type ROLLBACK to restore Ubuntu as the saved default and reboot: ' answer
    [[ $answer == ROLLBACK ]] || die 'rollback was not requested'
    "$trial" rollback
    ;;
  *) die "trial state is $trial_state; inspect status and resolve it before activation" ;;
esac
