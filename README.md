# pgz

A Python implementation of Git internals for educational and experimental purposes. This library provides low-level Git object manipulation and commands, allowing you to understand how Git works under the hood.

## Features

- **init** - Initialize a new Git repository
- **hash-object** - Compute object ID and optionally create a blob from a file
- **cat-file** - Provide content or type and size information for repository objects
- **log** - Show commit logs
- **tag** - Create, list, or delete tags
- **update-ref** - Update the object name stored in a ref safely
- **symbolic-ref** - Read, modify, and delete symbolic refs

## Requirements

- Python 3.11 or higher

## Installation

```bash
pip install pgz
```

Or install from source using Poetry:

```bash
git clone https://github.com/conao3/python-pgz.git
cd python-pgz
poetry install
```

## Usage

After installation, the `pgz` command will be available:

```bash
# Initialize a new repository
pgz init

# Hash a file and store it as a blob object
pgz hash-object -w myfile.txt

# Display contents of an object
pgz cat-file -p <sha>

# View commit history
pgz log

# Create a tag
pgz tag v1.0.0 <sha>

# Update a reference
pgz update-ref refs/heads/main <sha>

# Read or modify symbolic refs
pgz symbolic-ref HEAD refs/heads/main
```

## How It Works

pgz implements Git's core object model:

- **Blob** - Stores file contents
- **Tree** - Represents a directory listing
- **Commit** - Points to a tree and contains metadata
- **Tag** - Named reference to another object

Objects are stored in `.git/objects` using zlib compression with SHA-1 hashing, exactly as Git does.

## License

Apache-2.0
