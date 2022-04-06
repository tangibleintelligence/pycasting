# PyCasting

Python-based financial forecasting for startups.

# Setting up

Project uses `poetry`, so set up like a standard poetry project.

# Future features

In spreadsheet:

- Compare to actual

Not in spreadsheet:

- error bars on customer lead duration
- Better simulation of marketing/sales interaction. current pattern is simplistic.
  - spreadsheet just assumed constant monthly marketing budget
  - I'm assuming cost per ad click & (constant ad -> qualified lead ratio) (so scales with leads but doesn't reflect better ads,
    or outbound leads)
  - would like to simulate customer acquisition as a graph, not a list. coming in
    through ads, relationships, and outbound based on site visits etc.