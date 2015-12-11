## Changelog ##
### 0.1.5 ###
  * cg2dot: [issue #15](https://code.google.com/p/xdebugtoolkit/issues/detail?id=#15): root node now can just have arbitrary number of subcalls, we dont make any suppositions (that are wrong in some cases) about their number any more.
  * cg2dot: [issue #12](https://code.google.com/p/xdebugtoolkit/issues/detail?id=#12): -i/--ignore option.
  * cg2dot: optimized filter\_inclusive\_time a bit, using thresholds inclusively.
  * cg2dot: better error handling, introducing CgParseError.
  * added shebang lines.
  * svn: fixed script eol styles and executable flags.
  * removed unnecessary error masking.

### 0.1.4 ###
  * added a new xdot-pygoocanvas.py utility which works more rapidly than the original xdot

### 0.1.3 ###
  * cg2dot: [issue #11](https://code.google.com/p/xdebugtoolkit/issues/detail?id=#11): Change edge style
  * cg2dot: minor improvements in the command line usage
  * cg2dot: root node is now called root instead of -1
  * added cg2ubigraph: [issue #10](https://code.google.com/p/xdebugtoolkit/issues/detail?id=#10): Add ubigraph visualization for fun

### 0.1.2 ###
  * cg2dot: minor colorizing issue in the --aggregate=none mode
  * cg2dot: [issue #8](https://code.google.com/p/xdebugtoolkit/issues/detail?id=#8): Crash on shutdown functions
  * added a new cgsplit utility

### 0.1.1 ###
  * cg2dot: [issue #7](https://code.google.com/p/xdebugtoolkit/issues/detail?id=#7): Make aggregation optional

### 0.1.0 ###
> initial release