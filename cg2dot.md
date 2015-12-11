## Introduction ##
The cg2dot utility is a converter from [Xdebug cachegrind](http://www.xdebug.org/docs/profiler) files to the [dot format](http://www.graphviz.org/).

The most handy dot viewer is José Fonseca's [xdot](http://code.google.com/p/jrfonseca/wiki/XDot) utility.

If you work with large .dot files you may want to use a xdot-pygoocanvas tool provided along with the xdebugtoolkit. It's based on the xdot but the engine is re-written for using pygoocanvas which allows xdot work much faster. For this you'll need to install python-pygoocanvas package (sudo aptitude install python-pygoocanvas) in addition to regular xdot [requirements](http://code.google.com/p/jrfonseca/wiki/XDot#Requirements).

One of the main advantages over other programs like KCacheGrind and WebGrind is the way cg2dot aggregates calls. It makes call graphs very compact preserving their tree structure, so these graphs stay very clear. For example [this PHP code](http://code.google.com/p/xdebugtoolkit/source/browse/trunk/xdebugtoolkit/fixtures/2.php?r=92) being aggregated produces the following tree:

![http://xdebugtoolkit.googlecode.com/svn/wiki/aggregate_demo.png](http://xdebugtoolkit.googlecode.com/svn/wiki/aggregate_demo.png)

Check the details section below for more info.

## Usage ##
```
$ cg2dot --help
Usage: cg2dot [options] file [file ...]

Options:
  -h, --help            show this help message and exit
  -i, --ignore          Ignore files that can't be parsed.
  -t PERCENT, --threshold=PERCENT
                        remove fast tails that took less then PERCENT of total
                        execution time. Default is 1%.
  -a MODE, --aggregate=MODE
                        aggregation mode. MODE can have values "none" and
                        "func-file". The "none" means that aggregation will be
                        completely off. This is usually very memory wasting,
                        so use it very carefully especially with the xdot. The
                        "func-file" mode means that each call will be keyed by
                        (mapped to) file and function names of every call from
                        it's stack. Then all calls will be aggregated
                        (reduced) according to these keys. Default is "func-
                        file".
```

## Examples ##
render as png:
```
cg2dot some.cg | path_to_dot/dot -Tpng -osome.png
```

view in xdot:
```
cg2dot some.cg | xdot -
```

view in xdot-pygocanvas:
```
cg2dot some.cg | xdot-pygoocanvas -
```

## Screenshots ##
[Screenshots](Screenshots.md)

## Details ##

### Aggregation ###
The 'none' mode doesn't merge calls at all. It's the most detailed view of the profile.

The 'func-file' mode produces much more compact trees. If you look at the example tree above you will find that there are still few calls of the d() function not aggregated with each other. This is because these calls have diffent call stacks:
  * `root -> {main} -> a -> c -> d`
  * `root -> {main} -> b -> c -> d`
  * `root -> b -> c -> d`

You don't want your graphs look like [these](http://pycallgraph.slowchop.com/pycallgraph), do you? :)

### Labels ###
`4x[1ms..24ms] = 53ms` means the following:

  * the aggregated call aggregates 4 single calls
  * minimal single call's time is 1ms
  * maximum single call's time is 24ms
  * total time of the 4 calls is 53ms.
  * average call time is 53ms/4 = 13.25ms

<font color='#999999'> NB: You can meet labels like <code>1000x[0ms..0ms] = 10ms</code>. This can happen due to rounding to integer milliseconds and actually mean something like <code>1000x[0.005ms..0.015ms] = 10ms</code></font>

### Node colorizing ###
<font color='#CCCCCC'>██</font> Nodes colored with shades near to gray are fast and rarely called. There is usually nothing interesting.

<font color='#CCCC00'>██</font> Grade of yellow means call count of an aggregated call. If you use --aggregate=none all calls are considered single therefore have zero yellow grade.

<font color='#CC00CC'>██</font> Grade of magenta expresses call's self time.

<font color='#CC0000'>██</font> If some node were called often and took a lot of time, it will have both yellow and magenta colors mixed so it will be colored near-red. Red calls are usually the bottlenecks you should optimize first.

### Edges ###
Edges vary in their width due to their inclusive time. Most thick edges are at the top of the tree. Getting deeper they split into few thiner edges and also lose weight for nodes' self time. This allows you to easily track critical paths leading to most expensive operations.

### Performance ###
cg2dot processes (lexer + tree builder + tree aggregator + dot generator) about 1.6mb of raw cg per second on Core™2 Duo P7350 2.0GHz.
Lexer takes about half of this time.