# Task 1.1 Spec — NFS Server on the Ubuntu Workstation

**Project:** Scale-Up Initiative, Phase 1
**Host:** Ubuntu workstation (Command & Dev Node, future K8s control plane)
**Clients:** Cluster subnet `10.0.50.0/24` (DGX Spark and any other cluster nodes)
**Status of this doc:** Authoritative spec for Task 1.1. Follow it in order. Deviations must be reported back before proceeding.

---

## 0. Scope and hard constraints

This task uses the **existing storage already present on the Ubuntu server**. It turns a directory on an existing filesystem into an NFS export. It does **not** create, resize, format, or partition anything.

**Guardrails — never do any of these during this task:**

- ❌ No `fdisk`, `parted`, `mkfs`, `wipefs`, `lvcreate`, `lvresize`, or any other partition/filesystem-creation command.
- ❌ No wildcard (`*`) entries in `/etc/exports`. Exports are scoped to `10.0.50.0/24` only.
- ❌ No deleting or moving existing user data to "make room".
- ❌ No firewall rules broader than what Section 5 specifies.
- ❌ Do not edit any files other than the ones this spec names.

If any step fails, stop and report the exact error output. Do not improvise around a failure.

---

## 1. Pre-flight inventory (read-only)

Run these and record the output. Nothing in this step modifies the system.

```bash
lsblk -f
df -h
findmnt -t ext4,xfs,btrfs
free -h
ip -br addr        # confirm which interface is on 10.0.50.x
cat /etc/exports 2>/dev/null
systemctl status nfs-server 2>/dev/null
```

**Decision point:** pick the existing mounted filesystem with the most free space to host the share. Typical outcomes:

- A dedicated data disk is already mounted (e.g. `/data`, `/mnt/storage`) → host the share there.
- Only the root filesystem exists → host the share on `/` **only if** it has comfortably more free space than the cluster will need (rule of thumb: keep ≥20% of root free after planned usage). If root is too small, stop and report — that becomes a hardware/storage decision for the user, not something to solve in this task.

Record the chosen filesystem and its free space before continuing.

---

## 2. Directory layout

Create the share root and its internal structure. If the chosen filesystem is not `/` itself, create the real directory there and bind-mount it to the canonical path so clients always see the same path.

Canonical export path: **`/mnt/ai_cluster_data`**

```bash
sudo mkdir -p /mnt/ai_cluster_data
```

If hosting on a separate existing filesystem (example: `/data`):

```bash
sudo mkdir -p /data/ai_cluster_data
echo '/data/ai_cluster_data  /mnt/ai_cluster_data  none  bind,nofail  0  0' | sudo tee -a /etc/fstab
sudo mount /mnt/ai_cluster_data
```

Internal structure (encodes the "NFS for shared data, local NVMe for hot model weights" policy):

```bash
sudo mkdir -p /mnt/ai_cluster_data/{datasets,checkpoints,results,shared-models,k8s-pv}
```

- `datasets/` — training/eval data shared across nodes.
- `checkpoints/` — fine-tuning checkpoints written by the DGX.
- `results/` — eval outputs, logs, artifacts.
- `shared-models/` — the *source of truth* copy of model weights. Nodes **copy** weights from here to local NVMe before serving; they do not run inference directly off NFS.
- `k8s-pv/` — reserved for Kubernetes dynamic provisioning (Task 1.3, `nfs-subdir-external-provisioner`).

Ownership and permissions:

```bash
sudo groupadd -f aicluster
sudo chown -R root:aicluster /mnt/ai_cluster_data
sudo chmod -R 2775 /mnt/ai_cluster_data   # setgid so new files inherit the group
```

Add the workstation's own user to `aicluster` (`sudo usermod -aG aicluster <user>`).

---

## 3. NFS server install and configuration (NFSv4-only)

```bash
sudo apt-get update
sudo apt-get install -y nfs-kernel-server
```

Make the server NFSv4-only (avoids rpcbind/portmapper and its dynamic ports). Edit `/etc/nfs.conf` — in the `[nfsd]` section set:

```ini
[nfsd]
vers3=n
vers4=y
vers4.1=y
vers4.2=y
```

Then disable the v3 helpers:

```bash
sudo systemctl mask rpcbind.service rpcbind.socket 2>/dev/null || true
```

---

## 4. Exports

Append exactly one line to `/etc/exports` (do not remove existing lines without asking):

```
/mnt/ai_cluster_data  10.0.50.0/24(rw,sync,no_subtree_check,root_squash)
```

Option rationale (do not change these without approval):

- `10.0.50.0/24` — cluster subnet only. Never `*`.
- `sync` — correctness over throughput; checkpoints must survive a server crash.
- `root_squash` — remote root maps to `nobody`. **Start here.** If Kubernetes provisioning later fails on permissions (Task 1.3), the documented escalation path is `anonuid`/`anongid` mapping to a dedicated user — not `no_root_squash`. Switching to `no_root_squash` requires explicit user approval.

Apply and enable:

```bash
sudo exportfs -ra
sudo systemctl enable --now nfs-server
sudo exportfs -v
```

---

## 5. Firewall

NFSv4-only needs a single port. If `ufw` is active:

```bash
sudo ufw allow from 10.0.50.0/24 to any port 2049 proto tcp
```

If `ufw` is inactive, note that in the report and add nothing. Do not open port 111 (that's NFSv3/rpcbind, which we disabled).

---

## 6. Verification and acceptance criteria

Task 1.1 is **not complete** until every box below is checked. Server-side checks alone do not count as done.

**Server-side:**

- [ ] `sudo exportfs -v` shows `/mnt/ai_cluster_data` exported to `10.0.50.0/24` with `rw,sync,root_squash`.
- [ ] `systemctl is-enabled nfs-server` → `enabled`; `systemctl is-active nfs-server` → `active`.
- [ ] `ss -tlnp | grep 2049` shows nfsd listening; nothing listening on 111.

**Client-side (from the DGX or any other host on 10.0.50.x):**

```bash
sudo mkdir -p /mnt/cluster
sudo mount -t nfs4 -o hard,noatime <server-ip>:/mnt/ai_cluster_data /mnt/cluster
echo "nfs-ok $(date -Is)" | tee /mnt/cluster/results/mount-test.txt
cat /mnt/cluster/results/mount-test.txt
sudo umount /mnt/cluster
```

- [ ] Mount succeeds, write succeeds, file is readable back on the server at `/mnt/ai_cluster_data/results/mount-test.txt`.

**Reboot persistence:**

- [ ] After a server reboot (or `sudo mount -a && sudo exportfs -ra` as a dry check), the bind mount (if any) and the export both come back without manual steps.

If no second host is available yet, mark the client-side checks **DEFERRED — pending first cluster node**, state that explicitly in the report, and do not report Task 1.1 as verified.

---

## 7. Client mount policy (for later tasks, record now)

When cluster nodes mount this share permanently:

- Use `hard,noatime` for `datasets/` and `checkpoints/` (a `soft` mount can silently corrupt checkpoint writes during a server hiccup).
- Always add `nofail` (and consider `x-systemd.automount`) in client fstab entries so a workstation reboot doesn't hang DGX boot.
- Known limitation to keep in the blueprint: this workstation is a single point of failure for control plane + storage + dev. Accepted for now; revisit in a later phase.

## 8. Rollback

To fully undo this task: remove the line from `/etc/exports`, `sudo exportfs -ra`, `sudo systemctl disable --now nfs-server`, remove the ufw rule and the fstab bind-mount line, and unmount `/mnt/ai_cluster_data`. Data written into the share directory is left in place.
