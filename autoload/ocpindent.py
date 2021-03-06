import os
import sys
import vim
import time
import subprocess

ocp_indent_path = "ocp-indent"
ocp_lastline = None
ocp_lasttime = None
ocp_linefst = 0
ocp_linebuf = []
ocp_inarow = 0

def ocp_indent(lines):
  if lines:
    if type(lines) == int:
      end = lines
      lines = "%d-%d" % (lines,lines)
    else:
      end = lines[1]
      lines = "%d-%d" % lines
  content = "\n".join(vim.current.buffer[:end] + ["X"])
  process = subprocess.Popen(
      [ocp_indent_path,"--lines",lines,"--numeric"],
      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  process.stdin.write(content)
  process.stdin.close()
  return map(int,process.stdout.readlines())

def vim_indentline():
  global ocp_lastline, ocp_lasttime, ocp_linefst, ocp_linebuf, ocp_inarow
  line = int(vim.eval("v:lnum"))
  if ocp_lastline == line - 1 and abs(time.time() - ocp_lasttime) < 0.1:
    # Possibly a selection indentation, use a threshold to detect consecutive calls
    if ocp_inarow > 2:
      if not (line >= ocp_linefst and line < ocp_linefst + len(ocp_linebuf)):
        ocp_linefst = line
        ocp_linebuf = ocp_indent((line, min(line + 1000, len(vim.current.buffer))))
      ocp_lasttime = time.time()
      ocp_lastline = line
      return ocp_linebuf[line - ocp_linefst]
    else:
      # Increment counter
      ocp_inarow += 1
  else:
    # Not a selection indentation
    ocp_inarow = 0

  # Current line indentation
  ocp_linebuf = []
  indent = ocp_indent(line)
  indent = indent.pop()
  ocp_lasttime = time.time()
  ocp_lastline = line
  return indent

def vim_equal():
  r = vim.current.range
  w = vim.current.window
  pos = w.cursor
  vim.command("0,'>!%s --lines %d-" % (ocp_indent_path, r.start+1))
  w.cursor = pos
