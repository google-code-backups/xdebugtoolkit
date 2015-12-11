## Usage ##

```
$ ./cgsplit.py --help
Usage: cgsplit.py file [file ...]

Options:
  -h, --help  show this help message and exit
```

## Example ##
```
cgsplit fixtures/tth.cg; cg2dot tth.*.cg | xdot -
```

## Details ##

When you use xdebug extension with [xdebug.profiler\_append](http://www.xdebug.org/docs/profiler#profiler_append) option enabled, xdebug produces files that can not be currently handled directly by the cg2dot.py tool.

In order to use the cg2dot, you have to split such appended files using the cgsplit.py tool.

It will split the files into enumerated ones like file.0.cg, file.1.cg, etc placed in the current working directory.