# Installation rapide (avec une carte SD prête à l'emploi)
par Loïc Cuvillon

*[(English version here)](Quick_installation.md)*

Ce guide de démarrage rapide configure le TurtleBot3 et le PC pour le suivi de ligne, en utilisant une caméra avec le paquet ROS `v4l2_camera`.

Il suit le [manuel officiel](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup) pour installer ROS Humble, mais propose une alternative bien plus rapide pour configurer la Raspberry Pi (RPi) du TurtleBot3 : une image de carte SD prête à l'emploi.

**Sommaire**
1. [Installation du PC](#1-installation-du-pc)
2. [Installation de la RPi du TurtleBot3](#2-installation-de-la-rpi-du-turtlebot3-configuration-sbc-et-opencr)
3. [Sauvegarder la carte SD](#3-sauvegarder-la-carte-sd)
4. [Tests de base du TurtleBot3](#4-tests-de-base-du-turtlebot3)


## 1. Installation du PC
Suivez le guide de démarrage rapide officiel de Robotis pour configurer un PC sous Ubuntu 22.04 avec ROS 2 Humble :
- [quick_start_guide/pc_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/pc_setup)

> **Remarque :** à l'étape correspondante, installez à la fois ROS 2 Humble Desktop et les outils de développement ROS :
> ```sh
> sudo apt install ros-humble-desktop
> sudo apt install ros-dev-tools
> ```

Installez ensuite quelques outils utiles :
- `rpi-imager`, pour écrire la carte SD :
    ```sh
    sudo apt install rpi-imager
    ```
- `terminator`, pour ouvrir plusieurs terminaux dans une même fenêtre divisée :
    ```sh
    sudo apt install terminator
    ```
- `codium` (VSCodium, la version open source de VS Code), pour éditer du code Python :
    ```sh
    sudo snap install codium --classic
    ```
    Lancez ensuite `codium` et installez l'extension Python (`ms-python.python`) pour l'édition avancée, la vérification de syntaxe en direct, le débogage, etc.


## 2. Installation de la RPi du TurtleBot3 (configuration SBC et OpenCR)
Il y a deux façons d'installer la Raspberry Pi du TurtleBot3 (le SBC, *single board computer*) :
- [Option A](#option-a--avec-une-image-de-carte-sd-prête-à-lemploi) : écrire une image de carte SD prête à l'emploi (recommandé, bien plus rapide),
- [Option B](#option-b--pas-à-pas-avec-le-manuel-robotis) : suivre les instructions pas à pas du manuel Robotis.

### Option A : avec une image de carte SD prête à l'emploi
Plutôt que de construire le système de la RPi pas à pas comme dans le manuel Robotis ([quick_start_guide/sbc_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/sbc_setup)), une image de carte SD prête à l'emploi est disponible. Elle contient Ubuntu 22.04, ROS 2 Humble, les paquets TurtleBot3, l'ancien pilote de caméra (*legacy*) et les outils caméra (V4L2) :

**Téléchargement :** [turtlebot3_humble_v4l2camera.img.gz](https://seafile.unistra.fr/f/882bc4b224e947a8a27d/?dl=1)

Somme de contrôle MD5 : `17adbbfc7703a4f99a9bbc24980356a7  turtlebot3_humble_v4l2camera.img.gz`

#### Écrire l'image sur la carte SD
1. Vérifiez que le téléchargement n'est pas corrompu : la commande suivante doit afficher la somme de contrôle ci-dessus.
    ```sh
    md5sum turtlebot3_humble_v4l2camera.img.gz
    ```
2. Décompressez l'image (environ 7,5 Go une fois décompressée) :
    ```sh
    gunzip -k turtlebot3_humble_v4l2camera.img.gz
    ```
3. Écrivez l'image sur la carte SD avec `rpi-imager` :
    - dans la fenêtre de Raspberry Pi Imager, choisissez *Operating System* > *Use custom* et sélectionnez le fichier décompressé `turtlebot3_humble_v4l2camera.img`,
    - choisissez votre carte SD comme *Storage* et écrivez l'image,
    - aucune personnalisation de l'OS n'est nécessaire.

#### Configuration réseau
Le réseau du TurtleBot3 (Wi-Fi ou filaire) se configure dans le fichier `/etc/netplan/50-cloud-init.yaml`. Ce fichier peut être modifié soit sur le TurtleBot3 lui-même, avec un écran et un clavier (méthode 1), soit directement sur la carte SD depuis le PC (méthode 2).

##### Méthode 1 : avec un écran HDMI et un clavier USB
- Comme détaillé dans [Configure the Raspberry Pi](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/sbc_setup#configure-the-raspberry-pi) :
    - insérez la carte SD dans la RPi,
    - branchez un écran à la RPi avec un câble HDMI, et branchez un clavier USB,
    - allumez le TurtleBot3 (**après** avoir branché le câble HDMI !).
- Connectez-vous avec l'utilisateur `ubuntu` et le mot de passe `turtlebot`.
- Le répertoire `/etc/netplan` contient 1 fichier normal et 2 fichiers cachés :
    ```sh
    ls -A /etc/netplan
    ```
    ```
    50-cloud-init.yaml  .50-cloud-init.yaml.dhcp  .50-cloud-init.yaml.static
    ```
    Les deux fichiers cachés sont des configurations toutes prêtes. Copiez celle dont vous avez besoin à la place de `50-cloud-init.yaml`, puis modifiez-la :

    - **a) DHCP** : votre point d'accès/routeur Wi-Fi dispose d'un serveur DHCP qui attribue automatiquement une adresse IP au TurtleBot3.
        ```sh
        cd /etc/netplan
        sudo cp .50-cloud-init.yaml.dhcp 50-cloud-init.yaml
        ```
        Modifiez ensuite le fichier : remplacez `c138proj` par le SSID de votre Wi-Fi et `password_here` par votre mot de passe Wi-Fi.
        ```sh
        sudo nano 50-cloud-init.yaml
        ```
    - **b) IP statique** : il n'y a pas de serveur DHCP, ou vous utilisez une connexion filaire (`eth0`).
        ```sh
        cd /etc/netplan
        sudo cp .50-cloud-init.yaml.static 50-cloud-init.yaml
        ```
        Modifiez ensuite le fichier : remplacez `c138proj` par le SSID de votre Wi-Fi, le mot de passe par votre mot de passe Wi-Fi, et les 3 adresses IP par celles que vous souhaitez respectivement pour le TurtleBot3, le serveur de noms (DNS) et la passerelle.
        ```sh
        sudo nano 50-cloud-init.yaml
        ```
        > Dans les fichiers YAML, l'indentation compte : utilisez des espaces (pas de tabulations) et conservez l'indentation existante.

- Appliquez la configuration réseau (pas besoin de redémarrer) :
    ```sh
    sudo netplan apply
    ```
    L'avertissement suivant est normal et peut être ignoré : `WARNING:root:Cannot call Open vSwitch: ovsdb-server.service is not running.`

- Dépannage :
    - `ip a` affiche la configuration IP actuelle des interfaces Wi-Fi (`wlan0`) et filaire (`eth0`),
    - `sudo netplan --debug apply` affiche des informations de débogage.

##### Méthode 2 : directement sur la carte SD, depuis le PC (sans écran ni clavier)
Un écran et un clavier peuvent tout de même être nécessaires pour déboguer une connexion réseau qui échoue.
- Insérez la carte SD (avec l'image déjà écrite) dans le PC Ubuntu. Ses partitions sont montées automatiquement, en général dans `/media/<votre_utilisateur_PC>/`.
- Dans la partition `writable`, modifiez le fichier `etc/netplan/50-cloud-init.yaml` comme détaillé dans la [méthode 1](#méthode-1--avec-un-écran-hdmi-et-un-clavier-usb) (copiez la configuration DHCP ou statique, puis modifiez le SSID, le mot de passe et les adresses IP) :
    ```sh
    cd /media/$USER/writable/etc/netplan
    ```
    puis utilisez les mêmes commandes `sudo cp` et `sudo nano` que dans la méthode 1.
- Éjectez la carte SD, insérez-la dans le TurtleBot3 et allumez-le.

#### Se connecter à distance au TurtleBot3
Connectez-vous au TurtleBot3 via le réseau depuis un terminal du PC, comme décrit dans [quick_start_guide/bringup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/bringup) :

1. Sur le PC, vérifiez que la RPi du TurtleBot3 est en ligne :
    ```sh
    ping 192.168.1.45
    ```
    Remplacez `192.168.1.45` par l'adresse IP statique que vous avez donnée au TurtleBot3, ou par l'adresse IP dynamique attribuée par votre routeur/point d'accès (elle se trouve dans l'interface web du routeur, ou avec `ip a` sur le TurtleBot3 avec un écran branché).
    Si le TurtleBot3 est connecté au réseau, le temps d'aller-retour de chaque paquet s'affiche. Arrêtez `ping` avec `Ctrl+C`.

2. Sur le PC, connectez-vous à distance au TurtleBot3 :
    ```sh
    ssh ubuntu@192.168.1.45
    ```
    Remplacez `192.168.1.45` par l'adresse IP du TurtleBot3, et `ubuntu` par l'utilisateur que vous avez créé si vous avez construit la carte SD vous-même.
3. Lorsqu'il est demandé, saisissez le mot de passe de l'utilisateur du TurtleBot3 (`turtlebot` pour l'image prête à l'emploi).

#### Mettre à jour la clé du dépôt ROS 2
La clé de signature des dépôts de paquets ROS 2 change de temps en temps. Si `sudo apt update` signale une erreur `NO_PUBKEY` ou `EXPKEYSIG` pour `packages.ros.org`, mettez à jour la clé sur la RPi avec :
```sh
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
sudo apt update
```

#### Mise à jour du firmware OpenCR (si nécessaire)
- Le dernier firmware (à la date de création de l'image) et un script de mise à jour sont déjà installés sur la carte SD.
    - Lancez la mise à jour du firmware OpenCR sur la RPi :
        ```sh
        cd ~/opencr
        bash update_opencr.bash
        ```
        Remarque : le script a besoin d'une connexion Internet pour installer des paquets logiciels.
    - Lorsqu'il vous est demandé quels services (*daemons*) redémarrer, sélectionnez simplement *OK*.
    - Environ 20 secondes après la fin de la mise à jour, la carte OpenCR doit jouer une courte mélodie pour confirmer la mise à jour.
- En cas de problème, consultez la page officielle : [quick_start_guide/opencr_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/opencr_setup).

#### .bashrc
Le fichier `~/.bashrc` du TurtleBot3 est déjà configuré comme l'attend le manuel :
```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export ROS_DOMAIN_ID=30 #TURTLEBOT3
export LDS_MODEL=LDS-01
export TURTLEBOT3_MODEL=burger
```
Si votre modèle de LiDAR n'est pas `LDS-01`, remplacez-le par `LDS-02` ou `LDS-03`. Rechargez ensuite le fichier avec `source ~/.bashrc` (ou ouvrez un nouveau terminal).

> **Important :** le PC doit utiliser le même `ROS_DOMAIN_ID` (30) que le TurtleBot3, sinon ils ne peuvent pas communiquer. La configuration du PC décrite dans le manuel ajoute `export ROS_DOMAIN_ID=30 #TURTLEBOT3` au `~/.bashrc` du PC.

### Option B : pas à pas avec le manuel Robotis
- Installez Ubuntu et ROS 2 Humble sur le SBC, en choisissant la méthode du paquet `v4l2_camera` pour la caméra de la RPi :
    - [quick_start_guide/sbc_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/sbc_setup) (voir la section *Raspberry Pi Camera*),
    - si `rqt_image_view` n'est pas disponible lors du test de la caméra, utilisez `rqt -s image_view`.
- Installez le firmware OpenCR :
    - [quick_start_guide/opencr_setup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/opencr_setup).


## 3. Sauvegarder la carte SD
Il est fortement recommandé de sauvegarder le contenu de votre carte SD une fois l'installation terminée.
La procédure est décrite dans [BackupRestore_SDCard.md](BackupRestore_SDCard.md) (en anglais).


## 4. Tests de base du TurtleBot3
Testez la communication entre le PC et le TurtleBot3, ainsi que l'environnement ROS 2, avec la téléopération de base du manuel :
- [Bringup](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/bringup)
- [Teleoperation (clavier)](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/teleoperation)

> **Astuce :** pour éviter de taper `export TURTLEBOT3_MODEL=burger` dans chaque nouveau terminal du PC, ajoutez cette ligne à la fin du fichier `~/.bashrc` du PC, comme sur le TurtleBot3 ([quick_start_guide/export_turtlebot3_model](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/export_turtlebot3_model)).

Dépannage :
- vérifiez que le PC et le TurtleBot3 utilisent **tous les deux** le même `ROS_DOMAIN_ID` (lancez cette commande dans un terminal sur chacun d'eux) :
    ```sh
    echo $ROS_DOMAIN_ID
    ```
- vérifiez que le PC et le TurtleBot3 sont sur le même réseau (voir [Se connecter à distance au TurtleBot3](#se-connecter-à-distance-au-turtlebot3)),
- vérifiez que les moteurs et la carte OpenCR fonctionnent correctement : [OpenCR test](https://docs.robotis.com/docs/systems/turtlebot3/quick_start_guide/opencr_setup#opencr-test),
- redémarrez le TurtleBot3.
