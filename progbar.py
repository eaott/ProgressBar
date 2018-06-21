# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import six
import sys
import time

# @eaott: See git commit history for how this has been modified
# from the original Edward version.

class Progbar(object):
  def __init__(self, target, width=30, interval=0.01, avg=False):
    """(Yet another) progress bar.

    Args:
      target: int.
        Total number of steps expected.
      width: int.
        Width of progress bar.
      interval: float.
        Minimum time (in seconds) for progress bar to be displayed
        during updates.
      avg: boolean.
        Whether to report the average or current value of any values
        applied in the update step.
    """
    self.target = target
    self.width = width
    self.interval = interval

    self.stored_values = {}
    self.start = time.time()
    self.last_update = 0
    self.total_width = 0
    self.seen_so_far = 0
    self.avg = avg

  def update(self, current=None, values=None, force=False):
    """Update progress bar, and print to standard output if `force`
    is True, or the last update was completed longer than `interval`
    amount of time ago, or `current` >= `target`.

    The written output is the progress bar and all unique values.

    Modified by @eaott to not require a current value.

    Args:
      current: int or None.
        Index of current step. If None, will update to next integer.
      values: dict of str to float.
        Dict of name by value-for-last-step. The progress bar
        will display averages or current value for these values (based on
        avg parameter in the constructor).
      force: bool.
        Whether to force visual progress update.
    """
    if values is None:
      values = {}

    # Modified section
    if current is not None:
      self.seen_so_far = current
    else:
      self.seen_so_far += 1
      current = self.seen_so_far

    if self.avg:
      for k, v in six.iteritems(values):
        if k not in self.stored_values:
          self.stored_values[k] = 0
        self.stored_values[k] += v
    else:
      for k, v in six.iteritems(values):
        self.stored_values[k] = v


    now = time.time()
    if (not force and
            (now - self.last_update) < self.interval and
            current < self.target):
      return

    self.last_update = now

    prev_total_width = self.total_width
    sys.stdout.write("\b" * prev_total_width)
    sys.stdout.write("\r")

    # Write progress bar to stdout.
    n_digits = len(str(self.target))
    bar = '%%%dd/%%%dd' % (n_digits, n_digits) % (current, self.target)
    bar += ' [{0}%]'.format(str(int(current / self.target * 100)).rjust(3))
    bar += ' '
    len_counter = len(bar)
    prog_width = int(self.width * float(current) / self.target)
    if prog_width > 0:
      try:
        # This unicode symbol registers as more than one character,
        # so the length can't be trusted here.
        bar += ('█' * prog_width)
      except UnicodeEncodeError:
        bar += ('*' * prog_width)
    bar += (' ' * (self.width - prog_width))
    sys.stdout.write(bar)

    # Write values to stdout.
    if current:
      time_per_unit = (now - self.start) / current
    else:
      time_per_unit = 0

    eta = time_per_unit * (self.target - current)
    info = ''
    if current < self.target:
      info += ' ETA: %ds' % eta
    else:
      info += ' Elapsed: %ds' % (now - self.start)
    for k, v in six.iteritems(self.stored_values):
      if self.avg:
        v = v / current
      info += ' | {0:s}: {1:0.3f}'.format(k, v)

    self.total_width = len_counter + self.width + len(info)
    if prev_total_width > self.total_width:
      # print("entered condition")
      info += ((prev_total_width - self.total_width) * " ")
    self.total_width = len_counter + self.width + len(info)
    sys.stdout.write(info)
    sys.stdout.flush()
    if current >= self.target:
      sys.stdout.write("\n")
