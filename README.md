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

- `main`: Stable versions of the project. All tests are written and have to work, the documentation is present and conventions are complied with
- `dev`: Development branch for new features and changes, code can stil be messy

Development is done on `dev` and merged into `main` when no bugs occur and no test fails. It doesnt need to have all final functionality but it may not have known bugs.

## Documentation

Every class and every method should have a description of its purpose/usage.
And every function should have a describtion of its parameters and their constrains as well as the return value and its content.

## Testing 
at least one test per method. a test of how the method should work. (Positive)
Things to consider testing, every parameter different. not none, correct type, Violation of its constrains. And extreme cases. (Negative)

## Convention
private functions below public ones

#### class and function namings
idk yet