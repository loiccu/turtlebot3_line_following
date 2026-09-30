# Raspberry Pi SD Card Backup and Restore
(Author: L. Cuvillon)

This guide explains how to save a Raspberry Pi (RPi) SD card into an image file, and how to restore this image to an SD card, using a Linux computer.

**Contents**
1. [Back up the SD card](#back-up-the-sd-card)
2. [Restore the image](#restore-the-image)
3. [Mount the image locally to edit it](#mount-the-image-locally-to-edit-it)
4. [Check the SD card health](#check-the-sd-card-health)

> **Warning:** `dd` and `badblocks` write directly to the device you give them. A wrong device name (for example your computer's own disk instead of the SD card) will **erase it**. Always double-check the device name before running these commands.


# Back up the SD card
1. Plug the SD card into the computer.
2. Find the disk device of the RPi SD card. It has two partitions: a small boot partition (label `bootfs` on Raspberry Pi OS, `system-boot` on Ubuntu) and a large root partition (label `rootfs` on Raspberry Pi OS, `writable` on Ubuntu):
```shell
lsblk -o NAME,SIZE,LABEL,MOUNTPOINT
```
The partitions share a common base device, for example `/dev/sdc` (partitions `/dev/sdc1` and `/dev/sdc2`). Its size should match the size of your SD card.

3. Unmount the partitions.
    **Replace `sdc` below with your device name!**
```bash
sudo umount /dev/sdc1
sudo umount /dev/sdc2
```
If a partition was not mounted, `umount` reports an error, which can be ignored.

4. Create an image of the entire SD card (replace `sdc` with your device name, and the image name with a name of your choice):
```bash
sudo dd bs=4M if=/dev/sdc of=./tb3_rpi4_humble.img status=progress
sync
```
The image has the size of the whole SD card (for example 32 GB), even if most of it is empty. The next section shows how to reduce it.

## Shrink the image (using PiShrink)
[PiShrink](https://github.com/Drewsif/PiShrink) will:
* remove the unused space from the image, to reduce the file size;
* create or modify `/etc/rc.local` in the image, so that the filesystem is automatically expanded to the full SD card size on the next boot.

### Install PiShrink
```bash
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
sudo mv pishrink.sh /usr/local/bin
```

**For safety, review the script before running it with `sudo`.**

### Shrink and compress the image
1. Shrink the image:
```bash
sudo pishrink.sh tb3_rpi4_humble.img
```

2. Create an MD5 checksum, to be able to check the image integrity later:
```bash
md5sum tb3_rpi4_humble.img > tb3_rpi4_humble.img.md5
```

3. Compress the image (it creates `tb3_rpi4_humble.img.gz` and deletes the original `.img` file):
```bash
gzip tb3_rpi4_humble.img
```
Note: add the `-k` option to keep the original file.

4. (Optional) Remove PiShrink:
```bash
sudo rm /usr/local/bin/pishrink.sh
```


# Restore the image
1. Decompress the image (`-k` keeps the compressed file):
```shell
gunzip -k tb3_rpi4_humble.img.gz
```

2. Verify the checksum (optional but recommended). The `.md5` file must be in the same folder as the image:
```shell
md5sum -c tb3_rpi4_humble.img.md5
```
It should display `tb3_rpi4_humble.img: OK`.

3. Write the image to the SD card, with one of the two options below.

**Option 1: GUI with Raspberry Pi Imager** (recommended)
```bash
sudo snap install rpi-imager
```
Then launch the application and select:
- Device: your Raspberry Pi model (e.g. Raspberry Pi 4),
- Operating System: *Use custom*, then select the `.img` file,
- Storage: your SD card,
- no OS customization is needed.

**Option 2: command line**

Replace `sdc` below with the device name of your SD card (see step 2 of [Back up the SD card](#back-up-the-sd-card)):
```bash
sudo umount /dev/sdc1
sudo umount /dev/sdc2
sudo dd bs=4M if=tb3_rpi4_humble.img of=/dev/sdc status=progress
sync
```
Wait for `sync` to return before removing the SD card.


# Mount the image locally to edit it
This lets you change the content of the image without writing it to an SD card and backing it up again. It works on the uncompressed `.img` file: decompress it first if needed (see step 1 of [Restore the image](#restore-the-image)).

1. Find the start sector of the second (root) partition:
```bash
fdisk -l tb3_rpi4_humble.img
```
In the output, read the `Start` column of the second partition (the line starting with `tb3_rpi4_humble.img2`, of type `Linux`).

2. Compute the partition offset in **bytes**: offset = start sector × 512 (the sector size, given as `Units` by `fdisk`). Then mount the partition:
```bash
sudo mount -o loop,rw,sync,offset=269484032 tb3_rpi4_humble.img /mnt/
```
In this example, the start sector is 526336, so the offset is 526336 × 512 = 269484032. Replace this value with the one computed for your image.

3. The partition content is now available in `/mnt/`. When you are done, unmount it before using or compressing the image:
```bash
sudo umount /mnt
```
The image content has changed, so its old `.md5` checksum is no longer valid: create a new one (see step 2 of [Shrink and compress the image](#shrink-and-compress-the-image)).


# Check the SD card health
`badblocks` writes patterns on the SD card and reads them back to check its health.
Use it if you suspect defects on the SD card, for example after a filesystem corruption.

Replace `sdc2` below with the partition to test (see step 2 of [Back up the SD card](#back-up-the-sd-card)). The partition must be unmounted before the test.

**Warning:** the write-mode test (`-w`) is **destructive**: it erases all the data on the partition.

- Destructive read-write test (erases the data):
```shell
sudo badblocks -wsv /dev/sdc2
```
- Non-destructive read-write test (slower, keeps the data, but back up the SD card first in case of a problem):
```shell
sudo badblocks -nsv /dev/sdc2
```
