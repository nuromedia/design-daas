# Design

This project focuses on a novel approach to Desktop-as-a-Service (DaaS) solutions,
enabling seamless deployment of unmodified Linux and Windows desktop applications.
Unlike traditional methods, this solution allows users
to interact with applications entirely through a browser,
eliminating the need for additional client software.
The contained source code was created during a research project
and represents a prototypic state of implementation.
It still contains some rough edges,
so be warned and don't use it in productive environments!

______________________________________________________________________

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Acknowledgments](#acknowledgments)
5. [Resources](#resources)

______________________________________________________________________

## Features

- Enables deployment of unmodified Linux and Windows applications
- Integration of Virtual Machines and Containers (by using Proxmox and Docker)
- Browser-based user interaction (by using Guacamole as a Desktop Gateway)
- Dedicated user frontend [Repo: Frontend](https://github.com/nuromedia/design-daas-application-frontend)
- Dedicated authentication backend [Repo: Backend](https://github.com/nuromedia/design-daas-application-backend)

## Installation

The installation depends on Debian12 and several additional components and libraries.
A Makefile with all installation steps is provided in the "installer" folder.
Use it to install all components seperately.

- [Video: Installation](https://www.youtube.com/watch?v=-AUCHX9SRKE)

### Prerequisites

#### Supported Operating Systems (Host)

- Debian12

#### Utilized Libraries and Tools

- Guacamole
- Proxmox
- qemu-kvm
- docker.io
- Python 3.11+

#### Clone the repository

```bash
git clone git@github.com:nuromedia/design-daas.git
```

#### Install Custom Proxmox Kernel

```bash
cd installer
export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111
make proxmox-install
shutdown -r now
```

#### Install Proxmox

```bash
cd installer
export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111
make proxmox-install
```

#### Install Design Platform

```bash
cd installer
export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111
make daas-all STANDALONE=yes
```

#### Install Design Service Containers

```bash
cd installer
export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111
make daas-services
```

#### Install Design Templates

```bash
cd installer
export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111
make daas-containers # Baseimages Docker
make proxmox-isogen  # Baseimages VM
```

#### Install Frontend

```bash
cd installer
export HOST_NAME=pve HOST_DOMAIN=cluster.local HOST_IP=10.0.2.15 HOST_NUMBER=111
make frontend-all
```

## Usage

The installer creates systemd targets for daas nginx and the frontend.
Use systemctl or comparable alternatives to control them.
By default, nginx is used as a proxy to host the daas application on the default port 443 and the frontend on 8443.
Both are reachable by using any modern web browser.

- [Video: Usage](https://www.youtube.com/watch?v=nZoH-ngyu9E)

```bash
systemctl restart nginx
systemctl restart daas
systemctl restart frontend
```

## Acknowledgments

This work was funded by the Federal Ministry
for Economic Affairs and Climate Action
("Bundesministerium für Wirtschaft und Klimaschutz")
in the framework of the central innovation programme
for small and medium-sized enterprises ("Zentrales
Innovationsprogramm Mittelstand (ZIM)").

## Resources

- [Video: Installation](https://www.youtube.com/watch?v=-AUCHX9SRKE)
- [Video: Usage](https://www.youtube.com/watch?v=nZoH-ngyu9E)
- [Paper: Open Journal of Cloud Computing (OJCC)](https://www.ronpub.com/ojcc/OJCC_2023v8i1n01_Baun.html)
- [Paper: MobileWeb and Intelligent Information Systems (MobiWIS 2024)](https://link.springer.com/chapter/10.1007/978-3-031-68005-2_1)
- [Repo: Frontend](https://github.com/nuromedia/design-daas-application-frontend)
- [Repo: Backend](https://github.com/nuromedia/design-daas-application-backend)
