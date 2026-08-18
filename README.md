# energy\_grouping



## Overview

This repository contains the implementation and supporting code for my bachelor's thesis.



## Requirements

* Windows (not yet tested on Linux)
* Python 3.11.2
* pip
* Git

**optional:**
* draw.io

## Setup

Run the following commands in Command Prompt (CMD):

```cmd
git clone git@github.com:StevenLhmn/energy_grouping.git

cd energy_grouping

python -m venv .venv

.venv\Scripts\activate     # Windows

pip install -r req.txt
```

## Git Strategy

- `main`: Stable versions of the project. All test have to work.
- `dev`: Development branch for new features and changes.

Development is done on `dev` and merged into `main` when no bugs occur and no test fails. It doesnt need to have all final functionality but it may not have known bugs.
