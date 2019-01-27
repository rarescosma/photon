## Photon

Dead-simple tool for matching photos by name and hash.

It:

* globs the from- and to- paths
* matches files first by name, then by their MD5 hash
* prints out all matching pairs

### Sample usage

Find backlog photos that are already organized in an album:

```
photon ~/Photos/Backlog ~/Photos/Albums | cut -f1
```

### Installing

Install [pyenv](https://github.com/pyenv/pyenv#installation) and Python 3.7.2:

```
pyenv install 3.7.2
```

Generate a one-file PyInstaller executable and copy it to `${HOME}/bin`:

```
make && make install
```
